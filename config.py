import json
import os


def create():
    tmp_data = {'admin': [],
                'channel': {},
                'ticket': {},
                'message': {}}

    tmp_data['admin'].append({
        'username': 'pluton4ick',
        'id': -1,
        'name': 'Платон',
        'main': False
    })

    tmp_data['admin'].append({
        'username': 'FDX_VI',
        'id': -1,
        'name': 'Валентин',
        'main': True
    })

    tmp_data['channel']['Будка хлепла'] = 'puton4ick'

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
    global data
    with open('config.json', 'r', encoding='utf-8') as file:
        data = json.load(file)


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


if not os.path.exists('config.json'):
    create()

data = dict()
update()
