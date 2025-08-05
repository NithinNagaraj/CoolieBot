import sys
import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def send_telegram_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("⚠️ Telegram credentials missing")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=data)
        print(f"✅ Telegram sent: {r.status_code}")
    except Exception as e:
        print(f"❌ Telegram failed: {e}")

def launch_browser():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def main(movie_name):
    movie_name = movie_name.strip().lower()
    if not movie_name:
        print("❗ No movie name provided.")
        return

    driver = launch_browser()
    driver.get("https://www.district.in/movies/")
    time.sleep(5)

    try:
        cards = driver.find_elements(By.CSS_SELECTOR, ".movie-card")
        print(f"🎬 Found {len(cards)} movies")

        for card in cards:
            title_elem = card.find_element(By.TAG_NAME, "h2")
            title = title_elem.text.strip()
            if movie_name in title.lower():
                poster = card.find_element(By.TAG_NAME, "img").get_attribute("src")
                theatre = card.find_element(By.CLASS_NAME, "theatre").text
                showtimes = card.find_element(By.CLASS_NAME, "showtimes").text
                msg = f"🎬 *{title}*\n🖼️ Poster: {poster}\n📍 Theatre: {theatre}\n🕒 Showtimes: {showtimes}"
                send_telegram_message(msg)
                break
        else:
            send_telegram_message(f"❌ *{movie_name.title()}* is not yet listed on District.in")

    except Exception as e:
        print("❌ Scraping error:", e)
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

    driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python district_checker.py 'Movie Name'")
        sys.exit(1)
    main(" ".join(sys.argv[1:]))
