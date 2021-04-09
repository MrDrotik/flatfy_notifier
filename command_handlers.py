import aiohttp

from database import session
from models import ScrapFilters
from logging import getLogger

from telegram_api import send_message

log = getLogger(__name__)


async def handle_command(command_text: str, command_args: str, chat_id: int):
    if command_text == '/add':
        await add_filter(command_args, chat_id)
    elif command_text == '/del':
        await del_filter(command_args)
    elif command_text == '/list':
        await list_filters(chat_id)
    else:
        await unknown_command(chat_id)


async def add_filter(command_args: str, user_id: int):
    session.add(ScrapFilters(telegram_user_id=user_id, path=command_args))
    session.flush()


async def del_filter(command_args: str):
    filters = session.query(ScrapFilters)\
        .filter(ScrapFilters.path.like(command_args))\
        .all()
    for scraper_filter in filters:
        session.delete(scraper_filter)


async def list_filters(chat_id: int):
    filters = session.query(ScrapFilters).all()
    async with aiohttp.ClientSession() as aiohttp_session:
        await send_message(
            aiohttp_session=aiohttp_session,
            chat_id=chat_id,
            text='\n'.join(f.path for f in filters) if filters else 'filters list is empty'
        )


async def unknown_command(chat_id: int):
    async with aiohttp.ClientSession() as aiohttp_session:
        await send_message(
            aiohttp_session=aiohttp_session,
            chat_id=chat_id,
            text='unknown command'
        )
