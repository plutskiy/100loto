import logging
import telebot
from telebot import types

TOKEN = '5973304457:AAHGtaBx2VladoA7yt1S5H3IV7KDJoVD7z4'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    check = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Проверить подписку", callback_data="check")
    check.add(button)
    channel_username = "@puton4ick"
    bot.send_message(message.chat.id,
                     f"Привет, {message.from_user.first_name}! Добро пожаловать в нашу лотерею", parse_mode='Markdown'
                     )
    bot.send_message(message.chat.id,
                     f"Для участия в лотерее тебе нужно быть подписанным на следующие каналы:\n{channel_username}",
                     parse_mode='MarkdownV2',
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


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "check":
        if is_user_subscribed(call.from_user.id) == True:
            #Написал, стартовое сообщение при /start, чуток говнокод, нужно будет дописать запись в бд
            bot.send_message(call.message.chat.id, "Вы подписаны на канал")
        else:
            bot.send_message(call.message.chat.id, "Подпишитесь на канал и попробуйте снова")


bot.polling(none_stop=True)
