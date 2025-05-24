import asyncio
import json
from datetime import datetime
from django.conf import settings
from playwright.async_api import async_playwright
import boto3
from botocore.exceptions import NoCredentialsError

# Core Pinterest async scraper
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

# Blocking wrapper
def scrape_pinterest(url, scrolls=6):
    return asyncio.run(async_scrape_pinterest(url, scrolls))

# Upload scraped JSON to Backblaze B2
def scrape_pinterest_to_b2(url, scrolls=6, prefix="pinterest_scrapes/"):
    # Step 1: Scrape Pinterest
    print(f"Starting Pinterest scrape for: {url}")
    pins_data = scrape_pinterest(url, scrolls)

    # Step 2: Convert to JSON
    json_data = json.dumps(pins_data, indent=2)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_name = f"{prefix}scrape_{timestamp}.json"

    # Step 3: Upload to Backblaze B2
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        s3.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=file_name,
            Body=json_data,
            ContentType='application/json'
        )

        print(f"✅ Upload successful: {file_name}")
        return file_name

    except NoCredentialsError:
        print("❌ AWS credentials not found.")
        return None

    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None
