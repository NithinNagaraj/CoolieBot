import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message, image_url=None):
    send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    if image_url:
        payload["text"] = f"<a href='{image_url}'>🖼️ Poster</a>\n\n" + payload["text"]

    try:
        requests.post(send_url, data=payload, timeout=10)
    except Exception as e:
        print("⚠️ Failed to send Telegram message:", e)
