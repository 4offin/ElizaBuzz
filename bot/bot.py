# bot.py
import logging
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from moodle_client import MoodleClient
from config import TOKEN  # Конфиденциальные данные загружаются из отдельного файла

# Этапы диалога
USERNAME, PASSWORD = range(2)

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Добро пожаловать!\nПожалуйста, введите ваш логин для Moodle:")
    return USERNAME

def username_handler(update: Update, context: CallbackContext) -> int:
    username = update.message.text.strip()
    context.user_data['username'] = username
    update.message.reply_text("Введите ваш пароль для Moodle:")
    return PASSWORD

def password_handler(update: Update, context: CallbackContext) -> int:
    password = update.message.text.strip()
    username = context.user_data.get('username')
    client = MoodleClient(username, password)
    try:
        client.login()
        grades = client.get_grades()
        if grades:
            response_text = "Ваши оценки:\n" + "\n".join(f"{course}: {grade}" for course, grade in grades)
        else:
            response_text = "Оценки не найдены или произошла ошибка при получении данных."
    except Exception as e:
        response_text = f"Ошибка: {e}"
    update.message.reply_text(response_text)
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

def main():
    # Настройка логирования
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Обработчик диалога для авторизации
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            USERNAME: [MessageHandler(Filters.text & ~Filters.command, username_handler)],
            PASSWORD: [MessageHandler(Filters.text & ~Filters.command, password_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
