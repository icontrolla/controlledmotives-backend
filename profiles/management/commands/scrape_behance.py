import asyncio
from django.core.management.base import BaseCommand
from playwright.async_api import async_playwright

# Put your Pinterest credentials here or get them securely from env vars
PINTEREST_EMAIL = "walternyika20@gmail.com"

PINTEREST_PASSWORD = "Controll3r@2004"


async def login_pinterest(page):
    await page.goto("https://www.pinterest.com/login/", timeout=20000)

    await page.fill('input[name="id"]', PINTEREST_EMAIL)
    await page.fill('input[name="password"]', PINTEREST_PASSWORD)
    await page.click('button[type="submit"]')

    # Debug: take a screenshot after clicking login
    await page.screenshot(path="after_login.png")

    # Try waiting for a more stable selector after login
    await page.wait_for_selector("div[data-test-id='header-profile']", timeout=20000)


async def scrape_pinterest(url, scrolls=6):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Login first
        await login_pinterest(page)

        # Now go to the target Pinterest URL
        await page.goto(url)

        for _ in range(scrolls):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(5000)  # wait 3 seconds for content to load

        # Wait for pins to appear
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


class Command(BaseCommand):
    help = 'Scrapes Pinterest pins with login using Playwright'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            required=True,
            help='The Pinterest URL to scrape',
        )
        parser.add_argument(
            '--scrolls',
            type=int,
            default=6,
            help='Number of scrolls to perform on the page',
        )

    def handle(self, *args, **options):
        url = options['url']
        scrolls = options['scrolls']
        self.stdout.write(f"Starting scrape of Pinterest URL: {url} with {scrolls} scrolls...")

        try:
            pins_data = asyncio.run(scrape_pinterest(url, scrolls))
            self.stdout.write(f"Scraped {len(pins_data)} pins:")
            for item in pins_data:
                self.stdout.write(f"Image URL: {item['image_url']} | Source URL: {item['source_url']}")
        except Exception as e:
            self.stderr.write(f"Error during scraping: {e}")
