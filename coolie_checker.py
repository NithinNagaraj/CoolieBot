import os
import asyncio
from telegram_notify import send_telegram
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

MOVIE_NAME = os.getenv("MOVIE_NAME", "kingdom").lower()
CITY = "bengaluru"
LANGUAGES = ["tamil", "telugu", "english"]
FALLBACK_POSTER = "https://www.wallsnapy.com/img_gallery/coolie-movie-rajini--poster-4k-download-9445507.jpg"

API_URL = f"https://in.bookmyshow.com/api/explore/v2/movies?city={CITY}&language={','.join(LANGUAGES)}"

async def fetch_movies_with_playwright(context):
    page = await context.new_page()
    await page.goto("https://in.bookmyshow.com/explore/movies-bengaluru", timeout=60000)
    result = await page.evaluate(f'''
        async () => {{
            const response = await fetch("{API_URL}");
            if (!response.ok) throw new Error("API call failed");
            return await response.json();
        }}
    ''')
    await page.close()
    return result.get("movies", [])

def find_movie(movies):
    for movie in movies:
        title = movie.get("name", "").lower()
        if MOVIE_NAME in title or MOVIE_NAME.replace(" ", "") in title.replace(" ", ""):
            return {
                "title": movie.get("name"),
                "url": f"https://in.bookmyshow.com{movie.get('deeplink')}",
                "poster": movie.get("verticalPoster") or FALLBACK_POSTER
            }
    return None

async def scrape_showtimes(context, url):
    try:
        page = await context.new_page()
        await page.goto(url, timeout=60000)
        await page.wait_for_selector(".venue-card", timeout=30000)
        html = await page.content()
        await page.close()
    except Exception as e:
        print("❌ Showtimes fetch failed:", e)
        return "⚠️ Showtimes not available at the moment."

    soup = BeautifulSoup(html, "html.parser")
    venues = soup.select(".venue-card")
    result = "<b>🎭 Theatres & Timings:</b>\n"
    for venue in venues[:5]:
        name_el = venue.select_one(".__venue-name")
        time_els = venue.select("ul li")
        if name_el and time_els:
            venue_name = name_el.get_text(strip=True)
            slots = [t.get_text(strip=True) for t in time_els]
            result += f"• <b>{venue_name}</b>: {' | '.join(slots)}\n"
    return result if result.strip() else "⚠️ No showtimes listed yet."

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        try:
            movies = await fetch_movies_with_playwright(context)
            movie = find_movie(movies)

            if movie:
                showtimes = await scrape_showtimes(context, movie["url"])
                message = f"🎬 <b>{movie['title']} is now live in Bangalore!</b>\n"
                message += f"<a href='{movie['url']}'>🎟️ Book Now</a>\n\n"
                message += showtimes
                send_telegram(message, movie["poster"])
            else:
                send_telegram(f"❌ <b>{MOVIE_NAME.title()}</b> is not yet open for booking in Bangalore.")
        except Exception as e:
            print("🔥 Failed to fetch or parse:", e)
            send_telegram("⚠️ Movie check failed.")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
