
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from deep_translator import GoogleTranslator

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
logging.basicConfig(level=logging.INFO)

# Αποθήκευση κειμένων προσωρινά σε dictionary
message_store = {}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Το bot είναι έτοιμο!")

# Όταν γίνεται post στο κανάλι
async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.channel_post.text
    if not text:
        return

    message_id = update.channel_post.message_id
    message_store[str(message_id)] = text

    keyboard = [[InlineKeyboardButton("🌍 Translate to English", callback_data=f"translate|{message_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Απαντά χωρίς κείμενο — μόνο κουμπί
    await context.bot.send_message(
    chat_id=update.channel_post.chat_id,
    text="🔹",
    reply_markup=reply_markup
    )


# Όταν πατηθεί το κουμπί
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("translate|"):
        msg_id = data.split("|", 1)[1]
        original_text = message_store.get(msg_id, "[Μήνυμα δεν βρέθηκε]")

        translated = GoogleTranslator(source='auto', target='en').translate(original_text)

        try:
            await context.bot.send_message(
                chat_id=query.from_user.id,
                text=f"🇬🇧 Translation:\n{translated}"
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
