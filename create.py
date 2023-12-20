def channels_list(channels: dict) -> str:
    text = str()
    i = 1
    for name, url in channels.items():
        text += f'{i}. <a href="https://t.me/{url}">{name}</a>'
        i += 1
    return text


def help_info() -> str:
    text = '<b>Админские команды:</b>\n\n'
    text += 'Настройки конфига:\n'
    text += '<b>/auth</b>\n'
    text += '<b>/addAdmin</b>\n'
    text += '<b>/delAdmin</b>\n'
    text += 'Для получения подробной информации о команде "/command" используйте параметр --help:\n'
    text += 'Пример:\n'
    text += '/auth --help\n'
    return text

def auth_info() -> str:
    text = 'Функция /auth обновляет Ваши id и username в системе, если они изменились или отсутствуют.\n\n'
    text += 'Флаги: \n'
    text += '<b>-n</b> - Изменить имя\n'
    text += 'Примеры:\n'
    text += '/auth -n Иван\n'
    text += '/auth -n Иван Иванов\n\n'
    text += '<b>--help</b> - Узнать информацию о команде\n'
    return text


def addAdmin_info() -> str:
    text = 'Функция /addAdmin добавляет администратора в систему по его username\n\n'
    text += 'Допустимый ввод username:\n'
    text += 'https://t.me/username\n'
    text += 't.me/username\n'
    text += '@username\n\n'
    text += 'Флаги: \n'
    text += '<b>-n</b> - Добавить имя\n'
    text += 'Если флаг не указан, то укажется имя "admin"\n'
    text += 'Примеры:\n'
    text += '/addAdmin @username -n Иван\n'
    text += '/addAdmin @username -n Иван Иванов\n\n'
    text += '<b>-m</b> - Сделать администратора главным\n'
    text += 'Если флаг не указан, то пользователь станет обычным администратором\n'
    text += 'Примеры:\n'
    text += '/addAdmin @username -m\n'
    text += '/addAdmin @username -m -n Иван Иванов\n'
    text += '/addAdmin @username -n Иван Иванов -m\n\n'
    text += '<b>-s</b> - Установить новые параметры у существующего администратора\n'
    text += 'Если никакие параметры не указаны, они установятся на дефолтыне:\n'
    text += '(-n) Имя: admin\n'
    text += '(-m) Администратор: обычный\n'
    text += 'Примеры:\n'
    text += '/addAdmin @username -s -> (имя: admin; администратор: обычный)\n'
    text += '/addAdmin @username -s -n Иван -> (имя: Иван; администратор: обычный)\n'
    text += '/addAdmin @username -s -m -> (имя: admin; администратор: главный)\n'
    text += '/addAdmin @username -s -n -m -> (имя: admin; администратор: главный)\n'
    text += '/addAdmin @username -s -n Иван -m -> (имя: Иван; администратор: главный)\n\n'
    text += '<b>--help</b> - Узнать информацию о команде\n'
    return text


def delAdmin_info() -> str:
    text = 'Функция /delAdmin удаляет администратора из системы по его username\n\n'
    text += 'Допустимый ввод username:\n'
    text += 'https://t.me/username\n'
    text += 't.me/username\n'
    text += '@username\n\n'
    text += 'Примеры: \n'
    text += '/delAdmin @username - удалить одного пользователя\n'
    text += '/delAdmin @username1 @username2 ... - удалить несколько пользователя\n\n'
    text += 'Флаги: \n'
    text += '<b>--help</b> - Узнать информацию о команде\n'
    return text


def del_admin_text(info: tuple[str, int, str, bool]) -> str:
    text = f'Член персонала <a href="t.me/{info[0]}">{info[2]}</a> был удален из системы\n'
    text += '<b>Роль:</b> '
    if info[3]:
        text += 'Главный администратор\n'
    else:
        text += 'Администратор\n'
    text += f'ID: <span class="tg-spoiler">{info[1]}</span>'
    return text


def add_admin_text(username: str, name: str, main: bool) -> str:
    text = f'В систему был добавлен новый член персонала: <a href="https://t.me/{username}">{name}</a>\n'
    text += '<b>Роль:</b> '
    if main:
        text += 'Главный администратор\n'
    else:
        text += 'Администратор\n'
    return text


def set_admin_text(username: str, name: str, main: bool) -> str:
    text = f'Данные члена персонала <a href="https://t.me/{username}">{name}</a> обновлены\n'
    text += '<b>Роль:</b> '
    if main:
        text += 'Главный администратор\n'
    else:
        text += 'Администратор\n'
    return text
