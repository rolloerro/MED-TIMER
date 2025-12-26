import logging
from datetime import datetime, timedelta

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ===================== НАСТРОЙКИ =====================

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Временное хранилище (MVP)
user_timers = {}

# ===================== КНОПКИ =====================

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏰ Добавить приём", callback_data="add")],
        [InlineKeyboardButton("📋 Мои напоминания", callback_data="list")],
        [InlineKeyboardButton("❌ Очистить", callback_data="clear")]
    ])

# ===================== ХЭНДЛЕРЫ =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💊 *MED-TIMER*\n\n"
        "Я помогу не забывать принимать лекарства.\n\n"
        "Выберите действие 👇",
        reply_markup=main_keyboard(),
        parse_mode="Markdown"
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id

    if query.data == "add":
        await query.edit_message_text(
            "✍️ Напиши в формате:\n\n"
            "`название лекарства; минуты`\n\n"
            "Пример:\n`Аспирин;30`",
            parse_mode="Markdown"
        )

    elif query.data == "list":
        meds = user_timers.get(chat_id, [])
        if not meds:
            text = "📭 У тебя пока нет напоминаний."
        else:
            text = "📋 Твои напоминания:\n" + "\n".join(
                f"• {m['name']} через {m['minutes']} мин." for m in meds
            )
        await query.edit_message_text(text)

    elif query.data == "clear":
        user_timers.pop(chat_id, None)
        await query.edit_message_text("🧹 Все напоминания удалены.")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text

    if ";" not in text:
        await update.message.reply_text("❗ Формат: *название;минуты*", parse_mode="Markdown")
        return

    name, minutes = text.split(";", 1)

    try:
        minutes = int(minutes.strip())
    except ValueError:
        await update.message.reply_text("⛔ Введите количество минут числом.")
        return

    reminder_time = datetime.now() + timedelta(minutes=minutes)

    user_timers.setdefault(chat_id, []).append({
        "name": name.strip(),
        "minutes": minutes
    })

    await update.message.reply_text(
        f"✅ Напоминание добавлено!\n"
        f"💊 {name.strip()}\n"
        f"⏰ Через {minutes} мин."
    )

    # таймер
    context.job_queue.run_once(
        send_reminder,
        when=minutes * 60,
        chat_id=chat_id,
        data=name.strip()
    )


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=f"⏰ Пора принять: *{context.job.data}*",
        parse_mode="Markdown"
    )


# ===================== ЗАПУСК =====================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("🚀 MED-TIMER запущен")
    app.run_polling()


if __name__ == "__main__":
    main()
