import os
import logging
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

# === Configuration ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://chill-pizza-universe.onrender.com")
SHEET_NAME = "PizzaGamingData"

# === Logging Setup ===
logging.basicConfig(level=logging.INFO)

# === Google Sheets Connection ===
def get_google_credentials():
    """Retrieve Google credentials from environment variables."""
    credentials_json = os.getenv("GOOGLE_CREDENTIALS")
    if not credentials_json:
        logging.error("❌ GOOGLE_CREDENTIALS not found! Check environment variables.")
        raise ValueError("Missing GOOGLE_CREDENTIALS in environment variables")

    creds_dict = json.loads(credentials_json)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds).open(SHEET_NAME)

try:
    google_sheet = get_google_credentials()
    logging.info("✅ Successfully connected to Google Sheets!")
except Exception as e:
    logging.error(f"⚠️ Google Sheets connection failed: {e}")

# === Flask App for Webhooks ===
app = Flask(__name__)

# === Initialize Telegram Bot ===
application = Application.builder().token(BOT_TOKEN).build()

async def process_update(update: Update):
    """Process incoming Telegram updates asynchronously."""
    if not application.ready:
        logging.info("🔄 Initializing bot application...")
        await application.initialize()
    
    await application.process_update(update)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Processes incoming Telegram updates from Telegram Webhook."""
    try:
        update = Update.de_json(request.get_json(), application.bot)

        # Run the async function inside the event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process_update(update))

        return "OK", 200
    except Exception as e:
        logging.error(f"⚠️ Webhook processing error: {e}")
        return "Error", 500

# === Telegram Bot Commands ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text("🍕 Welcome to ChillPizza! Start playing now!")

application.add_handler(CommandHandler("start", start))

async def set_webhook():
    """Set webhook for Telegram bot."""
    await application.bot.set_webhook(f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logging.info(f"✅ Webhook set to: {WEBHOOK_URL}/{BOT_TOKEN}")

@app.route("/", methods=["GET"])
def home():
    """Basic home route to confirm Flask is running."""
    return "🚀 ChillPizza Backend is Live!", 200

if __name__ == "__main__":
    logging.info("🚀 Starting ChillPizza Bot Backend...")

    # Set webhook before starting Flask
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(set_webhook())

    # Start Flask App
    app.run(host="0.0.0.0", port=5000)

