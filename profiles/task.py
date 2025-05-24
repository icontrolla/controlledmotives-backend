import asyncio
import json
from datetime import datetime
from django.conf import settings
from playwright.async_api import async_playwright
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

async def async_scrape_pinterest(url, scrolls=6):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        for _ in range(scrolls):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(3000)

        await page.wait_for_selector("div[role='listitem']")
        pins = await page.query_selector_all("div[role='listitem']")
        pins_data = []

        for pin in pins:
            try:
                anchor = await pin.query_selector("a")
                href = await anchor.get_attribute("href") if anchor else None
                img = await pin.query_selector("img")
                img_url = await img.get_attribute("src") if img else None

                if href and img_url:
                    pins_data.append({
                        "image_url": img_url,
                        "source_url": href
                    })
            except Exception:
                continue

        await browser.close()
        return pins_data

def scrape_pinterest(url, scrolls=6):
    return asyncio.run(async_scrape_pinterest(url, scrolls))


def scrape_pinterest_to_b2(url, scrolls=6, prefix="pinterest_scrapes/", base_filename="behance_artworks.json"):
    # Step 1: Scrape Pinterest
    print(f"Starting Pinterest scrape for: {url}")
    pins_data = scrape_pinterest(url, scrolls)

    # Initialize boto3 S3 client for B2
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        region_name=settings.AWS_S3_REGION_NAME,
    )

    # Step 2: Fetch existing JSON content from B2 bucket (if exists)
    try:
        obj = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=base_filename)
        existing_json_bytes = obj['Body'].read()
        existing_data = json.loads(existing_json_bytes)
        print(f"Loaded existing data from {base_filename}, {len(existing_data)} items found.")
    except ClientError as e:
        # If the object doesn't exist, start fresh with an empty list
        if e.response['Error']['Code'] == 'NoSuchKey':
            print(f"{base_filename} does not exist. Starting new JSON data.")
            existing_data = []
        else:
            print(f"Error fetching {base_filename}: {e}")
            return None
    except Exception as e:
        print(f"Unexpected error loading existing JSON: {e}")
        return None

    # Step 3: Append new pins to existing data
    combined_data = existing_data + pins_data
    print(f"Appending {len(pins_data)} new pins. Total now: {len(combined_data)}")

    # Step 4: Upload combined JSON back to B2 bucket, overwrite existing file
    try:
        combined_json_str = json.dumps(combined_data, indent=2)
        s3.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=base_filename,
            Body=combined_json_str,
            ContentType='application/json'
        )
        print(f"✅ Successfully uploaded combined JSON to {base_filename}")
        return base_filename
    except NoCredentialsError:
        print("❌ AWS credentials not found.")
        return None
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None
