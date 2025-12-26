import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# -------- handlers --------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ Добавить приём", callback_data="add")],
        [InlineKeyboardButton("📋 Мои приёмы", callback_data="list")],
        [InlineKeyboardButton("✅ Отметить приём", callback_data="done")]
    ]
    await update.message.reply_text(
        "💊 MED-TIMER\nВыберите действие:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "add":
        await query.edit_message_text("🕒 Функция добавления приёма (в разработке)")
    elif query.data == "list":
        await query.edit_message_text("📋 Пока список пуст")
    elif query.data == "done":
        await query.edit_message_text("✅ Отмечено!")

# -------- запуск --------

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    print("🚀 MED-TIMER запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
