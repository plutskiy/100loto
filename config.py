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
        'main': True
    })

    tmp_data['admin'].append({
        'username': 'FDX_VI',
        'id': -1,
        'name': 'Валентин',
        'main': True
    })

    tmp_data['channel']['Будка хлепла'] = 'puton4ick'

    tmp_data['ticket'] = {
        'T': 1,
        "Z": 1
    }

    tmp_data['message'] = {
        'X': 10,
        'Y': 10
    }

    with open('config.json', 'w', encoding='utf-8') as file:
        json.dump(tmp_data, file)


def load():
    with open('config.json', 'w', encoding='utf-8') as file:
        json.dump(data, file)


def update():
    global data
    with open('config.json', 'r', encoding='utf-8') as file:
        data = json.load(file)


def add_admin(username: str, name: str, main: bool):
    data['admin'].append({
        'username': username,
        'id': -1,
        'name': name,
        'main': main
    })
    load()


def get_admin_info(username: str, id: int) -> tuple[str, int, str, bool]:
    admins: list = data['admin']
    for admin in admins:
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
        load()


if not os.path.exists('config.json'):
    create()

data = dict()
update()
