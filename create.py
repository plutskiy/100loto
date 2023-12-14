def channels_list(channels: dict) -> str:
    text = str()
    i = 1
    for channel in channels:
        text += f'{i}. <b>{channels[channel]}</b>: {channel}\n'
        i += 1
    return text
