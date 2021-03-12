#!/usr/bin/env /usr/local/bin/python3.9
import asyncio
from builtins import EnvironmentError
import json
import os

import aiohttp
from aiohttp import ClientSession
from datetime import timezone
import dateutil.parser
from logging import getLogger
import uvloop

from database import session
from models import PostedArticles


log = getLogger()

user_chat_ids = [411350834]


if "FLATFY_PARAMS" not in os.environ:
    raise EnvironmentError


async def get_new_articles_from_page(page_number: int, aiohttp_session: ClientSession) -> (list, bool):
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'api.flatfy.io',
        'Origin': 'https://flatfy.lun.ua',
        'Pragma': 'no-cache',
        'Referer': 'https://flatfy.lun.ua/search',
        'TE': 'Trailers',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
    }
    url = f'https://api.flatfy.io/api/realties'

    client_response = await aiohttp_session.get(
        url,
        params=f'page={page_number}&{os.environ["FLATFY_PARAMS"]}',
        headers=headers
    )
    page = json.loads(await client_response.text())
    articles = page['data']
    if len(articles) == 0:
        return [], False
    article_ids = [a['id'] for a in articles]

    old_articles = session.query(PostedArticles.article_id) \
        .filter(PostedArticles.article_id.in_(article_ids)) \
        .all()
    old_article_ids = [a.article_id for a in old_articles]

    new_article_ids = list(filter(lambda a_id: a_id not in old_article_ids, article_ids))

    new_articles = list(filter(lambda a: a['id'] in new_article_ids, articles))

    return new_articles, len(new_article_ids) == len(article_ids) and len(article_ids) == 24


def convert_time(timestamp: str) -> str:
    return dateutil.parser.parse(timestamp)\
        .replace(tzinfo=timezone.utc)\
        .astimezone(tz=None)\
        .strftime('%Y-%m-%d %H:%M:%S')


def build_caption(article) -> str:
    return f'<a href="https://flatfy.lun.ua/redirect/{article["id"]}"><b>' \
               f'{article["price"] and int(article["price"])} {article["currency"]} ' \
               f'({article["price_sqm"] and int(article["price_sqm"])} {article["currency"]} per m²)' \
           f'</b></a>\n\n' \
           f'<a href="https://www.google.com/maps/place/' \
               f'{article["location"][1]},{article["location"][0]}">{article["geo"]}' \
           f'</a>\n\n' \
           f'{article["text"]}\n\n\n' \
           f'm2 {(article["area_kitchen"] and int(article["area_kitchen"])) or "-"}/' \
           f'{(article["area_living"] and int(article["area_living"])) or "-"}/' \
           f'{(article["area_total"] and int(article["area_total"])) or "-"}\n' \
           f'year {article["built_year"] or "-"}\n' \
           f'floor {article["floor"]}/{article["floor_count"]}\nwalls {article["wall_type_name"]}\n' \
           f'agency {article["agency"] if article["agency"] else "none"}\n\n' \
           f'<i>post {convert_time(article["insert_time"])}\nupdate {convert_time(article["download_time"])}</i>'


async def send_article_notifies(article, aiohttp_session: ClientSession):
    if len(article['images']) == 0:
        log.warning(f'skipped article with id {article["id"]} without images')
        return

    caption = build_caption(article)
    if len(caption) > 1024:
        new_description = article['text'][0:-(len(caption)-1024+3)] + '...'
        caption = build_caption({**article, 'text': new_description})
    images = article['images'][0:9] if len(article['images']) > 10 else article['images']

    media_list = [
        {
            'type': 'photo',
            'media': f'https://lunappimg.appspot.com/lun-ua/414/336/images-cropped/{image["image_id"]}.jpg'
        } for image in images
    ]

    media_list[0] = {**media_list[0], 'caption': caption, 'parse_mode': 'HTML'}
    for user_chat_id in user_chat_ids:
        resp = await aiohttp_session.get(
            f'https://api.telegram.org/bot{os.environ["TELEGRAM_BOT_TOKEN"]}/sendMediaGroup',
            params={
                'chat_id': user_chat_id,
                'type': 'photo',
                'media': json.dumps(media_list),
                'disable_notification': 'true'
            }
        )
        if 400 <= resp.status < 500:
            log.error(f'non-ok http status. \nstatus: {resp.status}\ntext: {await resp.text()}\n{resp}')
        elif resp.status >= 500:
            log.warning(f'non-ok http status. \nstatus: {resp.status}\ntext: {await resp.text()}\n{resp}')


async def main():
    async with aiohttp.ClientSession() as aiohttp_session:
        page_number = 1
        new_articles, is_have_new_posts = await get_new_articles_from_page(page_number, aiohttp_session)
        print(f'Processed page {page_number}')
        while is_have_new_posts:
            page_number += 1
            page_articles, is_have_new_posts = await get_new_articles_from_page(page_number, aiohttp_session)
            new_articles += page_articles
            print(f'Processed page {page_number}')

        if new_articles:
            print(f'Sending notifications...')
        for article in new_articles:
            await send_article_notifies(article, aiohttp_session)
            await asyncio.sleep(0.05)

        await aiohttp_session.close()

        if new_articles:
            rows = list(map(lambda a: PostedArticles(article_id=a['id']), new_articles))
            session.add_all(rows)
            session.commit()
        print('Done.')

if __name__ == '__main__':
    loop = uvloop.new_event_loop()
    loop.run_until_complete(main())
