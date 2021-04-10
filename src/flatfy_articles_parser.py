#!/usr/bin/env /usr/local/bin/python3.9
import asyncio
import json
from logging import getLogger

import aiohttp
from aiohttp import ClientSession
from datetime import timezone
import dateutil.parser
import uvloop

from src.database import session
from src.models import PostedArticles, ScrapFilters, Users
from src.telegram_api import send_media_group

log = getLogger(__name__)

ARTICLES_COUNT_ON_SEARCH_PAGE = 24


async def fetch_new_articles_with_filter(aiohttp_session: ClientSession, scraper_filter: ScrapFilters) -> list:
    page_number = 1
    result, is_have_new_posts = await fetch_articles_from_search_page(
        aiohttp_session,
        scraper_filter.path,
        page_number
    )
    print(f'Processed page {page_number}')
    while is_have_new_posts:
        page_number += 1
        articles = await fetch_articles_from_search_page(
            aiohttp_session=aiohttp_session,
            params=scraper_filter.path,
            page_number=page_number
        )
        if len(articles) == 0:
            break
        articles_id = [a['id'] for a in articles]

        old_articles = session.query(PostedArticles.article_id) \
            .filter(PostedArticles.article_id.in_(articles_id)) \
            .all()
        old_articles_id = [a.article_id for a in old_articles]
        new_articles_id = list(filter(lambda a_id: a_id not in old_articles_id, articles_id))
        new_articles = list(filter(lambda a: a['id'] in new_articles_id, articles))
        is_have_new_posts = len(new_articles) == len(articles) and len(articles_id) == ARTICLES_COUNT_ON_SEARCH_PAGE
        result += new_articles
        print(f'Processed page {page_number}')
    return result


async def fetch_articles_from_search_page(aiohttp_session: ClientSession, params: str, page_number: int) -> dict:
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
        params=f'page={page_number}&{params}',
        headers=headers
    )
    return json.loads(await client_response.text())


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


async def notify_users_about_new_article(article, aiohttp_session: ClientSession):
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
    users = session.query(Users).all()
    for user in users:
        await send_media_group(aiohttp_session, user.id, media_list)


async def main():
    scrap_filters = session.query(ScrapFilters).all()

    async with aiohttp.ClientSession() as aiohttp_session:
        new_articles = []
        for filter in scrap_filters:
            new_articles += fetch_new_articles_with_filter(aiohttp_session, filter)

        if new_articles:
            print(f'Sending notifications...')
        for article in new_articles:
            await notify_users_about_new_article(article, aiohttp_session)
            await asyncio.sleep(0.20)

        await aiohttp_session.close()

        if new_articles:
            rows = list(map(lambda a: PostedArticles(article_id=a['id']), new_articles))
            session.add_all(rows)
            session.commit()
        print('Done.')

if __name__ == '__main__':
    loop = uvloop.new_event_loop()
    loop.run_until_complete(main())
