import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")

user_scan_times = {}

def get_airtable_record(country):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}

    today = datetime.utcnow().strftime("%-m/%-d/%Y") if os.name != "nt" else datetime.utcnow().strftime("%#m/%#d/%Y")
    formula = f"AND(country = '{country}', date = DATETIME_PARSE('{today}', 'M/D/YYYY'))"
    params = {"filterByFormula": formula}

    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    print("DEBUG FILTERED AIRTABLE:", data)

    if "records" in data and data["records"]:
        return data["records"][0]["fields"]
    return {}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fields = get_airtable_record("Germany")
    photo = fields.get("Photo", [None])[0]['url'] if "Photo" in fields else None
    text = fields.get("intro_text", "Welcome to the bot!")
    button_text = fields.get("intro_button_text", "🚀 Tap START to access group and activate bot")

    keyboard = [[InlineKeyboardButton(button_text, callback_data="start_bot")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if photo:
        await update.message.reply_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")

# Μετά το START κουμπί
async def start_bot_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass

    fields = get_airtable_record("Germany")
    after_start_photo = fields.get("after_start_photo", [None])[0]['url'] if "after_start_photo" in fields else None

    keyboard = [[
        InlineKeyboardButton("📢 Μπες στο κανάλι μας", url="https://t.me/+Idg13sBc6IthNmFk"),
        InlineKeyboardButton("🤖 Ξεκίνα το AI Bot", callback_data="activate_ai")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if after_start_photo:
        await query.message.reply_photo(photo=after_start_photo, caption=".", reply_markup=reply_markup, parse_mode="HTML")
    else:
        await query.message.reply_text("👇Διάλεξε πως θες να προχωρήσεις!", reply_markup=reply_markup, parse_mode="HTML")

# Ξεκινάει το AI Bot
async def activate_ai_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    fields = get_airtable_record("Germany")
    photo = fields.get("after_start_photo", [None])[0]['url'] if "after_start_photo" in fields else None
    text = fields.get("main_text", "Here's your feed for today.")

    keyboard = [[InlineKeyboardButton("🔗 ΞΕΚΙΝΑ", callback_data="connect")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if photo:
        await query.message.reply_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await query.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")

# Επιλογή χώρας (2 ανά σειρά)
async def connect_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    countries = [
        ("🇬🇷 Greece", "Greece"),
        ("🇦🇱 Albania", "Albania"),
        ("🇩🇪 Germany", "Germany"),
        ("🇬🇧 United Kingdom", "United Kingdom"),
        ("🇪🇸 Spain", "Spain"),
        ("🇮🇹 Italy", "Italy"),
        ("🇵🇱 Poland", "Poland"),
        ("🇨🇭 Switzerland", "Switzerland"),
        ("🇫🇷 France", "France"),
        ("🇸🇪 Sweden", "Sweden"),
        ("🇫🇮 Finland", "Finland"),
        ("🇳🇴 Norway", "Norway"),
        ("🇮🇸 Iceland", "Iceland"),
        ("🇦🇹 Austria", "Austria"),
        ("🇳🇱 Netherlands", "Netherlands")
    ]

    keyboard = [
        [
            InlineKeyboardButton(countries[i][0], callback_data=f"scan_{countries[i][1]}"),
            InlineKeyboardButton(countries[i+1][0], callback_data=f"scan_{countries[i+1][1]}")
        ]
        for i in range(0, len(countries) - 1, 2)
    ]
    if len(countries) % 2 == 1:
        keyboard.append([
            InlineKeyboardButton(countries[-1][0], callback_data=f"scan_{countries[-1][1]}")
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("🌍 <b>SELECT COUNTRY TO SCAN:</b>", reply_markup=reply_markup, parse_mode="HTML")

# Σκανάρισμα
async def scan_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    country = query.data.split("_")[1]
    user_id = query.from_user.id

    user_scan_times[user_id] = datetime.utcnow()

    fields = get_airtable_record(country)
    msg = fields.get("scan_message", "Act fast before the glitch is gone.")
    final = fields.get("scan_final_text", "SCAN READY ✅")
    scan_photo = fields.get("scan_photo", [None])[0]['url'] if "scan_photo" in fields else None

    if scan_photo:
        await query.message.reply_photo(photo=scan_photo, caption=msg, parse_mode="HTML")
    else:
        await query.message.reply_text(msg, parse_mode="HTML")

    await query.message.reply_text(final, parse_mode="HTML")

    keyboard = [[InlineKeyboardButton("🔁 SCAN AGAIN", callback_data="connect")]]
    await query.message.reply_text("Ready to scan again?", reply_markup=InlineKeyboardMarkup(keyboard))

# Εκκίνηση bot
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(start_bot_callback, pattern="^start_bot$"))
app.add_handler(CallbackQueryHandler(activate_ai_callback, pattern="^activate_ai$"))
app.add_handler(CallbackQueryHandler(connect_callback, pattern="^connect$"))
app.add_handler(CallbackQueryHandler(scan_country, pattern="^scan_"))

if __name__ == "__main__":
    app.run_polling()
