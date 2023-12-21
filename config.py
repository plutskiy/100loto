import json
import os


def create():
    tmp_data = {'admin': [],
                'channel': {},
                'ticket': {},
                'message': {},
                'chan_id': []}

    tmp_data['admin'].append({
        'username': 'pluton4ick',
        'id': -1,
        'name': 'Платон',
        'main': True
    })

    tmp_data['admin'].append({
        'username': 'FDX_VI',
        'id': -1,
        'name': 'Валентин',
        'main': True
    })

    tmp_data['ticket'] = {
        'per_msg': 1,
        "ref_msg": 1
    }

    tmp_data['message'] = {
        'needed_msg': 10,
        'ref_msg': 10
    }

    with open('config.json', 'w', encoding='utf-8') as file:
        json.dump(tmp_data, file)


def dump():
    with open('config.json', 'w', encoding='utf-8') as file:
        json.dump(data, file)


def update():
    with open('config.json', 'r', encoding='utf-8') as file:
        global data
        data = json.load(file)
        return data


def add_admin(username: str, name: str, main: bool) -> bool:
    for admin in data['admin']:
        if admin['username'] == username:
            return False
    else:
        data['admin'].append({
            'username': username,
            'id': -1,
            'name': name,
            'main': main
        })
        dump()
        return True


def del_admin(username: str) -> bool:
    for i in range(len(data['admin'])):
        if data['admin'][i]['username'] == username:
            data['admin'].pop(i)
            dump()
            return True
    return False


def get_admin_info(username: str, id: int) -> tuple[str, int, str, bool]:
    for admin in data['admin']:
        if admin['username'] == username or admin['id'] == id:
            return admin['username'], admin['id'], admin['name'], admin['main']

    return 'None', -1, 'None', False


def is_admin(username: str, id: int) -> tuple[bool, bool, bool, bool]:
    admin_username, admin_id, admin_name, isMainAdmin = get_admin_info(username, id)
    isCorrectUsername = admin_username == username
    isCorrectId = admin_id == id
    isAdmin = isCorrectUsername or isCorrectId
    return isAdmin, isCorrectUsername, isCorrectId, isMainAdmin


def update_admin(username: str, id: int, name: str, main: bool):
    verification = is_admin(username, id)
    if not verification[0]:
        return

    for admin in data['admin']:
        if not (admin['username'] == username or admin['id'] == id):
            continue

        if not verification[1]:
            admin['username'] = username
        if not verification[2]:
            admin['id'] = id
        admin['name'] = name
        admin['main'] = main
        dump()


def set_admin(username: str, name: str, main: bool) -> bool:
    for admin in data['admin']:
        if admin['username'] == username:
            admin['name'] = name
            admin['main'] = main
            dump()
            return True
    return False


def set_config(params: tuple[int, ...]):
    data['message']['needed_msg'] = params[0]
    data['message']['ref_msg'] = params[1]
    data['ticket']['per_msg'] = params[2]
    data['ticket']['ref_msg'] = params[3]
    dump()


def get_tam_info() -> tuple[int, ...]:
    return data['message']['needed_msg'], data['message']['ref_msg'], data['ticket']['per_msg'], data['ticket'][
        'ref_msg']


def add_chat(chat_id: int) -> bool:
    if chat_id in data['chan_id']:
        return False
    else:
        data['chan_id'].append(chat_id)
        dump()
        return True


def remove_chat(chat_id: int) -> bool:
    if chat_id not in data['chan_id']:
        return False
    else:
        data['chan_id'].remove(chat_id)
        dump()
        return True


def add_channel(channel_id: int, channel_name: str) -> bool:
    if str(channel_id) in data['channel']:
        return False
    else:
        data['channel'][int(channel_id)] = channel_name
        dump()
        update()
        return True

def delete_channel(channel_id: int) -> bool:
    if channel_id not in data['channel']:
        return False
    else:
        data['channel'].pop(channel_id)
        dump()
        update()
        return True


if not os.path.exists('config.json'):
    create()

data = dict()
update()
