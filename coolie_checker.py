import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from telegram_notify import send_telegram

load_dotenv()

MOVIE_NAME = os.getenv("MOVIE_NAME", "kingdom").lower()
CITY = "bengaluru"
LANGUAGES = ["tamil", "telugu", "english"]

def launch_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

def get_movie_info(driver):
    for lang in LANGUAGES:
        url = f"https://in.bookmyshow.com/explore/movies-{CITY}?languages={lang}"
        print(f"🔍 Checking: {url}")
        driver.get(url)
        time.sleep(3)

        try:
            cards = driver.find_elements(By.CSS_SELECTOR, "a.__movie-card-anchor")
            for card in cards:
                title_elem = card.find_element(By.CSS_SELECTOR, "div.sc-7o7nez-0")
                title = title_elem.text.strip().lower()
                if MOVIE_NAME in title or MOVIE_NAME.replace(" ", "") in title.replace(" ", ""):
                    href = card.get_attribute("href")
                    img = card.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
                    return {
                        "title": title.title(),
                        "link": href,
                        "poster": img
                    }
        except Exception as e:
            print(f"⚠️ Error checking language {lang}: {e}")
    return None

def get_showtimes(driver, movie_url):
    driver.get(movie_url)
    time.sleep(5)
    shows_data = ""

    try:
        theatres = driver.find_elements(By.CSS_SELECTOR, "div.sc-bke1zw-0")
        for t in theatres[:5]:  # limit to 5 theatres
            try:
                theatre_name = t.find_element(By.CSS_SELECTOR, "a").text.strip()
                showtimes = t.find_elements(By.CSS_SELECTOR, "a.sc-1vmod7e-2")
                times = [s.text.strip() for s in showtimes if s.text.strip()]
                if times:
                    shows_data += f"• <b>{theatre_name}</b>: {' | '.join(times)}\n"
            except:
                continue
    except Exception as e:
        print("⚠️ Error extracting showtimes:", e)
    return shows_data or "⚠️ No showtimes found."

def main():
    driver = launch_browser()
    try:
        movie = get_movie_info(driver)
        if not movie:
            send_telegram(f"❌ <b>{MOVIE_NAME.title()}</b> is not yet open for booking in Bengaluru.")
            return
        shows = get_showtimes(driver, movie["link"])
        msg = f"🎬 <b>{movie['title']}</b> is now available in Bengaluru!\n"
        msg += f"<a href='{movie['link']}'>🎟️ Book Now</a>\n\n"
        msg += shows
        send_telegram(msg, movie["poster"])
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
