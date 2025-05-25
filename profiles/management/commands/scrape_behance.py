import asyncio
import json
import boto3
from django.conf import settings
from django.core.management.base import BaseCommand
from playwright.async_api import async_playwright

# Your Pinterest credentials
PINTEREST_EMAIL = "walternyika20@gmail.com"
PINTEREST_PASSWORD = "Controll3r@2004"

# Custom headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Referer": "https://www.google.com/",
}

async def login_pinterest(page):
    await page.goto("https://www.pinterest.com/login/", wait_until="networkidle", timeout=80000)
    await page.wait_for_selector('input[type="email"]', timeout=20000)
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

        # Optional: Set additional headers on page navigation for safety
        await page.route("**/*", lambda route: route.continue_())

        await login_pinterest(page)

        await page.goto(url, wait_until="domcontentloaded", timeout=120000)  # Waits less strictly

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
                    pins_data.append({"image_url": img_url, "source_url": href})
            except Exception:
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

    s3_client.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=filename,
        Body=json.dumps(json_data),
        ContentType='application/json',
        ACL='public-read'
    )


class Command(BaseCommand):
    help = 'Scrapes Pinterest pins with login using Playwright and uploads to Backblaze B2'

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str, required=True, help='The Pinterest URL to scrape')
        parser.add_argument('--scrolls', type=int, default=6, help='Number of scrolls to perform')

    def handle(self, *args, **options):
        url = options['url']
        scrolls = options['scrolls']
        self.stdout.write(f"Starting scrape of Pinterest URL: {url} with {scrolls} scrolls...")

        try:
            pins_data = asyncio.run(scrape_pinterest(url, scrolls))
            self.stdout.write(f"Scraped {len(pins_data)} pins.")
            upload_to_b2(pins_data)
            self.stdout.write(f"Uploaded JSON to Backblaze B2 bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
        except Exception as e:
            self.stderr.write(f"Error: {e}")
