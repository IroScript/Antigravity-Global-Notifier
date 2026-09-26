#!/usr/bin/env python3
"""
Universal Buyer Discovery Engine (UBDE) - Main Scraper
High-Speed End-to-End Pipeline:
1. Cold-Probe Group Profiling (Language, Domain, Slang) in <1s
2. LLM-Synthesized Multi-Token Server Ingestion (Zero-Waste, Rate-Limit Safe)
3. 5-Layer Parallel Batch Semantic Reasoning (What They Want + Intent Extraction)
4. Author ID Deduplication & Rich Excel Export
"""

import asyncio
import argparse
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd
from telethon import TelegramClient
from telethon.errors import FloodWaitError

from config import config
from group_profiler import get_group_profile
from semantic_engine import analyze_all_candidates_parallel

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Bangladesh Local Time (UTC+6)
DHAKA_TZ = timezone(timedelta(hours=6))

class UniversalBuyerScraper:
    def __init__(self, channels: List[str] = None, date_min: datetime = None, date_max: datetime = None, max_messages: int = 50000):
        self.channels = channels or config.CHANNELS or ["@GV1212"]
        self.date_max = date_max or datetime.now(timezone.utc)
        self.date_min = date_min or (self.date_max - timedelta(days=3))
        self.max_messages = max_messages
        
        self.output_dir = Path(getattr(config, 'OUTPUT_DIR', './output'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = None

    async def connect(self):
        """Initializes and connects Telethon client."""
        self.client = TelegramClient(
            config.USERNAME or "session",
            config.API_ID,
            config.API_HASH
        )
        await self.client.connect()
        print("✓ Connected to Telegram MTProto Gateway", flush=True)

    async def disconnect(self):
        """Disconnects Telethon client."""
        if self.client:
            await self.client.disconnect()
            print("✓ Disconnected from Telegram", flush=True)

    async def run_discovery_for_channel(self, channel: str) -> Path:
        """Executes full Universal Buyer Discovery pipeline for a single channel."""
        print(f"\n{'='*70}", flush=True)
        print(f"🚀 STARTING UNIVERSAL BUYER DISCOVERY FOR: {channel}", flush=True)
        print(f"📅 Date Range (UTC): {self.date_min.strftime('%Y-%m-%d %H:%M')} to {self.date_max.strftime('%Y-%m-%d %H:%M')}", flush=True)
        print(f"{'='*70}", flush=True)

        # PHASE 1: Group Cold-Probe Profiling
        profile = await get_group_profile(self.client, channel)
        tokens = profile.get("target_buyer_tokens", ["wtb", "need", "收", "求", "লাগবে"])
        
        # PHASE 2: Targeted Server-Side Ingestion
        print(f"\n⚡ INGESTION PHASE: Querying Telegram server across {len(tokens)} targeted buyer tokens...", flush=True)
        candidates_map = {} # msg_id -> message object
        consecutive_empty_tokens = 0

        for i, token in enumerate(tokens, 1):
            token_clean = token.strip()
            if not token_clean:
                continue

            print(f"  [{i}/{len(tokens)}] Searching server for token: '{token_clean}'...", end="", flush=True)
            token_matches = 0
            new_matches = 0

            try:
                async for message in self.client.iter_messages(channel, search=token_clean):
                    if not message.text:
                        continue

                    msg_date = message.date.replace(tzinfo=timezone.utc)
                    if msg_date < self.date_min:
                        break
                    if msg_date > self.date_max:
                        continue

                    token_matches += 1
                    if message.id not in candidates_map:
                        candidates_map[message.id] = message
                        new_matches += 1

                    if len(candidates_map) >= self.max_messages:
                        break

            except FloodWaitError as e:
                print(f" [FloodWait {e.seconds}s]", end="", flush=True)
                await asyncio.sleep(e.seconds + 1)
            except Exception as e:
                print(f" [Error: {e}]", end="", flush=True)

            print(f" -> Found {token_matches} (New Unique: {new_matches})", flush=True)

            # Check saturation / convergence
            if new_matches == 0:
                consecutive_empty_tokens += 1
            else:
                consecutive_empty_tokens = 0

            if consecutive_empty_tokens >= 4:
                print(f"  ✓ Search space converged! No new unique candidates found in last 4 tokens.", flush=True)
                break

            await asyncio.sleep(0.2)

        total_candidates = len(candidates_map)
        print(f"\n✓ INGESTION COMPLETE: Retrieved {total_candidates} candidate messages from {channel}", flush=True)

        if total_candidates == 0:
            print("⚠️ No candidate messages found matching time range and tokens.", flush=True)
            return None

        # PHASE 3: 5-Layer Parallel Batch Semantic Reasoning
        print(f"\n🧠 SEMANTIC ANALYSIS PHASE: Parallel AI Reasoning across all candidates...", flush=True)
        candidate_list = list(candidates_map.values())
        
        # Run parallel multi-worker reasoning
        analyzed_results = analyze_all_candidates_parallel(candidate_list, batch_size=15, max_workers=5)
        
        # Map analyses back to original messages
        analysis_by_id = {r.get('msg_id'): r for r in analyzed_results if r.get('msg_id')}
        
        all_buyer_records = []
        for msg in candidate_list:
            analysis = analysis_by_id.get(msg.id)
            if analysis and analysis.get("is_buyer", False):
                local_dt = msg.date.astimezone(DHAKA_TZ)
                
                record = {
                    "Type": "text",
                    "Group": channel,
                    "Author ID": msg.sender_id,
                    "Author": getattr(msg, 'post_author', '') or '',
                    "Date": local_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "What They Want": analysis.get("what_they_want", "Unspecified Product/Service"),
                    "Intent Category": analysis.get("intent_category", "Buyer"),
                    "Quantity / Budget": analysis.get("quantity_or_budget", "Unknown"),
                    "Confidence": analysis.get("confidence", "Medium"),
                    "Reasoning": analysis.get("reasoning_summary", ""),
                    "Content": msg.text,
                    "English Translation": analysis.get("english_translation", ""),
                    "Bengali Translation": analysis.get("bengali_translation", ""),
                    "Message ID": msg.id,
                    "Url": f"https://t.me/{channel.replace('@', '')}/{msg.id}",
                    "Classification": analysis.get("intent_category", "Buyer")
                }
                all_buyer_records.append(record)

        print(f"\n✓ REASONING COMPLETE: Confirmed {len(all_buyer_records)} genuine buyers out of {total_candidates} candidates.", flush=True)

        if not all_buyer_records:
            print("⚠️ No confirmed buyers identified in the candidate pool.", flush=True)
            return None

        # PHASE 4: Author Deduplication & Excel Export
        df = pd.DataFrame(all_buyer_records)
        df_deduped = df.drop_duplicates(subset=["Author ID"], keep="first")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_ch = channel.replace("@", "").replace("/", "_")
        filename = f"BUYERS_{clean_ch}_{timestamp}_{len(df_deduped):03d}buyers.xlsx"
        filepath = self.output_dir / filename

        df_deduped.to_excel(filepath, index=False, engine='openpyxl')

        print(f"\n{'='*70}", flush=True)
        print(f"🎉 DISCOVERY COMPLETE!", flush=True)
        print(f"  • Total Candidates Scanned: {total_candidates}", flush=True)
        print(f"  • Total Buyer Posts: {len(df)}", flush=True)
        print(f"  • Unique Buyers (Deduplicated by Author ID): {len(df_deduped)}", flush=True)
        print(f"  • Output Saved: {filepath}", flush=True)
        print(f"{'='*70}\n", flush=True)

        # Display Top Identified Buyer Demands
        print("📋 TOP IDENTIFIED BUYER DEMANDS:", flush=True)
        for idx, row in df_deduped.head(5).iterrows():
            print(f"  [{idx+1}] Author: {row['Author ID']} | Want: {row['What They Want']} | Category: {row['Intent Category']}", flush=True)
            print(f"      English: {str(row['English Translation'])[:80]}...", flush=True)
            print(f"      Bengali: {str(row['Bengali Translation'])[:80]}...", flush=True)

        return filepath

async def main():
    parser = argparse.ArgumentParser(description="Universal Telegram Buyer Discovery Engine")
    parser.add_argument("--channel", type=str, default="", help="Telegram channel/group (e.g. @GV1212)")
    parser.add_argument("--days", type=int, default=1, help="Days to look back (default: 1)")
    parser.add_argument("--max-messages", type=int, default=50000, help="Max candidates limit")
    args = parser.parse_args()

    channels = [args.channel] if args.channel else config.CHANNELS or ["@GV1212"]
    now = datetime.now(timezone.utc)
    date_min = now - timedelta(days=args.days)

    scraper = UniversalBuyerScraper(
        channels=channels,
        date_min=date_min,
        date_max=now,
        max_messages=args.max_messages
    )

    await scraper.connect()
    try:
        for ch in channels:
            await scraper.run_discovery_for_channel(ch)
    finally:
        await scraper.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
