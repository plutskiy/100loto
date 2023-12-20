import re


def check_telegram_link(username: str) -> tuple[bool, str]:
    username_pattern_1 = r'@[a-zA-Z0-9_]+'
    username_pattern_2 = r't\.me\/[a-zA-Z0-9_]+'
    username_pattern_3 = r'https\:\/\/t\.me\/[a-zA-Z0-9_]+'

    if re.match(username_pattern_1, username):
        print(username[1:])
        return True, username[1:]
    elif re.match(username_pattern_2, username):
        print(username[5:])
        return True, username[5:]
    elif re.match(username_pattern_3, username):
        print(username[13:])
        return True, username[13:]

    return False, username
