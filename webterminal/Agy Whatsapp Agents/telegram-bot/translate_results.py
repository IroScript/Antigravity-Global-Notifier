#!/usr/bin/env python3
"""
Translates and dynamically categorizes the 'Content' column of the latest generated Excel file
in the output folder.
Uses the OpenRouter API (Tencent: Hy3) for both translation (English & Bengali) and 
independent 5-layer semantic message reasoning.
"""

import os
import sys
import glob
import json
import requests
import pandas as pd

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def load_api_key():
    # Try importing from config.py first
    try:
        from config import config
        if hasattr(config, 'OPENROUTER_API_KEY') and config.OPENROUTER_API_KEY:
            return config.OPENROUTER_API_KEY
    except Exception:
        pass

    if "OPENROUTER_API_KEY" in os.environ:
        return os.environ["OPENROUTER_API_KEY"]
    
    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "openRouterAPIKey.txt")
    if os.path.exists(key_path):
        try:
            with open(key_path, "r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped.startswith("sk-or-v1-"):
                        return stripped
        except Exception:
            pass
    return ""

API_KEY = load_api_key()
MODEL = "tencent/hy3:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

SEMANTIC_SYSTEM_PROMPT = """# ROLE
You are an Independent Semantic Message Reasoning Engine.

Your purpose is NOT to classify messages into a predefined list.
Your purpose is to understand a single message as deeply and objectively as possible, then generate the most accurate semantic category.

Every message MUST be treated as a completely independent case.
Never inherit knowledge from previous messages.
Never assume hidden conversation context.
Never assume sender identity.
Never assume the sender is the same person as before.
Never assume previous roles.
Never assume previous intentions.
Never use conversation history.
Never use statistical expectations.
Never use stereotypes.
Never use probability alone.
Never use common patterns unless supported by evidence inside THIS message.
Completely rebuild your understanding from zero for EVERY message.
The message itself is your ONLY source of truth.

------------------------------------------------------------
# FIVE-LAYER REASONING

LAYER 1: Semantic Understanding
Understand what the message literally says. Extract meaning, purpose, request, action, emotion, certainty. Separate facts from assumptions. Do NOT infer unnecessary info.

LAYER 2: Intent Reasoning
Determine the PRIMARY intent (e.g. Buying, Selling, Offering, Looking For, Searching, etc. Create new intents as needed).

LAYER 3: Actor & Object Reasoning
Determine WHO the sender appears to be (e.g. Buyer, Seller, Recruiter, Community Member, unknown) and WHAT the message is about (e.g. Google Voice, Account, Job, Software, unknown).

LAYER 4: Evidence & Attribute Reasoning
Extract every meaningful attribute (e.g. Urgent, Bulk, Cheap, Verified, Chinese, English, negotiating, fixed price). For every conclusion, verify supporting evidence.

LAYER 5: Dynamic Category Generation
Generate the MOST SPECIFIC category possible by combining Intent, Actor, Object, Attributes, Transaction Stage.

------------------------------------------------------------
# OUTPUT FORMAT
You must respond strictly in this format:

Primary Intent: <value>
Actor: <value>
Object: <value>
Attributes: <value>
Evidence: <value>
Confidence: <value>
Final Semantic Category: <value>
Reasoning Summary: <value>
"""

def translate_text(text: str, target_lang: str) -> str:
    if not text or not str(text).strip():
        return ""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    
    prompt = (
        f"Translate the following Telegram message into {target_lang}.\n"
        "Return ONLY the translated text. Do not add any explanation, quotes, or introduction.\n\n"
        f"Message:\n{text}"
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
        translated = res_json['choices'][0]['message']['content'].strip()
        if translated.startswith('"') and translated.endswith('"'):
            translated = translated[1:-1].strip()
        if translated.startswith("'") and translated.endswith("'"):
            translated = translated[1:-1].strip()
        return translated
    except Exception as e:
        print(f"  Error translating '{str(text)[:20]}...' to {target_lang}: {e}")
        return f"Translation Error: {e}"

def generate_semantic_reasoning(text: str) -> dict:
    fields = {
        "Primary Intent": "unknown",
        "Actor": "unknown",
        "Object": "unknown",
        "Attributes": "none",
        "Evidence": "none",
        "Confidence": "low",
        "Final Semantic Category": "General Message",
        "Reasoning Summary": "none"
    }
    
    if not text or not str(text).strip():
        return fields
        
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SEMANTIC_SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyze the following message:\n{text}"}
        ]
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        res_json = response.json()
        output_text = res_json['choices'][0]['message']['content'].strip()
        
        # Parse the structured keys
        current_key = None
        for line in output_text.splitlines():
            line_str = line.strip()
            matched = False
            for key in fields.keys():
                if line_str.lower().startswith(key.lower() + ":"):
                    current_key = key
                    val = line_str[len(key) + 1:].strip()
                    fields[key] = val
                    matched = True
                    break
            if not matched and current_key and line_str:
                fields[current_key] += " " + line_str
                
        # Clean up values
        for key in fields:
            fields[key] = fields[key].strip()
            
    except Exception as e:
        print(f"  Error generating semantic analysis for '{str(text)[:20]}...': {e}")
        fields["Reasoning Summary"] = f"API Error: {e}"
        
    return fields

def main():
    if not API_KEY:
        print("Error: OpenRouter API key is missing. Please place it in openRouterAPIKey.txt")
        return
        
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    xlsx_files = glob.glob(os.path.join(output_dir, "*.xlsx"))
    xlsx_files = [f for f in xlsx_files if "_translated" not in f]
    
    if not xlsx_files:
        print("No Excel files found in the output directory.")
        return
    
    latest_file = max(xlsx_files, key=os.path.getmtime)
    print(f"Latest file found: {os.path.basename(latest_file)}")
    
    try:
        df = pd.read_excel(latest_file, engine='openpyxl')
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return
        
    if 'Content' not in df.columns:
        print("Error: 'Content' column not found in the Excel file.")
        return
        
    total_rows = len(df)
    print(f"Starting translation and semantic reasoning for {total_rows} rows...")
    
    bangla_translations = []
    english_translations = []
    
    # Semantic reasoning data structures
    semantic_data = {
        "Primary Intent": [],
        "Actor": [],
        "Object": [],
        "Attributes": [],
        "Evidence": [],
        "Confidence": [],
        "Final Semantic Category": [],
        "Reasoning Summary": []
    }
    
    for idx, row in df.iterrows():
        content = str(row['Content'])
        print(f"\n[{idx+1}/{total_rows}] Processing: {content[:50]}...")
        
        # 1. Translation
        print("  - Translating...")
        bn_trans = translate_text(content, "Bengali")
        bangla_translations.append(bn_trans)
        
        en_trans = translate_text(content, "English")
        english_translations.append(en_trans)
        
        # 2. Semantic reasoning
        print("  - Analyzing semantics (5-layer reasoning)...")
        analysis = generate_semantic_reasoning(content)
        for key in semantic_data:
            semantic_data[key].append(analysis[key])
            
    # Add translation columns
    df['Content_Bengali'] = bangla_translations
    df['Content_English'] = english_translations
    
    # Add semantic reasoning columns
    for key in semantic_data:
        df[key] = semantic_data[key]
        
    # Save translated and categorized file
    file_dir, file_name = os.path.split(latest_file)
    name, ext = os.path.splitext(file_name)
    new_filename = f"{name}_translated{ext}"
    new_filepath = os.path.join(file_dir, new_filename)
    
    try:
        df.to_excel(new_filepath, index=False, engine='openpyxl')
        print(f"\n✓ Processing complete! Saved to:\n{new_filepath}")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    main()
