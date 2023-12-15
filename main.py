import logging
import telebot
from telebot import types
import create
import config
import models

TOKEN = '5973304457:AAHGtaBx2VladoA7yt1S5H3IV7KDJoVD7z4'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    if models.User.select().where(models.User.user_id == message.from_user.id).exists():
        bot.send_message(message.chat.id, "Вы уже участвуете в лотерее")
        return
    check = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Проверить подписку", callback_data="check")
    check.add(button)
    channels = create.channels_list(config.data['channel'])
    bot.send_message(message.chat.id,
                     f"Привет, {message.from_user.first_name}! Добро пожаловать в нашу лотерею", parse_mode='Markdown'
                     )
    bot.send_message(message.chat.id,
                     f"Для участия в лотерее тебе нужно быть подписанным на следующие каналы:\n{channels}",
                     parse_mode='HTML',
                     reply_markup=check
                     )


def is_user_subscribed(user_id) -> bool:
    channel_username = "@puton4ick"
    try:
        chat_member = bot.get_chat_member(channel_username, user_id)
        if chat_member.status == 'member' or chat_member.status == 'administrator' or chat_member.status == 'creator':
            print(chat_member.user.first_name)
            return True
        else:
            return False
    except telebot.apihelper.ApiTelegramException as e:
        logging.error(e)


@bot.message_handler(content_types=['text'])
def text_process(message: telebot.types.Message):
    print(message.html_text)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: types.CallbackQuery):
    if call.data == "check":
        if is_user_subscribed(call.from_user.id) == True:
            # Написал, стартовое сообщение при /start, чуток говнокод, нужно будет дописать запись в бд
            models.db.connect()
            models.User.create(user_id=call.from_user.id, nickname=call.from_user.username)
            models.db.close()
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
            bot.send_message(call.message.chat.id, "Поздравляем! Вы стали участником лотереи!")
        else:
            bot.send_message(call.message.chat.id, "Подпишитесь на канал и попробуйте снова")


bot.polling(none_stop=True)
