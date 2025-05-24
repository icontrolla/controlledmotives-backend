import asyncio
from .models import Artwork
from playwright.async_api import async_playwright
from django_q.tasks import async_task

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
