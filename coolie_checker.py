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

# Telegram message sender
def send_telegram_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("⚠️ Telegram credentials missing.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        res = requests.post(url, json=payload)
        print(f"✅ Telegram sent: {res.status_code}")
    except Exception as e:
        print(f"⚠️ Telegram send failed: {e}")

# Browser launcher with stealth options
def launch_browser():
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.binary_location = "/usr/bin/google-chrome"  # Required on GitHub Actions
    return webdriver.Chrome(options=options)

# Main logic
def main(movie_name):
    movie_name = movie_name.strip().lower()
    print(f"🔍 Searching for movie: '{movie_name}'")

    url = "https://in.bookmyshow.com/explore/movies-bengaluru?languages=tamil,telugu,english"
    print(f"🌐 Opening: {url}")

    driver = launch_browser()
    driver.get(url)

    try:
        # Wait for movie cards to load (up to 15s)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.__movie-card-anchor"))
        )
    except:
        send_telegram_message("⚠️ Timed out waiting for movie list to load.")
        driver.quit()
        return

    try:
        cards = driver.find_elements(By.CSS_SELECTOR, "a.__movie-card-anchor")
        print(f"🎬 Found {len(cards)} movie cards")

        movie_found = False

        for card in cards:
            title_elem = card.find_element(By.CSS_SELECTOR, "div.__movie-name")
            title = title_elem.text.strip()
            print(f"→ Movie: {title}")

            if movie_name in title.lower():
                href = card.get_attribute("href")
                send_telegram_message(f"🎉 *{title}* is now open for booking!\n🎟️ [Book Now]({href})")
                movie_found = True
                break

        if not movie_found:
            send_telegram_message(f"❌ *{movie_name.title()}* is not yet open for booking in Bengaluru.")

    except Exception as e:
        send_telegram_message(f"🔥 Movie check failed.\nError: {e}")
        print("Error:", e)

    driver.quit()

# CLI entry
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❗️ Please provide a movie name as an argument.")
        print("Usage: python coolie_checker_selenium.py 'Kingdom'")
        sys.exit(1)

    movie_name_arg = " ".join(sys.argv[1:])
    main(movie_name_arg)
