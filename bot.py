from telegram import Update, ReplyKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from openpyxl import Workbook, load_workbook
import os
from dotenv import load_dotenv
import logging

# ✅ Логи
logging.basicConfig(level=logging.INFO)

# 📁 Папка для Excel
USER_DATA_DIR = "user_excels"
os.makedirs(USER_DATA_DIR, exist_ok=True)

def get_excel_path(user_id: int) -> str:
    filename = f"{user_id}.xlsx"
    return os.path.join(USER_DATA_DIR, filename)

def init_excel(file_path: str):
    if not os.path.exists(file_path):
        wb = Workbook()
        ws = wb.active
        ws.append(["Товар", "Количество", "Цена/штука", "Цена/общая"])
        wb.save(file_path)

# 📤 Экспорт
async def export_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    file_path = get_excel_path(user_id)
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            await update.message.reply_document(document=InputFile(f, filename=os.path.basename(file_path)))
    else:
        await update.message.reply_text("Файл ещё не создан.")

# 🟢 /start
reply_keyboard = [["Добавить данные", "📤 Экспортировать файл"]]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"📩 Получен апдейт от {update.effective_user.id}")
    await update.message.reply_text("Привет! Я бот для Excel-записей.", reply_markup=markup)

# ➕ Ввод данных
async def prompt_for_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите: `Товар, Кол-во, Цена/шт, Общая`", parse_mode="Markdown")
    context.user_data["awaiting_data"] = True

# 📥 Обработка
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_data"):
        user_id = update.message.from_user.id
        file_path = get_excel_path(user_id)
        init_excel(file_path)
        try:
            parts = [p.strip() for p in update.message.text.split(",")]
            if len(parts) != 4:
                raise ValueError("Нужно 4 значения через запятую.")
            wb = load_workbook(file_path)
            ws = wb.active
            ws.append(parts)
            wb.save(file_path)
            await update.message.reply_text("✅ Сохранено.")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
        finally:
            context.user_data["awaiting_data"] = False
    else:
        await update.message.reply_text("Нажмите 'Добавить данные'.")

# 🚀 Запуск
load_dotenv()
TOKEN = os.environ.get("BOT_TOKEN")
RENDER_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
PORT = int(os.environ.get("PORT", 8443))

if not TOKEN or not RENDER_HOSTNAME:
    raise ValueError("BOT_TOKEN или RENDER_EXTERNAL_HOSTNAME не установлены.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("export", export_file))
app.add_handler(MessageHandler(filters.Text(["Добавить данные"]), prompt_for_data))
app.add_handler(MessageHandler(filters.Text(["📤 Экспортировать файл"]), export_file))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

logging.info(f"🌐 Старт бота: https://{RENDER_HOSTNAME}/webhook, порт {PORT}")

app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    webhook_url=f"https://{RENDER_HOSTNAME}/webhook"
)