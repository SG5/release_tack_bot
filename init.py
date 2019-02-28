import os
from sanic import Sanic
from motor.motor_asyncio import AsyncIOMotorClient
from telepot import Bot

app = Sanic()
dbClient = AsyncIOMotorClient(os.environ['MONGODB_CONNECT'])


@app.listener('before_server_start')
async def open_connection(app, loop):
    dbClient.io_loop = loop

releaseDb = dbClient[
    os.environ.get('MONGODB_DATABASE', 'releases')
]

releaseBot = Bot(token=os.environ['TELEGRAM_RELEASE_BOT_TOKEN'])
