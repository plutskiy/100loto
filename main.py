import logging
import telebot
from telebot import types
import create
import config
import models

TOKEN = '5973304457:AAHGtaBx2VladoA7yt1S5H3IV7KDJoVD7z4'
bot = telebot.TeleBot(TOKEN)
stop = True

@bot.message_handler(commands=['ref'])
def send_referral_link(message):
    user_id = message.from_user.id
    referral_link = f"https://t.me/test22832131bot?start={user_id}"
    bot.send_message(user_id, f"Ваша реферальная ссылка: {referral_link}")

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    referral_id = message.text[7:]  # Получаем user_id реферера из команды /start

    if models.User.select().where(models.User.user_id == user_id).exists():
        bot.send_message(message.chat.id, "Вы уже участвуете в лотерее")
        return
    if referral_id != "":
        if models.User.select().where(models.User.user_id == referral_id).exists():
            models.Ref.create(invite_id=referral_id, join_id=user_id)
        else:
            bot.send_message(message.chat.id, "Вы ввели неверный реферальный код")
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

@bot.message_handler(commands=['reset'])
def drop(message):
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0]:
        models.clear()
        bot.send_message(message.chat.id, "Все пользователи были удалены")


@bot.message_handler(commands=['reset_tickets'])
def drop(message):
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0]:
        models.db.connect()
        for user in models.User.select():
            user.tikets = 0
            user.save()
        for user in models.Ref.select():
            user.msg_count = 0
            user.save()
        models.db.drop_tables([models.Tickets])
        models.db.close()
        bot.send_message(message.chat.id, "Все билеты были удалены")

@bot.message_handler(commands=['stop'])
def stop(message):
    global stop
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0]:
        stop = True
        bot.send_message(message.chat.id, "Лотерея остановлена")

@bot.message_handler(commands=['start_lottery'])
def start(message):
    global stop
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0]:
        stop = False
        bot.send_message(message.chat.id, "Лотерея запущена")

@bot.message_handler(commands=['tickets'])
def tickets(message):
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0] and len(message.text.split()) == 2:
        params = list(message.text.split())
        if len(params) == 2:
            try:
                models.db.connect()
                user = models.User.get(models.User.user_id == params[1])
                bot.send_message(message.chat.id, f"У пользователя {params[1]} {user.tikets} билетов")
                models.db.close()
            except:
                bot.send_message(message.chat.id, "Пользователь не найден")
        else:
            bot.send_message(message.chat.id, "Неверный формат команды")
    else:
        models.db.connect()
        user = models.User.get(models.User.user_id == user_id)
        bot.send_message(message.chat.id, f"У Вас {user.tikets} билетов")
        models.db.close()

@bot.message_handler(commands=['delete'])
def delete(message):
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0]:
        params = list(message.text.split())
        if len(params) == 2:
                try:
                    models.db.connect()
                    user = models.User.get(models.User.nickname == params[1])
                    bot.send_message(user.user_id, "Ваш аккаунт был удален")
                    models.Tickets.delete().where(models.Tickets.user == user).execute()
                    models.Ref.delete().where((models.Ref.invite_id == user) | (models.Ref.join_id == user)).execute()
                    user.delete_instance()
                    models.db.close()
                    bot.send_message(message.chat.id, f"Пользователь {params[1]} был удален")
                except:
                    bot.send_message(message.chat.id, "Пользователь не найден")
        else:
            bot.send_message(message.chat.id, "Неверный формат команды")

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


@bot.message_handler(func=lambda message: True)
def count_messages(message):
    global stop
    user_id = message.from_user.id
    if not stop:
        if len(message.text.split()) >= 3:
            models.db.connect()
            if models.User.select().where(models.User.user_id == user_id).exists():
                user = models.User.get(models.User.user_id == user_id)
                user.tikets += 1
                user.save()
                ticket = models.Tickets.create(user=user)
                print(f"Ticket {ticket.id} created for user {user_id}")
                if models.Ref.select().where(models.Ref.join_id == user_id).exists():
                    ref = models.Ref.get(models.Ref.join_id == user_id)
                    if ref.msg_count + 1 == 5:
                        joined_user = models.User.get(models.User.user_id == user_id)
                        joined_user.tikets += 5
                        joined_user.save()

                        for _ in range(5):
                            models.Tickets.create(user=joined_user)

                        bot.send_message(joined_user.user_id, "Поздравляем! Вы получили 5 билетов!")

                        invited_user = models.User.get(models.User.user_id == ref.invite_id)
                        invited_user.tikets += 5
                        invited_user.save()

                        for _ in range(5):
                            models.Tickets.create(user=invited_user)

                        bot.send_message(invited_user.user_id, "Поздравляем! Вы получили 5 билетов!")

                        ref.delete_instance()
                    ref.msg_count += 1
                    ref.save()
            models.db.close()


bot.polling(none_stop=True)
