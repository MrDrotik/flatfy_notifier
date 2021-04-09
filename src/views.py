from hashlib import sha256
import json
import os

from aiohttp import web

from src.command_handlers import handle_command


routes = web.RouteTableDef()


@routes.post(f'/tg-webhook-message-{sha256(os.environ["TELEGRAM_BOT_TOKEN"].encode()).hexdigest()}')
async def telegram_message_webhook(request: web.Request):
    parsed_json = json.loads(await request.text())
    print(json.dumps(parsed_json, indent=4, sort_keys=True) + '\n\n\n')
    message = parsed_json['message']
    if 'text' not in message or message['chat']['type'] != 'private':
        return web.Response()
    text = message['text']
    if 'entities' in message and next((e for e in message['entities'] if e['type'] == 'bot_command'), None):
        command_entity = next((e for e in message['entities'] if e['type'] == 'bot_command'), None)
        command_text = text[command_entity['offset']:command_entity['offset'] + command_entity['length']]
        command_args = text[command_entity['offset'] + command_entity['length']:].strip()
    else:
        command_text = ''
        command_args = text.strip()

    await handle_command(
        command_text=command_text,
        command_args=command_args,
        chat_id=message['chat']['id'],
    )

    return web.Response(status=200)
