import asyncio
import json
import os
import requests
import logging
import aiohttp
import boto3
from django.conf import settings
from django.core.management.base import BaseCommand
from playwright.async_api import async_playwright

# Pinterest credentials
PINTEREST_EMAIL = "walternyika20@gmail.com"
PINTEREST_PASSWORD = "Controll3r@2004"

# DeepSeek API key
OPENROUTER_API_KEY = "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"  # <- Replace this with your actual DeepSeek key

# Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Referer": "https://www.google.com/",
}

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)



# Function to classify image using DeepSeek Vision (or similar AI API)
def classify_image(image_url):
    try:
        prompt = f"Classify this artwork: {image_url}"
        response = requests.post(
            "https://api.deepseek.com/vision/classify",  # Hypothetical URL
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={"image_url": image_url, "prompt": prompt}
        )
        result = response.json()
        return result.get("category", "uncategorized")
    except Exception as e:
        print(f"Classification error: {e}")
        return "uncategorized"


async def generate_ai_description(image_url):
    prompt = (
        f"Analyze this artwork image and generate a JSON output in the format:\n"
        f'{"category": "e.g. finearts, virtuall-art, conceptual-art, design-illustration, photography, abstract, fashion", '
        f'"description": "Max 20-word description of style, color, and feeling"}\n\n'
        f"Image URL: {image_url}"
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "You're a professional art critic and curator."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data) as resp:
                resp.raise_for_status()
                result = await resp.json()
                reply = result['choices'][0]['message']['content']

                try:
                    return json.loads(reply)
                except json.JSONDecodeError:
                    return {
                        "category": "Unknown",
                        "description": reply[:200]
                    }
    except Exception as e:
        logger.error(f"[OpenRouter Error] {e}")
        return {"category": "Unknown", "description": "No description available."}


async def login_pinterest(page):
    await page.goto("https://www.pinterest.com/login/", wait_until="networkidle", timeout=80000)
    await page.fill('input[type="email"]', PINTEREST_EMAIL)
    await page.fill('input[type="password"]', PINTEREST_PASSWORD)
    await page.click('button[type="submit"]')
    await page.wait_for_selector("div[data-test-id='header-profile']", timeout=20000)


async def scrape_pinterest(url, scrolls=6):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            extra_http_headers=HEADERS,
            user_agent=HEADERS["User-Agent"]
        )
        page = await context.new_page()
        await page.route("**/*", lambda route: route.continue_())

        await login_pinterest(page)
        await page.goto(url, wait_until="domcontentloaded", timeout=120000)

        for _ in range(scrolls):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(5000)

        await page.wait_for_selector("div[role='listitem']", timeout=30000)
        pins = await page.query_selector_all("div[role='listitem']")
        pins_data = []

        for pin in pins:
            try:
                anchor = await pin.query_selector("a")
                href = await anchor.get_attribute("href") if anchor else None
                img = await pin.query_selector("img")
                img_url = await img.get_attribute("src") if img else None

                if href and img_url:
                    ai_data = await generate_ai_description(img_url)
                    pins_data.append({
                        "image_url": img_url,
                        "source_url": href,
                        "category": ai_data.get("category", "Unknown"),
                        "description": ai_data.get("description", "")
                    })
                    await asyncio.sleep(1)  # rate limit protection
            except Exception as e:
                logger.warning(f"Error scraping a pin: {e}")
                continue

        await browser.close()
        return pins_data


def upload_to_b2(json_data, filename="behance_artworks.json"):
    session = boto3.session.Session()
    s3_client = session.client(
        service_name='s3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        region_name=settings.AWS_S3_REGION_NAME,
    )

    try:
        existing_obj = s3_client.get_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=filename
        )
        existing_data = json.loads(existing_obj['Body'].read().decode('utf-8'))
        logger.info(f"Loaded {len(existing_data)} existing pins from B2.")
    except s3_client.exceptions.NoSuchKey:
        existing_data = []
        logger.info("No existing JSON file found. Creating a new one.")
    except Exception as e:
        logger.error(f"Error reading existing file: {e}")
        existing_data = []

    # Optional: Remove duplicates based on image_url
    existing_urls = {item['image_url'] for item in existing_data}
    new_data = [item for item in json_data if item['image_url'] not in existing_urls]

    merged_data = existing_data + new_data

    s3_client.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=filename,
        Body=json.dumps(merged_data),
        ContentType='application/json',
        ACL='public-read'
    )
    logger.info(f"Uploaded {len(merged_data)} total pins to B2 (added {len(new_data)} new pins).")


class Command(BaseCommand):
    help = 'Scrapes Pinterest pins with AI metadata and uploads to Backblaze B2'

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str, required=True, help='The Pinterest URL to scrape')
        parser.add_argument('--scrolls', type=int, default=6, help='Number of scrolls to perform')
        parser.add_argument('--output', type=str, default="behance_artworks.json", help='Filename in B2')

    def handle(self, *args, **options):
        url = options['url']
        scrolls = options['scrolls']
        filename = options['output']

        self.stdout.write(f"Starting scrape of URL: {url} with {scrolls} scrolls...")

        try:
            pins_data = asyncio.run(scrape_pinterest(url, scrolls))
            self.stdout.write(f"Scraped {len(pins_data)} pins with AI enrichment.")
            upload_to_b2(pins_data, filename)
            self.stdout.write(f"Uploaded enriched data to B2 bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
        except Exception as e:
            self.stderr.write(f"Error: {e}")
