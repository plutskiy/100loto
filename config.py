import json
import os


def create():
    data = {'admin': [],
            'channel': {},
            'ticket': {},
            'message': {}}

    data['admin'].append({
        'username': 'pluton4ick',
        'id': -1,
        'name': 'Платон'
    })

    data['admin'].append({
        'username': 'FDX_VI',
        'id': -1,
        'name': 'Валентин'
    })

    data['channel']['@puton4ick'] = "Будка хлепла"

    data['ticket'] = {
        'T': 1,
        "Z": 1
    }

    data['message'] = {
        'X': 10,
        'Y': 10
    }

    with open('config.json', 'w', encoding='utf-8') as file:
        json.dump(data, file)


def update() -> dict:
    with open('config.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


if not os.path.exists('config.json'):
    create()

data = update()
