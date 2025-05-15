
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from deep_translator import GoogleTranslator

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Το bot είναι έτοιμο!")

# Όταν ποστάρεις κάτι στο κανάλι, απλά προσθέτει κουμπί "Translate" χωρίς να επαναλαμβάνει το μήνυμα
async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.channel_post.text
    if not text:
        return

    keyboard = [[InlineKeyboardButton("🌍 Translate to English", callback_data=f"translate|{text}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.channel_post.reply_text(" ", reply_markup=reply_markup)

# Όταν ο χρήστης πατήσει το κουμπί, λαμβάνει τη μετάφραση ΙΔΙΩΤΙΚΑ
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("translate|"):
        original_text = data.split("|", 1)[1]
        translated = GoogleTranslator(source='auto', target='en').translate(original_text)

        try:
            await context.bot.send_message(
                chat_id=query.from_user.id,
                text=f"🇬🇧 Translation:\{translated}"
            )
        except:
            await query.message.reply_text("❌ Δεν μπορώ να σου στείλω ιδιωτικά μήνυμα. Ξεκίνα το bot πρώτα με /start.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, handle_channel_post))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()
