from motor.motor_asyncio import AsyncIOMotorClient
from telepot import Bot
import os

db = AsyncIOMotorClient(os.environ['MONGODB_CONNECT'])[
    os.environ.get('MONGODB_DATABASE', 'releases')
]

bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])