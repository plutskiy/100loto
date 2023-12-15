def channels_list(channels: dict) -> str:
    text = str()
    i = 1
    for name, url in channels.items():
        text += f'{i}. <a href="https://t.me/{url}">{name}</a>'
        i += 1
    return text


def auth_info() -> str:
    text = 'Функция /auth обновляет Ваши id и username в системе, если они изменились или отсутствуют.\n\n'
    text += 'Параметры: \n'
    text += '<b>-n</b> - Изменить имя\n'
    text += 'Примеры:\n'
    text += '/auth -n Иван\n'
    text += '/auth -n Иван Иванов\n\n'
    text += '<b>--help</b> - Узнать информацию о команде\n'
    return text
