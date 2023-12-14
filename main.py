import logging
import telebot

TOKEN = '5973304457:AAHGtaBx2VladoA7yt1S5H3IV7KDJoVD7z4'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет, я бот, который проверяет подписку на канал")
    bot.send_message(message.chat.id, "Для проверки подписки отправьте мне команду /check")

@bot.message_handler(commands=['check'])
def is_user_subscribed(message):
    user_id = message.from_user.id
    channel_username = "@newcsgo"
    try:
        chat_member = bot.get_chat_member(channel_username, user_id)
        if chat_member.status == 'member' or chat_member.status == 'administrator' or chat_member.status == 'creator':
            bot.send_message(user_id, "Вы подписаны на канал")
        else:
            bot.send_message(user_id, "Вы не подписаны на канал")
    except telebot.apihelper.ApiTelegramException as e:
        logging.error(e)


bot.polling(none_stop=True)
