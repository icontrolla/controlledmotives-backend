import json
import os
import asyncio
import logging
from django.core.management.base import BaseCommand
from b2sdk.v2 import B2Api, InMemoryAccountInfo
from dotenv import load_dotenv

from profiles.management.commands.scrape_pinterest import scrape_behance  # Assuming scrape_pinterest is available

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = "Scrapes Pinterest pins and appends new fine-arts entries to behance_artworks.json in B2"

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str, required=True, help='Pinterest URL to scrape')
        parser.add_argument('--scrolls', type=int, default=6, help='Number of scrolls')
        parser.add_argument('--category', type=str, default="fine-arts", help='Default category if AI fails')
        parser.add_argument('--file', type=str, default="behance_artworks.json", help='Target B2 JSON filename')

    def handle(self, *args, **options):
        # Credentials
        B2_KEY_ID = os.getenv("B2_KEY_ID")
        B2_APP_KEY = os.getenv("B2_APP_KEY")
        BUCKET_NAME = "controlled-media"
        FILE_NAME = options["file"]
        LOCAL_TEMP_FILE = "artworks_temp.json"

        if not B2_KEY_ID or not B2_APP_KEY:
            self.stderr.write("Missing B2 credentials. Check .env or environment variables.")
            return

        # Authenticate with B2
        info = InMemoryAccountInfo()
        b2_api = B2Api(info)
        b2_api.authorize_account("production", B2_KEY_ID, B2_APP_KEY)
        bucket = b2_api.get_bucket_by_name(BUCKET_NAME)

        # Download the existing JSON
        try:
            bucket.download_file_by_name(FILE_NAME).save_to(LOCAL_TEMP_FILE)
            with open(LOCAL_TEMP_FILE, "r") as f:
                data = json.load(f)
            self.stdout.write(f"Loaded {len(data)} existing entries.")
        except Exception as e:
            self.stderr.write(f"Error downloading {FILE_NAME}: {e}")
            data = []

        # Scrape Pinterest for new entries
        url = options["url"]
        scrolls = options["scrolls"]

        try:
            pins_data = asyncio.run(scrape_pinterest(url, scrolls))
            self.stdout.write(f"Scraped {len(pins_data)} Pinterest entries.")
        except Exception as e:
            self.stderr.write(f"Pinterest scraping failed: {e}")
            return

        existing_urls = {item["image_url"] for item in data}
        unique_new_entries = [pin for pin in pins_data if pin["image_url"] not in existing_urls]

        if not unique_new_entries:
            self.stdout.write(self.style.WARNING("No new unique entries to append."))
            return

        data.extend(unique_new_entries)

        with open(LOCAL_TEMP_FILE, "w") as f:
            json.dump(data, f, indent=2)

        bucket.upload_local_file(
            local_file=LOCAL_TEMP_FILE,
            file_name=FILE_NAME,
            file_infos={"category": "art-json"}
        )

        self.stdout.write(self.style.SUCCESS(
            f"Added {len(unique_new_entries)} new artworks to {FILE_NAME} on Backblaze B2."
        ))
