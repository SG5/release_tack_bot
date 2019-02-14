import os
from sanic import Sanic
from motor.motor_asyncio import AsyncIOMotorClient
from telepot import Bot

app = Sanic()

@app.listener('before_server_start')
async def open_connection(app, loop):
    db.client.io_loop = loop

db = AsyncIOMotorClient(os.environ['MONGODB_CONNECT'])[
    os.environ.get('MONGODB_DATABASE', 'releases')
]

bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])