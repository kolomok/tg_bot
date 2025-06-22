import os
import logging
import asyncio
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔧 Настройка логов
logging.basicConfig(level=logging.INFO)

# 📩 Ответ на /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"📨 Пришёл апдейт от {update.effective_user.id}")
    await update.message.reply_text("✅ Бот живой! Webhook работает.")

# 🚀 Основной запуск
async def main():
    load_dotenv()

    TOKEN = os.environ.get("BOT_TOKEN")
    HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    PORT = int(os.environ.get("PORT", 8443))

    if not TOKEN or not HOSTNAME:
        raise ValueError("❌ BOT_TOKEN или RENDER_EXTERNAL_HOSTNAME не установлены")

    WEBHOOK_URL = f"https://{HOSTNAME}/webhook"
    logging.info(f"🌐 Webhook URL будет: {WEBHOOK_URL}")

    # 🔗 Устанавливаем webhook в Telegram
    set_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}"
    r = requests.get(set_url)
    if not r.ok:
        raise RuntimeError(f"❌ Не удалось установить webhook: {r.text}")
    logging.info("✅ Webhook успешно установлен")

    # ⚙️ Сборка и запуск
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    asyncio.run(main())