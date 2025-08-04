import requests
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message, image_url=None):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram credentials not set.")
        return

    try:
        if image_url:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            data = {
                "chat_id": CHAT_ID,
                "caption": message,
                "parse_mode": "HTML",
                "photo": image_url
            }
        else:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }

        response = requests.post(url, data=data)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
