import os
import asyncio
from telegram_notify import send_telegram
from playwright.async_api import async_playwright
from playwright_stealth import stealth_sync

MOVIE_NAME = os.getenv("MOVIE_NAME", "Kingdom").lower()
CITY = "bengaluru"

FALLBACK_POSTER = "https://www.wallsnapy.com/img_gallery/coolie-movie-rajini--poster-4k-download-9445507.jpg"


async def check_movie():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        stealth_sync(context)
        page = await context.new_page()
        await stealth_sync(page)

        try:
            url = f"https://in.bookmyshow.com/explore/movies-{CITY}"
            await page.goto(url, timeout=60000)

            try:
                await page.wait_for_selector("a.__movie-card-anchor", timeout=60000)
            except Exception:
                # Save debug HTML for inspection
                html = await page.content()
                with open("debug.html", "w", encoding="utf-8") as f:
                    f.write(html)
                raise Exception("❌ Movie cards not found. HTML dumped to debug.html.")

            movie_cards = await page.query_selector_all("a.__movie-card-anchor")
            for card in movie_cards:
                title = (await card.get_attribute("aria-label") or "").lower()
                if MOVIE_NAME in title:
                    link = await card.get_attribute("href")
                    poster = await card.query_selector("img")
                    poster_url = await poster.get_attribute("src") if poster else FALLBACK_POSTER

                    full_url = "https://in.bookmyshow.com" + link
                    details = await get_showtimes(context, full_url)

                    message = f"🎬 <b>{title.title()} is now live in Bangalore!</b>\n"
                    message += f"<a href='{full_url}'>🎟️ Book Now</a>\n\n"
                    message += details or "Showtimes not available yet."

                    await browser.close()
                    send_telegram(message, poster_url)
                    return

            await browser.close()
            send_telegram(f"❌ <b>{MOVIE_NAME.title()}</b> is not yet open for booking in Bangalore.")
        except Exception as e:
            await browser.close()
            print("Playwright error:", e)
            send_telegram("⚠️ Failed to check BookMyShow.")


async def get_showtimes(context, movie_url):
    try:
        page = await context.new_page()
        await page.goto(movie_url, timeout=60000)
        await page.wait_for_selector(".venue-card", timeout=30000)

        venue_cards = await page.query_selector_all(".venue-card")
        result = "<b>🎭 Theatres & Timings:</b>\n"
        for card in venue_cards[:5]:
            venue_name_el = await card.query_selector(".__venue-name")
            venue_name = await venue_name_el.inner_text() if venue_name_el else "Unknown"

            time_slots = await card.query_selector_all("ul li")
            slots = [await t.inner_text() for t in time_slots]
            if slots:
                result += f"• <b>{venue_name}</b>: {' | '.join(slots)}\n"

        return result if result.strip() else None
    except Exception as e:
        print("Error scraping showtimes:", e)
        return None

if __name__ == "__main__":
    asyncio.run(check_movie())
