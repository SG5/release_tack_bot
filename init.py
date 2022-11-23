import logging
import os

from sanic import Sanic
from motor.motor_asyncio import AsyncIOMotorClient
from telepot import Bot

app = Sanic("bot")
dbClient = AsyncIOMotorClient(os.environ['MONGODB_CONNECT'])

logging.basicConfig(level=logging.INFO)

@app.before_server_start
async def open_connection(_, loop):
    dbClient.io_loop = loop

releaseDb = dbClient[
    os.environ.get('MONGODB_DATABASE', 'releases')
]

releaseBot = Bot(token=os.environ['TELEGRAM_RELEASE_BOT_TOKEN'])
mobMapBot = Bot(token=os.environ['TELEGRAM_MOBMAP_BOT_TOKEN'])
