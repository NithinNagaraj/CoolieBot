# 🎬 Coolie Movie Ticket Notifier

This GitHub Action checks every hour if Rajinikanth's **Coolie** movie is available for booking in **Bangalore** on BookMyShow. Sends updates via **Telegram**, including:

- Movie status
- Poster
- Theatres & timings

## 🛠 Setup Instructions

### 1. Create Telegram Bot

- Open Telegram and search `@BotFather`
- Send `/newbot` and get the bot token

### 2. Get Your Telegram User ID

- Use `@GetIDsBot` in Telegram
- Note down the numeric ID

### 3. Set GitHub Secrets

Go to **GitHub → Settings → Secrets → Actions**, add:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### 4. Upload Files to GitHub

Push this folder to your GitHub repo. GitHub will run it every hour 🎯

## 🔧 Local Test (Optional)

```bash
pip install -r requirements.txt
python coolie_checker.py
```
