import logging
import os

from sanic import Sanic
from motor.motor_asyncio import AsyncIOMotorClient
from telepot import Bot
from telegram import Bot as tgBot

app = Sanic("bot")
db_client = AsyncIOMotorClient(os.environ['MONGODB_CONNECT'])

logging.basicConfig(level=logging.INFO)

@app.before_server_start
async def open_connection(_, loop):
    db_client._io_loop = loop

release_db = db_client[
    os.environ.get('MONGODB_DATABASE', 'releases')
]

release_bot = tgBot(token=os.environ['TELEGRAM_RELEASE_BOT_TOKEN'])
mobMapBot = Bot(token=os.environ['TELEGRAM_MOBMAP_BOT_TOKEN'])
