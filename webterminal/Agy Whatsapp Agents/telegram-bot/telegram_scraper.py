#!/usr/bin/env python3
"""
Telegram Scraper - Standalone Python Script
Scrapes messages from Telegram channels/groups using Telethon
Exports to Excel (.xlsx) or Parquet (.parquet)
Supports date filtering, keyword search, and seller/buyer keyword filtering
"""

import asyncio
import argparse
import json
import random
import re
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Optional

import pandas as pd
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError, ChannelPrivateError, UserNotParticipantError



def check_credentials_and_open_drive():
    """
    Checks if config.py exists and contains valid credentials.
    If not, opens the Google Drive link for downloading config.py,
    creates a config.py template from config_example.py (if missing),
    and exits the program with instructions.
    """
    import os
    import sys
    import shutil
    import webbrowser
    from pathlib import Path

    drive_url = "https://drive.google.com/drive/folders/1VyiMKjcjf7ohEF5tpO2CW6tY9jt-T5FF?usp=sharing"
    base_dir = Path(__file__).parent.resolve()
    config_path = base_dir / "config.py"
    example_path = base_dir / "config_example.py"

    has_errors = False

    # 1. Check if config.py exists
    if not config_path.exists():
        print("\n" + "="*80)
        print(" [WARNING] config.py file is missing!")
        print(" Please download your config.py credentials file from Google Drive:")
        print(f" {drive_url}")
        print(" and place it in the project root folder.")
        print("="*80 + "\n")

        # Create a default template config.py if example exists
        if example_path.exists():
            try:
                shutil.copy(example_path, config_path)
                print(f"Created a template config.py from config_example.py.")
            except Exception as e:
                print(f"Could not create template config.py: {e}")
        has_errors = True
    else:
        # 2. Check if credentials inside config.py are still default/empty
        try:
            # We must import it dynamically to avoid caching issues or syntax/import errors at the top
            sys.path.insert(0, str(base_dir))
            if "config" in sys.modules:
                del sys.modules["config"]
            import config
            conf = config.config
            if (not conf.API_ID or conf.API_ID == 0 or conf.API_ID == 12345678 or
                not conf.API_HASH or conf.API_HASH == "abcdef1234567890abcdef1234567890" or
                not conf.PHONE or conf.PHONE == "+1234567890"):
                print("\n" + "="*80)
                print(" [WARNING] config.py contains default or empty credentials!")
                print(" Please edit config.py or download the correct config.py from Google Drive:")
                print(f" {drive_url}")
                print("="*80 + "\n")
                has_errors = True
        except Exception as e:
            print(f"Error loading config.py: {e}")
            has_errors = True

    if has_errors:
        print("Opening Google Drive credentials folder in your browser...")
        try:
            webbrowser.open(drive_url)
        except Exception as e:
            print(f"Could not open browser: {e}")
        print("\nExiting program. Please configure your credentials first.")
        sys.exit(1)


# =============================================================================
# CONFIGURATION CLASS
# =============================================================================

class ScraperConfig:
    """Configuration for the scraper - set your values here or use CLI args"""

    # ---- REQUIRED: Telegram API credentials (get from https://my.telegram.org/apps) ----
    API_ID: int = 0  # e.g., 12345678
    API_HASH: str = ""  # e.g., "abcdef1234567890abcdef1234567890"
    PHONE: str = ""  # e.g., "+1234567890"
    USERNAME: str = ""  # Optional: your Telegram username (without @)
    OPENROUTER_API_KEY: str = ""  # OpenRouter API Key for translation and reasoning
    ACCOUNTS: List[dict] = []  # List of Telegram accounts for rotation

    # ---- SCRAPING PARAMETERS ----
    CHANNELS: List[str] = []  # e.g., ["@channel1", "@channel2", "https://t.me/channel3"]
    DATE_MIN: datetime = datetime(2024, 1, 1)  # Note: using naive datetime for simplicity
    DATE_MAX: datetime = datetime(2025, 12, 31)

    # Additional time filtering options
    TIME_RANGE_MODE: str = "all"  # "all", "last_hour", "specific_time"
    SPECIFIC_START_TIME: Optional[datetime] = None  # e.g., hour: 3, minute: 15
    SPECIFIC_END_TIME: Optional[datetime] = None   # e.g., hour: 3, minute: 30
    KEYWORD: str = ""  # Leave empty to scrape all messages
    MAX_MESSAGES: int = 1_000_000  # Limit per channel
    TIMEOUT_SECONDS: int = 21600  # Max 6 hours (21600 seconds)
    SCRAPE_MODE: str = "keyword"  # "keyword" or "all"
    BUYER_CATEGORIES: List[str] = ["Buyer", "Potential Buyer", "Urgent Buyer", "Bulk Buyer", "Wholesale Buyer"]
    BUYER_MESSAGE_TEMPLATE: str = "Hello, I saw your post looking for services in the group. Please let me know if you still need help!"

    # ---- OUTPUT SETTINGS ----
    OUTPUT_FORMAT: str = "excel"  # "excel" or "parquet"
    OUTPUT_DIR: str = "./output"
    FILE_PREFIX: str = "telegram_scrape"

    # ---- SELLER/BUYER KEYWORDS (for filtering) ----
    SELLER_KEYWORDS: List[str] = [
        "sell", "selling", "wts", "for sale", "stock available",
        "available", "price", "dm me", "shipment", "posting", "shipping",
        "minimum order", "moq", "bulk", "wholesale", "retail",
        "offer", "deal", "discount", "promotion"
    ]
    BUYER_KEYWORDS: List[str] = [
        "buy", "buying", "wtb", "looking for", "need", "want",
        "seeking", "searching", "interested", "inquiry", "quote",
        "pricing", "cost", "budget", "requirement", "specification"
    ]


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def remove_unsupported_characters(text: str) -> str:
    """Remove invalid XML characters from text."""
    if not text:
        return ""
    valid_xml_chars = (
        "[^\u0009\u000A\u000D\u0020-\uD7FF\uE000-\uFFFD"
        "\U00010000-\U0010FFFF"
        "]"
    )
    return re.sub(valid_xml_chars, '', text)

def format_time(seconds: float) -> str:
    """Format seconds into DD:HH:MM:SS."""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{days:02}:{hours:02}:{minutes:02}:{secs:02}"


def print_progress(
    processed: int,
    msg_date: datetime,
    date_min: datetime,
    date_max: datetime,
    start_time: float,
    max_messages: int
) -> None:
    """Print scraping progress."""
    elapsed = time.time() - start_time
    
    total_seconds = (date_max - date_min).total_seconds()
    if total_seconds > 0:
        elapsed_seconds = (date_max - msg_date).total_seconds()
        progress = max(0.0, min(1.0, elapsed_seconds / total_seconds))
        pct = progress * 100
        if progress > 0:
            est_total = elapsed / progress
            remaining = est_total - elapsed
            rem_str = format_time(remaining)
        else:
            rem_str = "00:00:00:00"
    else:
        pct = 0.0
        rem_str = "00:00:00:00"

    elapsed_str = format_time(elapsed)
    print(f"Progress: {pct:.2f}% | Elapsed: {elapsed_str} | ETA: {rem_str}")


def classify_message(text: str, seller_kw: List[str], buyer_kw: List[str]) -> str:
    """Classify message as seller, buyer, or other based on keywords."""
    if not text:
        return "other"
    text_lower = text.lower()

    seller_score = sum(1 for kw in seller_kw if kw in text_lower)
    buyer_score = sum(1 for kw in buyer_kw if kw in text_lower)

    if seller_score > buyer_score and seller_score > 0:
        return "seller"
    elif buyer_score > seller_score and buyer_score > 0:
        return "buyer"
    return "other"


async def extract_reactions(message) -> str:
    """Extract reaction emojis and counts from a message."""
    if not message.reactions:
        return ""
    parts = []
    for reaction_count in message.reactions.results:
        emoji = reaction_count.reaction.emoticon
        count = reaction_count.count
        parts.append(f"{emoji} {count}")
    return " ".join(parts)


async def scrape_comments(client, channel: str, message_id: int) -> List[dict]:
    """Scrape comments/replies for a specific message."""
    comments = []
    try:
        async for comment in client.iter_messages(channel, reply_to=message_id):
            comment_text = remove_unsupported_characters(comment.text or "")
            comment_media = 'True' if comment.media else 'False'

            reactions = await extract_reactions(comment)
            comment_date = comment.date.strftime('%Y-%m-%d %H:%M:%S')

            comments.append({
                'Type': 'comment',
                'Comment Group': channel,
                'Comment Author ID': comment.sender_id,
                'Comment Content': comment_text,
                'Comment Date': comment_date,
                'Comment Message ID': comment.id,
                'Comment Author': comment.post_author,
                'Comment Views': comment.views,
                'Comment Reactions': reactions,
                'Comment Shares': comment.forwards,
                'Comment Media': comment_media,
                'Comment Url': f'https://t.me/{channel.replace("@", "")}/{message_id}?comment={comment.id}',
            })
    except Exception as e:
        print(f"  Warning: Could not scrape comments for message {message_id}: {e}")
    return comments


# =============================================================================
# MAIN SCRAPER CLASS
# =============================================================================

class TelegramScraper:
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.client = None
        self.all_data = []
        self.total_processed = 0
        self.start_time = time.time()
        self.output_dir = Path(config.OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.stop_requested = False
        self.last_msg_date = config.DATE_MAX
        self.progress_callback = None

    async def connect(self):
        """Initialize and connect Telethon client."""
        self.client = TelegramClient(
            self.config.USERNAME or "session",
            self.config.API_ID,
            self.config.API_HASH
        )
        await self.client.start(phone=self.config.PHONE)
        print("✓ Connected to Telegram")

    async def disconnect(self):
        """Close the client connection."""
        if self.client:
            await self.client.disconnect()
            print("✓ Disconnected from Telegram")

    def _save_backup(self, channel: str, msg_id: int):
        """Save periodic backup."""
        if self.total_processed % 1000 != 0:
            return

        df = pd.DataFrame(self.all_data)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{self.config.FILE_PREFIX}_{timestamp}_ch{channel.replace('@','')}_msg{msg_id:07d}"

        if self.config.OUTPUT_FORMAT == "parquet":
            filepath = self.output_dir / f"{backup_name}.parquet"
            df.to_parquet(filepath, index=False)
        else:
            filepath = self.output_dir / f"{backup_name}.xlsx"
            df.to_excel(filepath, index=False, engine='openpyxl')

        print(f"  ✓ Backup saved: {filepath.name}")

    def _save_final(self):
        """Save final output file — deduplicated by Author ID."""
        # Define expected columns (must match record keys in scrape_channel)
        columns = ['Type', 'Group', 'Author ID', 'Content', 'Date', 'Message ID', 'Author', 'Views', 'Reactions', 'Shares', 'Media', 'Url', 'Comments List', 'Classification']

        # Build DataFrame; if no data, create empty DataFrame with columns
        df = pd.DataFrame(self.all_data, columns=columns)
        total_messages = len(df)

        # Deduplicate by Author ID — keep first (most recent) message per user
        if 'Author ID' in df.columns:
            df_deduped = df.drop_duplicates(subset='Author ID', keep='first')
        else:
            df_deduped = df

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        final_name = f"FINAL_{self.config.FILE_PREFIX}_{timestamp}_{len(df_deduped):05d}unique_buyers"

        # Always save as Excel (requirement: always produce an .xlsx file)
        filepath = self.output_dir / f"{final_name}.xlsx"
        df_deduped.to_excel(filepath, index=False, engine='openpyxl')

        print(f"\n{'='*60}")
        print(f"✓ SCRAPING COMPLETE!")
        print(f"  Total messages scanned: {total_messages:,}")
        print(f"  Unique buyers (deduplicated): {len(df_deduped):,}")
        print(f"  Duplicates removed: {total_messages - len(df_deduped):,}")
        print(f"  Saved to: {filepath}")
        print(f"{'='*60}")

        # Print summary by classification
        if getattr(self.config, 'SCRAPE_MODE', 'all') == 'keyword' and 'Classification' in df.columns:
            print("\nClassification Summary (before dedup):")
            print(df['Classification'].value_counts())

        return filepath

    async def scrape_channel(self, channel: str):
        """Scrape a single channel/group."""
        scrape_mode = getattr(self.config, 'SCRAPE_MODE', 'all')
        print(f"\n{'='*60}")
        print(f"Starting scrape: {channel}")
        print(f"Mode: {scrape_mode.upper()}")
        if scrape_mode == 'keyword' and self.config.BUYER_KEYWORDS:
            print(f"Searching for keywords: {self.config.BUYER_KEYWORDS}")
        print(f"{'='*60}")

        channel_processed = 0
        channel_scanned = 0

        try:
            async for message in self.client.iter_messages(channel, search=self.config.KEYWORD):
                channel_scanned += 1
                
                # Print status every 50 checked messages to avoid looking frozen
                if channel_scanned % 50 == 0:
                    print(f"  [Scanning...] Checked {channel_scanned} messages in {channel}... ({self.total_processed} matches found)")

                # Check user stop request
                if self.stop_requested:
                    print("Scraping stopped by user request.")
                    break

                # Check limits
                if self.total_processed >= self.config.MAX_MESSAGES:
                    print(f"Reached max messages limit ({self.config.MAX_MESSAGES:,})")
                    break

                if time.time() - self.start_time > self.config.TIMEOUT_SECONDS:
                    print(f"Reached timeout limit ({self.config.TIMEOUT_SECONDS}s)")
                    break

                # Check date range
                msg_date = message.date.replace(tzinfo=timezone.utc)
                if msg_date < self.config.DATE_MIN:
                    # Messages are returned newest first, so we can break
                    break
                if msg_date > self.config.DATE_MAX:
                    continue

                self.last_msg_date = msg_date

                # Skip empty messages
                if not message.text:
                    continue

                # Filter by keyword if in keyword mode and keywords are provided
                matched_kw = "matched"
                if scrape_mode == 'keyword' and self.config.BUYER_KEYWORDS:
                    text_lower = message.text.lower()
                    found_kw = None
                    for kw in self.config.BUYER_KEYWORDS:
                        if kw.strip() and kw.strip().lower() in text_lower:
                            found_kw = kw.strip()
                            break
                    if not found_kw:
                        continue
                    matched_kw = found_kw

                # Extract reactions
                reactions = await extract_reactions(message)

                # Scrape comments
                comments = await scrape_comments(self.client, channel, message.id)

                # Classify message
                if scrape_mode == 'keyword':
                    classification = matched_kw
                else:
                    classification = classify_message(
                        message.text,
                        self.config.SELLER_KEYWORDS,
                        self.config.BUYER_KEYWORDS
                    )

                # Convert UTC message date to Bangladesh local time (UTC+6) for display/saving
                local_tz = timezone(timedelta(hours=6))
                local_msg_date = msg_date.astimezone(local_tz)

                # Build record
                record = {
                    'Type': 'text',
                    'Group': channel,
                    'Author ID': message.sender_id,
                    'Content': remove_unsupported_characters(message.text),
                    'Date': local_msg_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'Message ID': message.id,
                    'Author': message.post_author,
                    'Views': message.views,
                    'Reactions': reactions,
                    'Shares': message.forwards,
                    'Media': 'True' if message.media else 'False',
                    'Url': f'https://t.me/{channel.replace("@", "")}/{message.id}',
                    'Comments List': remove_unsupported_characters(json.dumps(comments)),
                    'Classification': classification,
                }

                self.all_data.append(record)
                self.total_processed += 1
                channel_processed += 1

                # Random delay to mimic human activity (0.02 to 2 seconds, async-friendly)
                await asyncio.sleep(random.uniform(0.02, 2.0))

                # Progress display
                print(f"{'-'*60}")
                print_progress(
                    self.total_processed,
                    msg_date,
                    self.config.DATE_MIN,
                    self.config.DATE_MAX,
                    self.start_time,
                    self.config.MAX_MESSAGES
                )
                print(f"From {channel}: {channel_processed:05d} messages")
                print(f"ID: {message.id:05d} | Date: {record['Date']}")
                print(f"Total: {self.total_processed:05d} messages")
                if getattr(self.config, 'SCRAPE_MODE', 'all') == 'keyword':
                    print(f"Classification: {classification.upper()}")
                print(f"{'-'*60}\n")

                if self.progress_callback:
                    try:
                        self.progress_callback(channel, self.total_processed, msg_date)
                    except Exception:
                        pass

                # Periodic backup
                self._save_backup(channel, message.id)

        except ChannelPrivateError:
            print(f"✗ Error: Cannot access {channel} - private channel or not a member")
        except UserNotParticipantError:
            print(f"✗ Error: You are not a member of {channel}")
        except FloodWaitError as e:
            wait_time = e.seconds
            print(f"⚠ FloodWait: Need to wait {wait_time}s. Sleeping...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            print(f"✗ Error scraping {channel}: {type(e).__name__}: {e}")

        print(f"\n✓ Completed {channel}: {channel_processed:,} messages")

        # Save channel-specific file
        if channel_processed > 0:
            channel_data = [d for d in self.all_data if d['Group'] == channel]
            df = pd.DataFrame(channel_data)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            fname = f"complete_{channel.replace('@','')}_in_{self.config.FILE_PREFIX}_{timestamp}_{channel_processed:05d}"

            if self.config.OUTPUT_FORMAT == "parquet":
                filepath = self.output_dir / f"{fname}.parquet"
                df.to_parquet(filepath, index=False)
            else:
                filepath = self.output_dir / f"{fname}.xlsx"
                df.to_excel(filepath, index=False, engine='openpyxl')

            print(f"  Channel file saved: {filepath.name}")

        # Rate limiting: wait at least 60s between channels
        elapsed = time.time() - self.start_time
        if elapsed < 60:
            await asyncio.sleep(60 - elapsed)

    async def run(self):
        """Main scraping loop."""
        await self.connect()

        try:
            for channel in self.config.CHANNELS:
                if self.total_processed >= self.config.MAX_MESSAGES:
                    break
                if time.time() - self.start_time > self.config.TIMEOUT_SECONDS:
                    break
                await self.scrape_channel(channel.strip())
        finally:
            self._save_final()
            await self.disconnect()


# =============================================================================
# ARGUMENT PARSING & MAIN
# =============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Telegram Channel/Group Scraper using Telethon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python telegram_scraper.py --api-id 12345678 --api-hash abcdef --phone +1234567890 \\
    --channels "@channel1,@channel2" --date-min 2024-01-01 --date-max 2024-12-31

  python telegram_scraper.py --api-id 12345678 --api-hash abcdef --phone +1234567890 \\
    --channels "@marketplace" --keyword "sell" --output-format excel
        """
    )

    # Required credentials
    parser.add_argument("--api-id", type=int, help="Telegram API ID (from my.telegram.org/apps)")
    parser.add_argument("--api-hash", type=str, help="Telegram API Hash (from my.telegram.org/apps)")
    parser.add_argument("--phone", type=str, help="Phone number with country code (e.g., +1234567890)")
    parser.add_argument("--username", type=str, default="", help="Telegram username (optional, for session)")

    # Scraping parameters
    parser.add_argument("--channels", type=str, required=False,
                        help='Comma-separated list of channels: "@chan1,@chan2,https://t.me/chan3"')
    parser.add_argument("--date-min", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--date-max", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument("--keyword", type=str, default="", help="Search keyword (optional)")
    parser.add_argument("--max-messages", type=int, default=1_000_000, help="Max messages per channel")
    parser.add_argument("--timeout", type=int, default=21600, help="Timeout in seconds (max 21600)")

    # Output settings
    parser.add_argument("--output-format", choices=["excel", "parquet"], default="excel",
                        help="Output format: excel (.xlsx) or parquet (.parquet)")
    parser.add_argument("--output-dir", type=str, default="./output", help="Output directory")
    parser.add_argument("--file-prefix", type=str, default="telegram_scrape", help="Output file prefix")

    return parser.parse_args()


def build_config(args) -> ScraperConfig:
    """Build config from args, falling back to class defaults."""
    config = ScraperConfig()

    # Override with CLI args if provided
    if args.api_id:
        config.API_ID = args.api_id
    if args.api_hash:
        config.API_HASH = args.api_hash
    if args.phone:
        config.PHONE = args.phone
    if args.username:
        config.USERNAME = args.username

    if args.channels:
        config.CHANNELS = [c.strip() for c in args.channels.split(",")]
    if args.date_min:
        config.DATE_MIN = datetime.fromisoformat(args.date_min).replace(tzinfo=timezone.utc)
    if args.date_max:
        config.DATE_MAX = datetime.fromisoformat(args.date_max).replace(tzinfo=timezone.utc)
    if args.keyword is not None:
        config.KEYWORD = args.keyword
    if args.max_messages:
        config.MAX_MESSAGES = args.max_messages
    if args.timeout:
        config.TIMEOUT_SECONDS = min(args.timeout, 21600)  # Cap at 6 hours

    config.OUTPUT_FORMAT = args.output_format
    config.OUTPUT_DIR = args.output_dir
    config.FILE_PREFIX = args.file_prefix

    return config


def validate_config(config: ScraperConfig) -> bool:
    """Validate required configuration."""
    errors = []

    if config.API_ID == 0:
        errors.append("API_ID is required (get from https://my.telegram.org/apps)")
    if not config.API_HASH:
        errors.append("API_HASH is required (get from https://my.telegram.org/apps)")
    if not config.PHONE:
        errors.append("PHONE is required (format: +1234567890)")
    if not config.CHANNELS:
        errors.append("At least one CHANNEL is required (use --channels or edit config)")

    if errors:
        print("\n✗ Configuration Errors:")
        for err in errors:
            print(f"  - {err}")
        print("\nGet API credentials at: https://my.telegram.org/apps")
        return False

    return True


def main():
    check_credentials_and_open_drive()
    args = parse_args()
    config = build_config(args)

    print("=" * 60)
    print("TELEGRAM SCRAPER - Standalone Python Script")
    print("=" * 60)
    print(f"Channels: {', '.join(config.CHANNELS)}")
    print(f"Date range: {config.DATE_MIN.date()} to {config.DATE_MAX.date()}")
    print(f"Keyword filter: '{config.KEYWORD}' (empty = all messages)")
    print(f"Max messages: {config.MAX_MESSAGES:,}")
    print(f"Timeout: {config.TIMEOUT_SECONDS}s")
    print(f"Output: {config.OUTPUT_FORMAT.upper()} in {config.OUTPUT_DIR}/")
    print(f"Seller keywords: {len(config.SELLER_KEYWORDS)} terms")
    print(f"Buyer keywords: {len(config.BUYER_KEYWORDS)} terms")
    print("=" * 60)

    if not validate_config(config):
        return 1

    # Confirm before starting
    response = input("\nStart scraping? (y/N): ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return 0

    scraper = TelegramScraper(config)

    try:
        asyncio.run(scraper.run())
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user. Saving progress...")
        scraper._save_final()
    except Exception as e:
        print(f"\n✗ Fatal error: {type(e).__name__}: {e}")
        scraper._save_final()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
