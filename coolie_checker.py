import os
import time
import sys
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller

# Telegram notifier
def send_telegram_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("⚠️ Telegram token or chat_id missing")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        print(f"✅ Telegram sent: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Telegram error: {e}")

# Browser setup
def launch_browser():
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/google-chrome"
    return webdriver.Chrome(options=options)

# Main logic
def main(movie_name):
    movie_name = movie_name.strip()
    print(f"🔍 Searching for movie: '{movie_name}'")

    driver = launch_browser()
    url = "https://in.bookmyshow.com/explore/movies-bengaluru?languages=tamil,telugu,english"
    print(f"🌐 Opening: {url}")
    driver.get(url)
    time.sleep(5)

    try:
        cards = driver.find_elements(By.CSS_SELECTOR, "a.__movie-card-anchor")
        movie_found = False

        print(f"🎬 Found {len(cards)} movie cards")
        for card in cards:
            title_elem = card.find_element(By.CSS_SELECTOR, "div.__movie-name")
            title = title_elem.text.strip()
            print(f"→ Movie: {title}")
            if movie_name.lower() in title.lower():
                href = card.get_attribute("href")
                send_telegram_message(f"🎉 Booking open for *{title}*\n🔗 {href}")
                movie_found = True
                break

        if not movie_found:
            send_telegram_message(f"❌ {movie_name} is not yet open for booking in Bengaluru.")

    except Exception as e:
        send_telegram_message(f"🔥 Movie check failed.\nError: {e}")
        print("Error:", e)

    driver.quit()

# Entry point
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❗️ Please provide a movie name as an argument.")
        print("Usage: python coolie_checker_selenium.py 'Kingdom'")
        sys.exit(1)

    movie_name_arg = " ".join(sys.argv[1:])
    main(movie_name_arg)
