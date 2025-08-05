import os
import sys
import time
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def send_telegram_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("⚠️ TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is missing")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        print(f"✅ Telegram sent: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Telegram error: {e}")

def launch_browser():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return uc.Chrome(options=options, headless=True)

def main(movie_name):
    movie_name = movie_name.strip()
    if not movie_name:
        print("❗ Movie name is empty")
        return

    print(f"🔍 Searching for: '{movie_name}'")
    driver = launch_browser()

    try:
        url = "https://in.bookmyshow.com/explore/movies-bengaluru?languages=tamil,telugu,english"
        print(f"🌐 Opening: {url}")
        driver.get(url)
        time.sleep(10)

        cards = driver.find_elements(By.CSS_SELECTOR, "a.__movie-card-anchor")
        print(f"🎬 Found {len(cards)} movie cards")

        found = False
        for card in cards:
            title_elem = card.find_element(By.CSS_SELECTOR, "div.__movie-name")
            title = title_elem.text.strip()
            print(f"→ Movie: {title}")
            if movie_name.lower() in title.lower():
                href = card.get_attribute("href")
                send_telegram_message(f"🎉 Booking open for *{title}*\n🔗 {href}")
                found = True
                break

        if not found:
            send_telegram_message(f"❌ *{movie_name}* is not yet open for booking in Bengaluru.")

    except Exception as e:
        send_telegram_message(f"🔥 Failed to scrape.\nError: {e}")
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

    driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❗ Please provide a movie name as an argument.")
        print("Usage: python coolie_checker.py 'Movie Name'")
        sys.exit(1)

    movie_name_arg = " ".join(sys.argv[1:])
    main(movie_name_arg)
