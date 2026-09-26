#!/usr/bin/env python3
"""
Reads the latest translated Excel file.
Finds buyer rows (based on semantic category or intent).
Rotates between configured Telegram accounts (round-robin) to send messages,
and uses OpenRouter (Tencent Hy3) to generate a personalized 2-3 line response
for each buyer based on their specific message.
"""

import asyncio
import sys
import glob
import os
import random
import time
import requests
import pandas as pd
from config import config
from telethon import TelegramClient
from telethon.errors import FloodWaitError

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

API_KEY = getattr(config, 'OPENROUTER_API_KEY', '')
MODEL = "tencent/hy3:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

def generate_ai_reply(buyer_message: str) -> str:
    """
    Queries OpenRouter to generate a personalized 2-3 line reply to the buyer.
    """
    if not API_KEY:
        print("  Warning: No OpenRouter API key found. Using default template.")
        return getattr(config, 'BUYER_MESSAGE_TEMPLATE', "Hello, I saw your post. Let me know if you still need help!")
        
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    
    prompt = (
        "You are a helpful, professional business assistant drafting a direct message to a potential client on Telegram.\n"
        f"The client posted this message in a group:\n\"{buyer_message}\"\n\n"
        "Draft a polite, personalized, and professional 2-3 line direct message offering matching services/products.\n"
        "Ask them to reply to this DM if they are interested.\n"
        "IMPORTANT: Do not include any quotes, placeholders (like [My Name]), brackets, or explanations. "
        "Return ONLY the exact text of the message to be sent directly."
    )
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        res_json = response.json()
        reply = res_json['choices'][0]['message']['content'].strip()
        # Clean quotes
        if reply.startswith('"') and reply.endswith('"'):
            reply = reply[1:-1].strip()
        return reply
    except Exception as e:
        print(f"  Error generating AI reply: {e}. Using default template.")
        return getattr(config, 'BUYER_MESSAGE_TEMPLATE', "Hello, I saw your post. Let me know if you still need help!")

async def main():
    # Find latest translated file
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    files = glob.glob(os.path.join(output_dir, "*_translated.xlsx"))
    if not files:
        print("No translated Excel files found in output directory.")
        return
        
    latest_file = max(files, key=os.path.getmtime)
    print(f"Reading translated file: {os.path.basename(latest_file)}")
    
    try:
        df = pd.read_excel(latest_file, engine='openpyxl')
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return
        
    if "Author ID" not in df.columns or "Final Semantic Category" not in df.columns or "Message ID" not in df.columns:
        print("Required columns (Author ID, Message ID, Final Semantic Category) not found.")
        return
        
    # Add Messaged tracking column if not exists
    if "Messaged" not in df.columns:
        df["Messaged"] = "No"
        
    # Get rotation accounts list
    accounts = getattr(config, 'ACCOUNTS', [])
    if not accounts:
        # Fallback to primary account
        accounts = [{
            "API_ID": config.API_ID,
            "API_HASH": config.API_HASH,
            "PHONE": config.PHONE,
            "SESSION": config.USERNAME or "session"
        }]
        
    print(f"Loaded {len(accounts)} accounts for round-robin rotation.")
    
    # Configure buyer category filters
    buyer_filters = [c.lower().strip() for c in getattr(config, 'BUYER_CATEGORIES', [])]
    total_rows = len(df)
    messages_sent_count = 0
    account_index = 0
    
    try:
        for idx, row in df.iterrows():
            author_id_val = row["Author ID"]
            msg_id_val = row["Message ID"]
            group_val = row.get("Group", "")
            content_val = str(row.get("Content", ""))
            category = str(row["Final Semantic Category"]).lower().strip()
            intent = str(row.get("Primary Intent", "")).lower().strip()
            
            # Check if this row matches buyer definitions
            is_buyer = any(bf in category for bf in buyer_filters) or intent == "buying"
            
            if not is_buyer:
                continue
                
            # Check if already messaged
            if str(row["Messaged"]).strip().lower().startswith("yes") or str(row["Messaged"]).strip().lower() == "yes":
                print(f"[{idx+1}/{total_rows}] User {author_id_val} already messaged. Skipping.")
                continue
                
            try:
                target_id = int(author_id_val)
                message_id = int(msg_id_val)
                target_group = str(group_val)
            except (ValueError, TypeError):
                continue
                
            # Get the next account in the rotation
            acc = accounts[account_index % len(accounts)]
            account_index += 1
            
            print(f"\n[{idx+1}/{total_rows}] Match Found! Sender: {target_id}")
            print(f"  Using Account: {acc['PHONE']} ({acc['SESSION']})")
            
            # Generate AI Reply
            print("  Generating personalized AI response...")
            custom_reply = generate_ai_reply(content_val)
            print(f"  AI Reply:\n  \"\"\"\n  {custom_reply}\n  \"\"\"")
            
            # Message Sending Logic
            client = None
            try:
                client = TelegramClient(
                    acc["SESSION"],
                    acc["API_ID"],
                    acc["API_HASH"]
                )
                
                await client.start(phone=acc["PHONE"])
                
                # Fetch message first to cache entity
                if target_group and message_id:
                    try:
                        await client.get_messages(target_group, ids=message_id)
                    except Exception:
                        pass
                
                # Send PM
                await client.send_message(target_id, custom_reply)
                
                # Record success with sender info
                df.at[idx, "Messaged"] = f"Yes (via {acc['PHONE']})"
                messages_sent_count += 1
                print(f"  ✓ Personal Message successfully sent from {acc['PHONE']} to {target_id}!")
                
                # Random safety delay (1 to 2.5 minutes) between successful messages
                wait_time = random.randint(60, 150)
                print(f"  Waiting {wait_time} seconds before checking next row (safe bot bypass)...")
                await asyncio.sleep(wait_time)
                
            except FloodWaitError as fe:
                print(f"  ⚠ Account {acc['PHONE']} rate limited (FloodWait). Need to sleep for {fe.seconds} seconds.")
                df.at[idx, "Messaged"] = f"Failed (FloodWait on {acc['PHONE']})"
                await asyncio.sleep(fe.seconds)
            except Exception as e:
                print(f"  ✗ Failed to send message from {acc['PHONE']} to {target_id}: {e}")
                df.at[idx, "Messaged"] = f"Failed: {e}"
            finally:
                if client:
                    await client.disconnect()
                    
    except KeyboardInterrupt:
        print("\n⚠ Stopped by user. Saving message status...")
    finally:
        # Save file with updated message status
        try:
            df.to_excel(latest_file, index=False, engine='openpyxl')
            print(f"\n✓ Processed. Messaged status saved to: {os.path.basename(latest_file)}")
        except Exception as e:
            print(f"Error saving file: {e}")
            
        print(f"Process ended. Sent {messages_sent_count} messages in this run.")

if __name__ == "__main__":
    asyncio.run(main())
