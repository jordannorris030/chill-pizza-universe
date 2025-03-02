import os
import logging
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

# === Configuration ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://chill-pizza-universe.onrender.com")
SHEET_NAME = "PizzaGamingData"
GAME_URL = "https://jordannorris030.github.io/ChillPizzaGame/"  # ✅ Update with your game URL

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

# === Initialize Telegram Bot Application ===
application = Application.builder().token(BOT_TOKEN).build()

async def initialize_application():
    """Ensures the bot application is fully initialized before processing updates."""
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(f"{WEBHOOK_URL}/{BOT_TOKEN}")  # ✅ Set Webhook Here
    logging.info(f"✅ Telegram Bot Application Initialized & Webhook Set: {WEBHOOK_URL}/{BOT_TOKEN}")

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    """Processes incoming Telegram updates from Telegram Webhook."""
    try:
        update = Update.de_json(request.get_json(), application.bot)
        await application.process_update(update)  # ✅ Now processes update properly
        return "OK", 200
    except Exception as e:
        logging.error(f"⚠️ Webhook processing error: {e}")
        return "Error", 500

# === Telegram Bot Commands ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    keyboard = [[InlineKeyboardButton("🎮 Play Game", callback_data="play_game")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🍕 Welcome to ChillPizza! Tap below to play!", reply_markup=reply_markup)

async def launch_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Launches the HTML5 game inside Telegram."""
    game_url = "https://jordannorris030.github.io/chill-pizza-universe/"  # Ensure this is correct

    keyboard = [[InlineKeyboardButton("🎮 Play Game", url=game_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("🎮 Tap below to start playing ChillPizza!", reply_markup=reply_markup)

application.add_handler(CommandHandler("game", launch_game))

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button clicks (including Play Game button)."""
    query = update.callback_query
    if query.data == "play_game":
        await launch_game(update, context)

# === Register Commands & Handlers ===
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("game", launch_game))
application.add_handler(CommandHandler("play", launch_game))  # Alias for /game
application.add_handler(CommandHandler("menu", start))  # Alias to return to menu
application.add_handler(CommandHandler("help", start))  # Temporary help command

# === Basic Home Route to Confirm Flask is Running ===
@app.route("/", methods=["GET"])
def home():
    return "🚀 ChillPizza Backend is Live!", 200

# === Start Bot Properly ===
if __name__ == "__main__":
    logging.info("🚀 Starting ChillPizza Bot Backend...")

    loop = asyncio.new_event_loop()  # ✅ Create a new event loop
    asyncio.set_event_loop(loop)
    loop.run_until_complete(initialize_application())  # ✅ Run the setup process

    # Start Flask App
    app.run(host="0.0.0.0", port=5000)




