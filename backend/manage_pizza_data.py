import os
import logging
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# === Configuration ===
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://chill-pizza-universe.onrender.com")
SHEET_NAME = "PizzaGamingData"

# === Google Sheets Connection ===
def get_google_credentials():
    """Retrieve Google credentials from Render environment variables."""
    credentials_json = os.getenv("GOOGLE_CREDENTIALS")
    creds_dict = json.loads(credentials_json)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds).open(SHEET_NAME)

google_sheet = get_google_credentials()
logging.info("✅ Connected to Google Sheets")

# === Flask App for Webhooks ===
app = Flask(__name__)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(), bot)
    await application.process_update(update)
    return "OK", 200

# === Telegram Bot ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text("🍕 Welcome to ChillPizza! Start playing now!")

# Initialize bot
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))

# Set webhook
async def set_webhook():
    await application.bot.set_webhook(f"{WEBHOOK_URL}/{BOT_TOKEN}")

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())
    app.run(host="0.0.0.0", port=5000)

