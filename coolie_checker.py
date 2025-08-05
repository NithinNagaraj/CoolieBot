import os
import sys
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller

# -------------------- Telegram --------------------
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

# -------------------- Launch Chrome Headless --------------------
def launch_browser():
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/google-chrome"  # required in GitHub Actions
    return webdriver.Chrome(options=options)

# -------------------- Main Movie Checker --------------------
def main(movie_name):
    movie_name = movie_name.strip()
    if not movie_name:
        print("❗ Movie name is empty")
        return

    print(f"🔍 Searching for: '{movie_name}'")

    driver = launch_browser()
    url = "https://in.bookmyshow.com/explore/movies-bengaluru?languages=tamil,telugu,english"
    print(f"🌐 Opening: {url}")
    driver.get(url)

    try:
        # Wait for movie cards to be present
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.__movie-card-anchor"))
        )
    except Exception:
        send_telegram_message("⚠️ Timed out waiting for movie list to load.")
        driver.quit()
        return

    cards = driver.find_elements(By.CSS_SELECTOR, "a.__movie-card-anchor")
    print(f"🎬 Found {len(cards)} movie cards")

    movie_found = False
    for card in cards:
        try:
            title_elem = card.find_element(By.CSS_SELECTOR, "div.__movie-name")
            title = title_elem.text.strip()
            print(f"→ Movie: {title}")

            if movie_name.lower() in title.lower():
                href = card.get_attribute("href")
                send_telegram_message(f"🎉 Booking open for *{title}*\n🔗 {href}")
                movie_found = True
                break
        except Exception as e:
            print(f"⚠️ Error reading a card: {e}")

    if not movie_found:
        send_telegram_message(f"❌ *{movie_name}* is not yet open for booking in Bengaluru.")

    driver.quit()

# -------------------- Entry Point --------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❗ Please provide a movie name as an argument.")
        print("Usage: python coolie_checker_selenium.py 'Movie Name'")
        sys.exit(1)

    movie_name_arg = " ".join(sys.argv[1:])
    main(movie_name_arg)
