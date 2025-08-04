import requests
from bs4 import BeautifulSoup
from telegram_notify import send_telegram
import os

CITY = "bengaluru"
MOVIE_NAME = os.getenv("MOVIE_NAME", "su from so").lower().strip()
FALLBACK_POSTER = "https://www.wallsnapy.com/img_gallery/coolie-movie-rajini--poster-4k-download-9445507.jpg"

BMS_URL = f"https://in.bookmyshow.com/explore/movies-{CITY}"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://in.bookmyshow.com/",
    "Origin": "https://in.bookmyshow.com",
    "X-Requested-With": "XMLHttpRequest"
}


def check_movie():
    city = "Bangalore"
    api_url = f"https://in.bookmyshow.com/serv/getData?cmd=QUICKBOOK&type=MT&city={city}"

    try:
        response = requests.get(api_url, headers=headers)
        data = response.json()

        movies = data.get("moviesData", {}).values()

        for movie in movies:
            title = movie.get("EventTitle", "").lower()
            if MOVIE_NAME in title:
                movie_url = f"https://in.bookmyshow.com/buytickets/{movie.get('EventURL')}/{CITY}/eventcode/{movie.get('EventCode')}"
                poster_url = movie.get("EventImageUrl", FALLBACK_POSTER)

                message = f"🎬 <b>{movie.get('EventTitle')} is now live in Bangalore!</b>\n"
                message += f"<a href='{movie_url}'>🎟️ Book Now</a>\n\n"
                message += f"🎞️ Language: {movie.get('Language')}\n"
                message += f"⭐ Rating: {movie.get('avgRating') or 'N/A'}"

                send_telegram(message, poster_url)
                return

        send_telegram(f"❌ <b>{MOVIE_NAME.title()}</b> is not yet open for booking in Bangalore.")
    except Exception as e:
        print("Error calling BMS API:", e)
        send_telegram("⚠️ Failed to contact BookMyShow.")


def get_showtimes(movie_url):
    try:
        movie_page = requests.get(movie_url, headers=headers)
        soup = BeautifulSoup(movie_page.text, "html.parser")

        theatres = soup.select(".venue-card")
        if not theatres:
            return None

        result = "<b>🎭 Theatres & Timings:</b>\n"
        for t in theatres[:5]:
            name_tag = t.select_one(".__venue-name")
            name = name_tag.text.strip() if name_tag else "Unknown"

            times = t.select("ul li")
            slots = [time.text.strip() for time in times if time.text.strip()]
            if slots:
                result += f"• <b>{name}</b>: {' | '.join(slots)}\n"

        return result if result.strip() else None
    except Exception as e:
        print(f"Error scraping showtimes: {e}")
        return None

if __name__ == "__main__":
    check_movie()
