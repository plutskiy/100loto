import logging
import random
from peewee import *

import telebot
from telebot import types
import create
import config
import models

TOKEN = '5973304457:AAHGtaBx2VladoA7yt1S5H3IV7KDJoVD7z4'
bot = telebot.TeleBot(TOKEN)
stop = True
group_chats_ids = [-10021431471, -1002143147104]

@bot.message_handler(commands=['ref'])
def send_referral_link(message):
    user_id = message.from_user.id
    referral_link = f"https://t.me/test22832131bot?start={user_id}"
    bot.send_message(user_id, f"Ваша реферальная ссылка: {referral_link}")


@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type != 'private':
        return

    user_id = message.from_user.id
    referral_id = message.text[7:]  # Получаем user_id реферера из команды /start

    if models.Ref.select().where(models.Ref.join_id == user_id).exists():
        bot.send_message(message.chat.id, 'Вы уже присоеденились по реферальной ссылке')
        return
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
    if message.chat.type != 'private':
        return
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0]:
        models.clear()
        bot.send_message(-1002143147104, "Лотерея была сброшена")


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

@bot.message_handler(commands=['stop'])
def stop(message):
    if message.chat.type != 'private':
        return
    global stop
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0]:
        stop = True
        # for chat_id in group_chats_ids:
        #     bot.send_message(chat_id, "Лотерея остановлена")

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
        # for chat_id in group_chats_ids:
        #     bot.send_message(chat_id, "Лотерея запущена")


@bot.message_handler(commands=['tickets'])
def tickets(message):
    if message.chat.type != 'private':
        return
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
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
                models.db.connect()
                user_to_delete = models.User.get(models.User.nickname == params[1])
                user_to_delete.delete_instance(recursive=True)

                # Create a temporary table
                models.db.execute_sql('CREATE TABLE temp AS SELECT * FROM tickets')

                # Delete the original table
                models.db.execute_sql('DROP TABLE tickets')

                # Recreate the original table without data
                models.Tickets.create_table()

                # Copy the data from the temporary table to the original table
                # The ticket_id will be reassigned automatically in ascending order
                models.db.execute_sql('INSERT INTO tickets SELECT * FROM temp')

                # Delete the temporary table
                models.db.execute_sql('DROP TABLE temp')

                models.db.close()
                bot.send_message(message.chat.id, f"Пользователь {params[1]} был удален")
                bot.send_message(user_to_delete.user_id, f"Вы удалены из лотереи")
            except:
                bot.send_message(message.chat.id, "Пользователь не найден")
        else:
            bot.send_message(message.chat.id, "Неверный формат команды")


@bot.message_handler(commands=['lottery'])
def lottery(message):
    if message.chat.type != 'private':
        return
    user_id = message.from_user.id
    user_username = message.from_user.username
    verification = config.is_admin(user_username, user_id)
    if verification[0]:
        models.db.connect()
        total_tickets = models.Tickets.select().count()
        winners = set()
        while len(winners) < 2:
            ticket_number = random.randint(1, total_tickets)
            winners.add(ticket_number)
        winner_tickets = [models.Tickets.get(models.Tickets.id == winner) for winner in winners]
        winner_users = [ticket.user for ticket in winner_tickets]
        winner_usernames = [user.nickname for user in winner_users]
        bot.send_message(message.chat.id, f"The winners are: {', '.join(winner_usernames)}")
        models.db.close()
    else:
        bot.send_message(message.chat.id, "You do not have permission to execute this command.")


def is_user_subscribed(user_id) -> bool:
    channel_username = "@puton4ick"
    try:
        chat_member = bot.get_chat_member(channel_username, user_id)
        if chat_member.status == 'member' or chat_member.status == 'administrator' or chat_member.status == 'creator':
            return True
        else:
            return False
    except telebot.apihelper.ApiTelegramException as e:
        logging.error(e)


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
            if parts[0][0] != '@':
                bot.send_message(chat_id=chat_id,
                                 text='<b>Ошибка:</b> username введен некорректно или отсутствует',
                                 parse_mode='HTML')
            else:
                params = ['-n', '-m']
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

                if len(name) == 0 and '-n' in parts:
                    bot.send_message(chat_id=chat_id,
                                     text='<b>Ошибка:</b> не указано имя после флага -n',
                                     parse_mode='HTML')
                else:
                    if len(name) != 0:
                        name = name[:-1]
                    else:
                        name = 'admin'
                    username = parts[0][1:]
                    is_added = config.add_admin(username, name, is_main)

                    if is_added:
                        bot.send_message(chat_id=chat_id,
                                         text=create.add_admin_text(username, name, is_main),
                                         parse_mode='HTML')
                    else:
                        bot.send_message(chat_id=chat_id,
                                         text=f'<b>Администратор</b> @{username} <b>уже записан в системе</b>',
                                         parse_mode='HTML')

    elif verification[0]:
        bot.send_message(chat_id=chat_id,
                         text='<b>permission denied</b>',
                         parse_mode='HTML')


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
                admin_info = config.get_admin_info(admin[1:], -2)
                is_deleted = config.del_admin(admin[1:])

                if is_deleted:
                    bot.send_message(chat_id=chat_id,
                                     text=create.del_admin_text(admin_info),
                                     parse_mode='HTML')
                else:
                    bot.send_message(chat_id=chat_id,
                                     text=f'<b>Пользователь</b> {admin} <b>не является администратором</b>',
                                     parse_mode='HTML')
    elif verification[0]:
        bot.send_message(chat_id=chat_id,
                         text='<b>permission denied</b>',
                         parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: types.CallbackQuery):
    if call.data == "check":
        if not models.User.select().where(models.User.user_id == call.from_user.id).exists():
            if is_user_subscribed(call.from_user.id) == True:
                try:
                    models.db.connect()
                    models.User.create(user_id=call.from_user.id, nickname=call.from_user.username)
                    models.db.close()
                    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
                    bot.send_message(call.message.chat.id, "Поздравляем! Вы стали участником лотереи!")
                except:
                    print("Юзер еблан, пускай на кнопку не спамит")
            else:
                bot.send_message(call.message.chat.id, "Подпишитесь на канал и попробуйте снова")


@bot.message_handler(func=lambda message: True)
def count_messages(message : types.Message):
    # if message.chat.type != 'public':
    #     return
    global stop
    user_id = message.from_user.id
    print(message.chat.id)
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
