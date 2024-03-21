import os
from datetime import datetime, timedelta
from subprocess import run
from time import sleep

import requests

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


def run_is_alive(service: str) -> bool:
    status = run(
        ('systemctl', 'is-active', service), capture_output=True, text=True
    ).stdout.strip()
    return status in ('active', 'activating', 'reloading')


def send_report(d: set[str], a: set[str], header: str) -> bool:
    text = '\n'.join(f'{ch} {s}' for ch, da in (('-', d), ('+', a)) for s in sorted(da))
    try:
        response = requests.post(
            url='https://api.telegram.org/bot{}/sendMessage'.format(TELEGRAM_BOT_TOKEN),
            data={
                'chat_id': TELEGRAM_CHAT_ID,
                'text': f'`{header}{text}`',
                'parse_mode': 'MarkdownV2',
            },
        )
        return response.status_code == 200
    except:
        return False


with open('services') as file:
    services = set(s for s in file.read().split() if not s.startswith('#'))

if __name__ == '__main__':
    header = True
    reported = set()
    for _ in every(timedelta(minutes=1)):
        dead = set(s for s in services if not run_is_alive(s))
        if header:
            if send_report(dead, services - dead, 'power on self test:\n'):
                header = False
                reported = dead
        elif reported != dead:
            if send_report(dead - reported, reported - dead, ''):
                reported = dead
