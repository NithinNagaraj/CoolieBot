import requests
from bs4 import BeautifulSoup
from telegram_notify import send_telegram
import os

CITY = "bengaluru"
MOVIE_NAME = os.getenv("MOVIE_NAME", "su from so").lower().strip()
FALLBACK_POSTER = "https://www.wallsnapy.com/img_gallery/coolie-movie-rajini--poster-4k-download-9445507.jpg"

BMS_URL = f"https://in.bookmyshow.com/explore/movies-{CITY}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36"
}

def check_movie():
    response = requests.get(BMS_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    found_movies = soup.find_all("a", class_="__movie-card-anchor")

    for movie in found_movies:
        title = movie.get("aria-label", "").lower().strip()
        if MOVIE_NAME in title:
            movie_url = "https://in.bookmyshow.com" + movie.get("href", "")
            poster = movie.find("img")
            poster_url = poster["src"] if poster and poster.get("src") else FALLBACK_POSTER

            details = get_showtimes(movie_url)

            message = f"🎬 <b>{title.title()} is now live in Bangalore!</b>\n"
            message += f"<a href='{movie_url}'>🎟️ Book Now</a>\n\n"
            message += details or "Showtimes not available yet. Check the link for updates."

            send_telegram(message, poster_url)
            return

    send_telegram(f"❌ <b>{MOVIE_NAME.title()}</b> is not yet open for booking in Bangalore.")

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
