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


@bot.message_handler(commands=['auth'])
def auth(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0]:
        params = list(message.text.split())
        admin_info = config.get_admin_info(user_username, user_id)
        print(params)
        if '--help' in params:
            bot.send_message(chat_id=chat_id,
                             text=create.auth_info(),
                             parse_mode='HTML')
        else:
            name = str()
            if '-n' in params:
                param_index = params.index('-n')
                for i in range(param_index + 1, len(params)):
                    name += f'{params[i]} '

                if len(name) != 0:
                    name = name[:-1]
                    config.update_admin(user_username, user_id, name, admin_info[3])
                    text = '<b>Успешно:</b> username, id и name обновлены'
                else:
                    text = '<b>Ошибка:</b> не указано имя после параметра -n)'

            else:
                config.update_admin(user_username, user_id, admin_info[2], admin_info[3])
                text = '<b>Успешно:</b> username и id обновлены'

            bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode='HTML')
@bot.message_handler(commands=['addAdmin'])
def addAdmin(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id


@bot.message_handler(content_types=['text'])
def text_process(message: telebot.types.Message):
    print(config.data)


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
