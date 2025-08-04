import os
import asyncio
from telegram_notify import send_telegram
from playwright.async_api import async_playwright

MOVIE_NAME = os.getenv("MOVIE_NAME", "kingdom").lower()
CITY = "bengaluru"
LANGUAGES = ["tamil", "telugu", "english"]
FALLBACK_POSTER = "https://www.wallsnapy.com/img_gallery/coolie-movie-rajini--poster-4k-download-9445507.jpg"

async def check_movie():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Safari/537.36",
            locale="en-US"
        )
        page = await context.new_page()

        try:
            found = False
            for lang in LANGUAGES:
                url = f"https://in.bookmyshow.com/explore/movies-{CITY}?languages={lang}"
                print(f"Checking: {url}")
                await page.goto(url, timeout=60000)

                try:
                    await page.wait_for_selector("div.sc-7o7nez-0", timeout=60000)
                except Exception:
                    print(f"❌ Failed to load movies for language: {lang}")
                    continue

                movie_cards = await page.query_selector_all("div.sc-7o7nez-0 a")
                for card in movie_cards:
                    title = (await card.get_attribute("aria-label") or "").lower()
                    print("Found movie:", title)
                    if MOVIE_NAME in title or MOVIE_NAME.replace(" ", "") in title.replace(" ", ""):
                        found = True
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
            if not found:
                send_telegram(f"❌ <b>{MOVIE_NAME.title()}</b> is not yet open for booking in Tamil/Telugu/English in Bangalore.")
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
