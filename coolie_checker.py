import os
import requests
from telegram_notify import send_telegram

CITY = "bengaluru"
MOVIE_NAME = os.getenv("MOVIE_NAME", "kingdom").lower()
LANGUAGES = "tamil,telugu,english"

MOVIE_LIST_URL = f"https://in.bookmyshow.com/api/explore/v2/movies?city={CITY}&language={LANGUAGES}"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}

def find_movie():
    try:
        response = requests.get(MOVIE_LIST_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        for movie in data.get("movies", []):
            title = movie.get("name", "").lower()
            if MOVIE_NAME in title or MOVIE_NAME.replace(" ", "") in title.replace(" ", ""):
                return {
                    "title": movie.get("name"),
                    "eventCode": movie.get("eventCode"),
                    "url": "https://in.bookmyshow.com" + movie.get("deeplink", ""),
                    "poster": movie.get("verticalPoster") or movie.get("horizontalPoster")
                }
    except Exception as e:
        print("Failed to fetch movie list:", e)
    return None

def fetch_showtimes(event_code):
    try:
        url = f"https://in.bookmyshow.com/api/explore/v1/shows?eventCode={event_code}&city={CITY}"
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        data = res.json()
        theatres = data.get("venueShows", [])
        result = ""
        for theatre in theatres[:5]:  # limit to 5 theatres
            name = theatre.get("venue", {}).get("name")
            shows = [show.get("showTimeDisplay") for show in theatre.get("shows", [])]
            if name and shows:
                result += f"• <b>{name}</b>: {' | '.join(shows)}\n"
        return result or "⚠️ No showtimes available yet."
    except Exception as e:
        print("Failed to fetch showtimes:", e)
        return None

def main():
    movie = find_movie()
    if not movie:
        send_telegram(f"❌ <b>{MOVIE_NAME.title()}</b> is not yet open for booking in Bengaluru.")
        return

    showtimes = fetch_showtimes(movie["eventCode"])
    if not showtimes:
        send_telegram(f"⚠️ Unable to fetch showtimes for <b>{movie['title']}</b> at the moment.")
        return

    msg = f"🎬 <b>{movie['title']}</b> is now available in Bengaluru!\n"
    msg += f"<a href='{movie['url']}'>🎟️ Book Now</a>\n\n"
    msg += f"{showtimes}"
    send_telegram(msg, movie["poster"])

if __name__ == "__main__":
    main()
