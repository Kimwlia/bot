
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from deep_translator import GoogleTranslator

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Το bot λειτουργεί! Κάνε post στο κανάλι για να δοκιμάσεις.")

# Όταν γίνεται νέο post στο κανάλι
async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.channel_post.text
    if not text:
        return

    keyboard = [[InlineKeyboardButton("🌍 Translate to English", callback_data=text)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.channel_post.chat_id,
        text=text,
        reply_markup=reply_markup,
        reply_to_message_id=update.channel_post.message_id
    )

# Όταν πατηθεί το κουμπί μετάφρασης
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    original_text = query.data
    translated = GoogleTranslator(source='auto', target='en').translate(original_text)

    await query.message.reply_text(f"🇬🇧 {translated}")

# Εκκίνηση του bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, handle_channel_post))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()
