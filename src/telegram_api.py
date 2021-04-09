import json
import os
from functools import wraps
from logging import getLogger

from aiohttp import ClientSession

log = getLogger(__name__)


def status_code_checker(func):
    @wraps(func)
    async def _wrapper(*args, **kwargs):
        resp = await func(*args, **kwargs)
        if 400 <= resp.status < 500:
            log.error(f'non-ok http status. \nstatus: {resp.status}\ntext: {await resp.text()}\n{resp}')
        elif resp.status >= 500:
            log.warning(f'non-ok http status. \nstatus: {resp.status}\ntext: {await resp.text()}\n{resp}')
        return resp
    return _wrapper


async def send_media_group(
        aiohttp_session: ClientSession,
        user_chat_id: int,
        media_list: list,
        disable_notification: bool = False
):
    resp = await aiohttp_session.get(
        f'https://api.telegram.org/bot{os.environ["TELEGRAM_BOT_TOKEN"]}/sendMediaGroup',
        params={
            'chat_id': user_chat_id,
            'type': 'photo',
            'media': json.dumps(media_list),
            'disable_notification': disable_notification
        }
    )
    return resp


async def send_message(
        aiohttp_session: ClientSession,
        chat_id: int,
        text: str,
        disable_notification: bool = False
):
    resp = await aiohttp_session.get(
        f'https://api.telegram.org/bot{os.environ["TELEGRAM_BOT_TOKEN"]}/sendMessage',
        params={
            'chat_id': chat_id,
            'text': text,
            'disable_notification': 'true' if disable_notification else 'false'
        }
    )
    return resp
