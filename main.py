import logging
import random
from peewee import *

import telebot
from telebot import types
import create
import check
import config
import models
import threading
import schedule
import time
from backup import backup_db


# Функция для резервного копирования базы данных
def job():
    backup_db("users")


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


schedule.every(1).hour.do(job)

schedule_thread = threading.Thread(target=run_schedule)
schedule_thread.start()

# Токен бота
TOKEN = '5973304457:AAHGtaBx2VladoA7yt1S5H3IV7KDJoVD7z4'
bot = telebot.TeleBot(TOKEN)
stop = True
# Создание таблиц в базе данных
models.db.create_tables([models.Ref], safe=True)
models.db.create_tables([models.Tickets], safe=True)
models.db.create_tables([models.User], safe=True)
data = config.update()


# Функция для обработки склонения слов
def declension(n, forms):
    n = abs(n) % 100
    n1 = n % 10
    if 5 <= n <= 20:
        return forms[2]
    elif n1 == 1:
        return forms[0]
    elif 2 <= n1 <= 4:
        return forms[1]
    else:
        return forms[2]


# Функция для создания пользовательской клавиатуры

def user_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Билеты", callback_data="tickets"))
    keyboard.add(types.InlineKeyboardButton(text="Реферальная ссылка", callback_data="ref"))
    keyboard.add(types.InlineKeyboardButton(text="ТОП 10 участников", callback_data="top"))
    return keyboard


# Команда бота для отправки реферальной ссылки
@bot.message_handler(commands=['ref'])
def send_referral_link(message):
    user_id = message.from_user.id
    referral_link = f"https://t.me/test22832131bot?start={user_id}"
    bot.send_message(user_id, f"Ваша реферальная ссылка: {referral_link}")


# Команда бота для запуска бота
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type != 'private':
        return
    word_forms_message = ['сообщение', 'сообщения', 'сообщений']
    word_forms_ticket = ['билет', 'билета', 'билетов']
    user_id = message.from_user.id
    referral_id = message.text[7:]
    verification = config.is_admin(message.from_user.username, user_id)
    if verification[0]:
        bot.send_message(user_id,
                         text='Добро пожаловать в админ панель',
                         parse_mode='HTML')
        bot.send_message(user_id,
                         text=create.help_info(),
                         parse_mode='HTML')
        return
    if models.User.select().where(models.User.user_id == user_id).archieved:
        bot.send_message(user_id, "Вы были удалены из лотереи и больше не можете ей пользоваться")
        return
    if models.Ref.select().where(models.Ref.join_id == user_id).exists():
        bot.send_message(message.chat.id, 'Вы уже присоеденились по реферальной ссылке')
        return
    if models.User.select().where(models.User.user_id == user_id).exists():
        bot.send_message(message.chat.id, "[      Меню      ]", reply_markup=user_keyboard())
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
    channels = create.channels_list(data['channel'])
    bot.send_message(message.chat.id,
                     f'''Привет, {message.from_user.first_name}! Добро пожаловать в нашу лотерею

За каждое сообщение в чатах учавствующих в лотерее более <b>{data['message']['needed_msg']}</b> {declension(data['message']['needed_msg'], word_forms_message)} вы получите <b>{data['ticket']['per_msg']}</b> {declension(data['ticket']['per_msg'], word_forms_ticket)}.

Если вы пригласите другого участника, и он напишет <b>{data['message']['ref_msg']}</b> {declension(data['message']['ref_msg'], word_forms_message)}, вы оба получите по <b>{data['ticket']['ref_msg']}</b> {declension(data['ticket']['ref_msg'], word_forms_ticket)}.''',
                     parse_mode='HTML'
                     )
    bot.send_message(message.chat.id,
                     f"Для участия в лотерее тебе нужно быть подписанным на следующие каналы:\n{channels}",
                     parse_mode='HTML',
                     reply_markup=check
                     )


# Команда бота для удаления чата из учавствующих в начислении билетов
@bot.message_handler(commands=['removechat'])
def remove_chat(message):
    if message.chat.type == 'private':
        return
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_username = message.from_user.username
    chat_title = message.chat.title
    verification = config.is_admin(user_username, user_id)
    if verification[0]:
        if config.remove_chat(chat_id):
            bot.send_message(user_id, f"Чат '{chat_title}' был успешно удалён из лотереи")
            global data
            data = config.update()  # Update the data variable
        else:
            bot.send_message(user_id, f"Чата {chat_title} нет в списке лотереи")


# Команда бота для добавления чата в учавствующих в начислении билетов
@bot.message_handler(commands=['addchat'])
def add_chat(message):
    if message.chat.type == 'private':
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    user_username = message.from_user.username
    chat_title = message.chat.title
    verification = config.is_admin(user_username, user_id)
    if verification[0]:
        if config.add_chat(chat_id):
            bot.send_message(user_id, f"Чат '{chat_title}' добавлен в лотерею")
            global data
            data = config.update()
        else:
            bot.send_message(user_id, f"Чат '{chat_title}' уже добавлен в лотерею")


# Команда бота для сброса всей лотереи
@bot.message_handler(commands=['reset'])
def drop(message):
    if message.chat.type != 'private':
        return
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0]:
        models.clear()
        bot.send_message(-1002143147104, "Лотерея была сброшена")


# Команда бота для сброса билетов
@bot.message_handler(commands=['reset_tickets'])
def drop(message):
    if message.chat.type != 'private':
        return
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
        models.db.create_tables([models.Tickets], safe=True)
        models.db.close()
        bot.send_message(message.chat.id, "Все билеты были удалены")


# Команда бота для остановки начисления билетов
@bot.message_handler(commands=['stop_lottery'])
def stop(message):
    if message.chat.type != 'private':
        return
    global stop
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0]:
        stop = True
        for chat_id in data['']:
            bot.send_message(chat_id, "Лотерея остановлена")


# Команда бота для запуска начисления билетов
@bot.message_handler(commands=['start_lottery'])
def start(message):
    if message.chat.type != 'private':
        return
    global stop
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0]:
        stop = False
        for chat_id in data['chan_id']:
            bot.send_message(chat_id, "Лотерея запущена")


# Команда бота для проверки билетов
@bot.message_handler(commands=['tickets'])
def tickets(message):
    if message.chat.type != 'private':
        return
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if models.User.select().where(models.User.user_id == user_id).archieved:
        bot.send_message(user_id, "Вы были удалены из лотереи и больше не можете ей пользоваться")
        return
    if verification[0] and len(message.text.split()) == 2:
        params = list(message.text.split())
        if len(params) == 2:
            try:
                models.db.connect()
                user = models.User.get(models.User.nickname == params[1])
                bot.send_message(message.chat.id, f"У пользователя {params[1]} {user.tikets} билетов")
                models.db.close()
            except:
                bot.send_message(message.chat.id, "Пользователь не найден")
        else:
            bot.send_message(message.chat.id, "Неверный формат команды")
    elif models.User.select().where(models.User.user_id == user_id).exists():
        models.db.connect()
        user = models.User.get(models.User.user_id == user_id)
        bot.send_message(message.chat.id, f"У Вас {user.tikets} билетов")
        models.db.close()
    elif not models.User.select().where(models.User.user_id == user_id).exists():
        bot.send_message(message.chat.id, "Вы не участвуете в лотерее")

@bot.message_handler(commands=['unban'])
def unban(message : types.Message):
    if message.chat.type != 'private':
        return
    params = list(message.text.split())
    if len(params) == 2:
        try:
            user = models.User.get(models.User.nickname == params[1])
            if user.archieved:
                user.archieved = False
                bot.send_message(message.chat.id, f"Этот пользователь {params[1]} успешно разбанен!")
            else:
                bot.send_message(message.chat.id, f"Этот пользователь {params[1]} не забанен!")
                bot.send_message(user.user_id, "Вы были разбанены!")
        except:
            bot.send_message(message.chat.id, "Пользователь не найден")
        else:
            bot.send_message(message.chat.id, "Неправильный формат команды!")


# Команда бота для удаления пользователя
@bot.message_handler(commands=['delete'])
def delete(message):
    if message.chat.type != 'private':
        return
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0]:
        params = list(message.text.split())
        if len(params) == 2:
            try:
                user = models.User.get(models.User.nickname == params[1])
                user.delete_instance(recursive=True)
                tickets = models.Tickets.select().order_by(models.Tickets.id)

                tickets_data = []
                for ticket in tickets:
                    ticket_data = ticket.__data__.copy()
                    del ticket_data['id']
                    tickets_data.append(ticket_data)

                models.Tickets.delete().execute()
                with models.db.atomic():
                    for i, ticket_data in enumerate(tickets_data, start=1):
                        models.Tickets.create(id=i, **ticket_data)
                models.User.create(user_id=user_id, archieved=True)
                bot.send_message(message.chat.id, f"Пользователь {params[1]} был удален")
                bot.send_message(user.user_id, f"Вы удалены из лотереи")
            except:
                bot.send_message(message.chat.id, "Пользователь не найден")
        else:
            bot.send_message(message.chat.id, "Неверный формат команды")


# Команда бота для выбора победителя
@bot.message_handler(commands=['winner'])
def lottery(message):
    if message.chat.type != 'private':
        return
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0]:
        total_tickets = models.Tickets.select().count()
        if total_tickets < 3:
            bot.send_message(message.chat.id, "Недостаточно билетов для проведения лотереи")
            return
        winners_nicknames = set()
        while len(winners_nicknames) < 3:
            winning_id = random.randint(1, total_tickets)
            winner_ticket = models.Tickets.get(models.Tickets.id == winning_id)
            winner_nickname = models.User.get(models.User.user_id == winner_ticket.user_id).nickname
            if winner_nickname not in winners_nicknames:
                winners_nicknames.add(winner_nickname)
        winners_text = ', @'.join(winners_nicknames)
        for chat_id in data['chan_id']:
            bot.send_message(chat_id, f"Победители лотереи: @{winners_text}")


# Функция для проверки подписки пользователя
def is_user_subscribed(user_id) -> dict:
    result = dict()
    for channel_nickname, channel_username in data['channel'].items():
        try:
            chat_member = bot.get_chat_member(f'@{channel_username}', user_id)
            if not (
                    chat_member.status == 'member' or chat_member.status == 'administrator' or chat_member.status == 'creator'):
                result[channel_nickname] = channel_username
        except telebot.apihelper.ApiTelegramException as e:
            logging.error(e)
    return result


# Команда бота для отображения списка команд
@bot.message_handler(commands=['help'])
def help(message: types.Message):
    if message.chat.type != 'private':
        return
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0]:
        bot.send_message(chat_id=chat_id,
                         text=create.help_info(),
                         parse_mode='HTML')


# Команда бота для аутентификации пользователя
@bot.message_handler(commands=['auth'])
def auth(message: types.Message):
    if message.chat.type != 'private':
        return
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
                    text = '<b>Ошибка:</b> не указано имя после флага -n'

            else:
                config.update_admin(user_username, user_id, admin_info[2], admin_info[3])
                text = '<b>Успешно:</b> username и id обновлены'

            bot.send_message(chat_id=chat_id,
                             text=text,
                             parse_mode='HTML')


# Команда бота для добавления админа
@bot.message_handler(commands=['addAdmin'])
def addAdmin(message: types.Message):
    if message.chat.type != 'private':
        return
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0] and verification[3]:
        parts = list(message.text.split())[1:]
        if '--help' in parts or not parts:
            bot.send_message(chat_id=chat_id,
                             text=create.addAdmin_info(),
                             parse_mode='HTML')
        elif parts:
            correct_username = check.check_telegram_link(parts[0])
            if not correct_username[0]:
                bot.send_message(chat_id=chat_id,
                                 text='<b>Ошибка:</b> username введен некорректно или отсутствует.\nИспользуйте /addAdmin --help</b>',
                                 parse_mode='HTML')
            else:
                parts[0] = correct_username[1]
                params = ['-n', '-m', '-s']
                name = ''
                is_main = False

                if '-m' in parts:
                    is_main = True

                if '-n' in parts:
                    param_index = parts.index('-n')
                    for i in range(param_index + 1, len(parts)):
                        if parts[i] in params:
                            break
                        name += f'{parts[i]} '

                if len(name) == 0 and '-n' in parts and not ('-s' in parts):
                    bot.send_message(chat_id=chat_id,
                                     text='<b>Ошибка:</b> не указано имя после флага -n',
                                     parse_mode='HTML')
                else:
                    if len(name) != 0:
                        name = name[:-1]
                    else:
                        name = 'admin'
                    username = parts[0]

                    if '-s' in parts:
                        is_s_par = True
                        is_added = False
                        is_setted = config.set_admin(username, name, is_main)
                    else:
                        is_s_par = False
                        is_added = config.add_admin(username, name, is_main)
                        is_setted = False

                    if is_s_par and is_setted:
                        bot.send_message(chat_id=chat_id,
                                         text=create.set_admin_text(username, name, is_main),
                                         parse_mode='HTML')
                    elif is_s_par and not is_setted:
                        bot.send_message(chat_id=chat_id,
                                         text=f'<b>Ошибка</b>: Пользователь @{username} не является администратором',
                                         parse_mode='HTML')
                    elif not is_s_par and is_added:
                        bot.send_message(chat_id=chat_id,
                                         text=create.add_admin_text(username, name, is_main),
                                         parse_mode='HTML')
                    elif not is_s_par and not is_added:
                        bot.send_message(chat_id=chat_id,
                                         text=f'<b>Ошибка</b>: Администратор @{username} уже записан в системе',
                                         parse_mode='HTML')


# Команда бота для удаления админа
@bot.message_handler(commands=['delAdmin'])
def delAdmin(message: types.Message):
    if message.chat.type != 'private':
        return
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0] and verification[3]:
        admins = list(message.text.split())[1:]
        if '--help' in admins or not admins:
            bot.send_message(chat_id=chat_id,
                             text=create.delAdmin_info(),
                             parse_mode='HTML')
        elif admins:
            for admin in admins:
                correct_username = check.check_telegram_link(admin)
                admin_info = config.get_admin_info(correct_username[1], -2)
                is_deleted = config.del_admin(correct_username[1])
                if correct_username[0]:
                    if is_deleted:
                        bot.send_message(chat_id=chat_id,
                                         text=create.del_admin_text(admin_info),
                                         parse_mode='HTML')
                    else:
                        bot.send_message(chat_id=chat_id,
                                         text=f'<b>Ошибка</b>: Пользователь {admin} не является администратором',
                                         parse_mode='HTML')
                else:
                    bot.send_message(chat_id=chat_id,
                                     text=f'<b>Ошибка</b>: username {correct_username[1]} введен некорректно.\nИспользуйте /delAdmin --help',
                                     parse_mode='HTML')

    elif verification[0]:
        bot.send_message(chat_id=chat_id,
                         text='<b>permission denied</b>',
                         parse_mode='HTML')


# Команда бота для установки конфигурации
@bot.message_handler(commands=['setCFG'])
def setCFG(message: types.Message):
    if message.chat.type != 'private':
        return
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0] and verification[3]:
        parts = list(message.text.split())[1:]
        if '--help' in parts or not parts:
            bot.send_message(chat_id=chat_id,
                             text=create.setCFG_info(),
                             parse_mode='HTML')
        elif parts:
            set_params = {
                '-x': config.data['message']['needed_msg'],
                '-y': config.data['message']['ref_msg'],
                '-t': config.data['ticket']['per_msg'],
                '-z': config.data['ticket']['ref_msg']
            }
            params = ['-x', '-y', '-t', '-z']

            for i in range(len(parts)):
                if parts[i] in params:
                    if i + 1 < len(parts) and not (parts[i + 1] in params):
                        try:
                            parts[i + 1] = int(parts[i + 1])
                            is_correct = True
                        except:
                            is_correct = False
                        if is_correct:
                            set_params[parts[i]] = parts[i + 1]

            set_params = tuple(set_params.values())
            config.set_config(set_params)
            bot.send_message(chat_id=chat_id,
                             text=create.CFG_tam_info(config.get_tam_info()),
                             parse_mode='HTML')

    elif verification[0]:
        bot.send_message(chat_id=chat_id,
                         text='<b>permission denied</b>',
                         parse_mode='HTML')


# Команда бота для добавления канала
@bot.message_handler(commands=['addChannel'])
def addChannel(message: types.Message):
    if message.chat.type != 'private':
        return
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0]:
        parts = list(message.text.split())[1:]
        if '--help' in parts or not parts:
            bot.send_message(chat_id=chat_id,
                             text=create.addChannel_info(),
                             parse_mode='HTML')
        elif parts:
            correct_username = check.check_telegram_link(parts[0])
            if not correct_username[0]:
                bot.send_message(chat_id=chat_id,
                                 text='<b>Ошибка:</b> username введен некорректно или отсутствует.\nИспользуйте /addChannel --help</b>',
                                 parse_mode='HTML')
            else:
                parts[0] = correct_username[1]
                params = ['-n', '-s']
                name = ''
                is_setted = False

                if '-n' in parts:
                    param_index = parts.index('-n')
                    for i in range(param_index + 1, len(parts)):
                        if parts[i] in params:
                            break
                        name += f'{parts[i]} '

                if len(name) == 0 and '-n' in parts and not ('-s' in parts):
                    bot.send_message(chat_id=chat_id,
                                     text='<b>Ошибка:</b> не указано имя после флага -n',
                                     parse_mode='HTML')
                else:
                    if len(name) != 0:
                        name = name[:-1]
                    else:
                        name = 'channel'
                    username = parts[0]

                    if '-s' in parts:
                        is_s_par = True
                        is_added = False
                        is_setted = config.set_channel(username, name)
                    else:
                        is_s_par = False
                        is_added = config.add_channel(username, name)
                        is_setted = False

                    if is_s_par and is_setted:
                        bot.send_message(chat_id=chat_id,
                                         text=create.set_channel_text(username, name),
                                         parse_mode='HTML')
                    elif is_s_par and not is_setted:
                        bot.send_message(chat_id=chat_id,
                                         text=f'<b>Ошибка</b>: Канал @{username} не является каналом лотереи',
                                         parse_mode='HTML')
                    elif not is_s_par and is_added:
                        bot.send_message(chat_id=chat_id,
                                         text=create.add_channel_text(username, name),
                                         parse_mode='HTML')


# Обратный вызов для встроенных запросов
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: types.CallbackQuery):
    if models.User.select().where(models.User.user_id == call.from_user.id).archieved:
        bot.send_message(call.from_user.id, "Вы были удалены из лотереи и больше не можете ей пользоваться")
        return
    if call.data == "check":
        if not models.User.select().where(models.User.user_id == call.from_user.id).exists():
            is_not_subscribed_channels = is_user_subscribed(call.from_user.id)
            if not is_not_subscribed_channels:
                try:
                    models.db.connect()
                    models.User.create(user_id=call.from_user.id, nickname=call.from_user.username)
                    models.db.close()
                    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
                    bot.send_message(call.message.chat.id, "Поздравляем! Вы стали участником лотереи!",
                                     reply_markup=user_keyboard())
                except:
                    print("Юзер еблан, пускай на кнопку не спамит")
            else:
                bot.send_message(call.message.chat.id,
                                 f"Вы не подписаны на следующие каналы:\n{create.channels_list(is_not_subscribed_channels)}",
                                 parse_mode='HTML')
    elif call.data == "tickets":
        models.db.connect()
        user = models.User.get(models.User.user_id == call.from_user.id)
        bot.send_message(call.message.chat.id, f"У Вас {user.tikets} билетов")
        models.db.close()
    elif call.data == "ref":
        referral_link = f"https://t.me/test22832131bot?start={call.from_user.id}"
        bot.send_message(call.message.chat.id, f"Ваша реферальная ссылка: {referral_link}")
    elif call.data == "top":
        models.db.connect()
        top = models.User.select().order_by(models.User.tikets.desc()).limit(10)
        text = "ТОП 10 участников:\n"
        for user in top:
            text += f"@{user.nickname} - {user.tikets}\n"
        bot.send_message(call.message.chat.id, text)
        models.db.close()


# Обработчик сообщений для начсиления тикетов
@bot.message_handler(func=lambda message: True)
def count_messages(message: types.Message):
    global stop
    user_id = message.from_user.id
    chat_id = message.chat.id
    if chat_id not in data['chan_id']:
        return
    if models.User.select().where(models.User.user_id == user_id).archieved:
        bot.send_message(user_id, "Вы были удалены из лотереи и больше не можете ей пользоваться")
        return
    if len(message.text.split()) >= 3:
        models.db.connect()
        if models.User.select().where(models.User.user_id == user_id).exists():
            if models.User.select().where(models.User.user_id == user_id).get().msg_count <= data['message'][
                'needed_msg']:
                models.User.update(msg_count=models.User.msg_count + 1).where(models.User.user_id == user_id).execute()
                models.db.close()
                return
    if not stop:
        if len(message.text.split()) >= 3:
            models.db.connect()
            if models.User.select().where(models.User.user_id == user_id).exists():
                if models.User.select().where(models.User.user_id == user_id).get().msg_count <= data['message'][
                    'needed_msg']:
                    models.User.update(msg_count=models.User.msg_count + 1).where(
                        models.User.user_id == user_id).execute()
                    models.db.close()
                    return
                user = models.User.get(models.User.user_id == user_id)
                user.tikets += data['ticket']['per_msg']
                user.save()
                for _ in range(data['ticket']['per_msg']):
                    tiket = models.Tickets.create(user=user)
                    print(f"Билет {tiket.id} создан для {user_id}")

                if models.Ref.select().where(models.Ref.join_id == user_id).exists():
                    ref = models.Ref.get(models.Ref.join_id == user_id)
                    if ref.msg_count + 1 == data["message"]['ref_msg']:
                        joined_user = models.User.get(models.User.user_id == user_id)
                        joined_user.tikets += data['ticket']['ref_msg']
                        joined_user.save()

                        for _ in range(data['ticket']['ref_msg']):
                            models.Tickets.create(user=joined_user)

                        bot.send_message(joined_user.user_id, "Поздравляем! Вы получили 5 билетов!")

                        invited_user = models.User.get(models.User.user_id == ref.invite_id)
                        invited_user.tikets += data['ticket']['ref_msg']
                        invited_user.save()

                        for _ in range(data['ticket']['ref_msg']):
                            models.Tickets.create(user=invited_user)

                        bot.send_message(invited_user.user_id, "Поздравляем! Вы получили 5 билетов!")

                        ref.delete_instance()
                    ref.msg_count += 1
                    ref.save()
            models.db.close()


bot.polling(none_stop=True)
