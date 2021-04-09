#!/usr/bin/env /usr/local/bin/python3.9
from aiohttp import web
import logging

from views import routes


def setup_routes(app):
    app.add_routes(routes)


app = web.Application()


logging.basicConfig(level=logging.ERROR)
setup_routes(app)


if __name__ == '__main__':
    web.run_app(app)
