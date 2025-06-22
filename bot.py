import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

# ✅ Настройка логов
logging.basicConfig(level=logging.INFO)

# ✅ Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"📩 Получен апдейт от {update.effective_user.id}")
    await update.message.reply_text("✅ Бот работает! Всё ок.")

# 🚀 Запуск
if __name__ == "__main__":
    load_dotenv()

    TOKEN = os.environ.get("BOT_TOKEN")
    RENDER_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    PORT = int(os.environ.get("PORT", 8443))

    if not TOKEN or not RENDER_HOSTNAME:
        raise ValueError("BOT_TOKEN или RENDER_EXTERNAL_HOSTNAME не установлены.")

    logging.info(f"🌐 Запуск бота на https://{RENDER_HOSTNAME}/webhook, порт {PORT}")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"https://{RENDER_HOSTNAME}/webhook"
    )