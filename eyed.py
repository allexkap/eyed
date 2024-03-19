from datetime import datetime, timedelta
from subprocess import run
from time import sleep

import requests
import os


TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']


def every(step: timedelta, start: datetime | None = None):
    if start is None:
        start = datetime.now()
    while True:
        if start < datetime.now():
            start += step
            yield
        sleep(1)


def send_report(d: tuple[str], a: tuple[str], h: str):
    b = '\n'.join(f'{c} {s}' for c, da in (('-', d), ('+', a)) for s in sorted(da))
    text = f'`{h}\n{b}`'
    response = requests.post(
        url='https://api.telegram.org/bot{}/sendMessage'.format(TELEGRAM_BOT_TOKEN),
        data={'chat_id': TELEGRAM_CHAT_ID, 'text': text, 'parse_mode': 'MarkdownV2'},
    )
    return response.status_code == 200


is_alive_cmd = ('systemctl', 'is-active', '--quiet')
header = 'power on self test:'

services = {'postgresql', 'docker', 'nessusd'}

reported = set()
for _ in every(timedelta(minutes=0, seconds=2)):
    dead = set(s for s in services if run(is_alive_cmd + (s,)).returncode)
    if header or reported != dead:
        if send_report(dead - reported, reported - dead, header):
            reported = dead
            header = ''
