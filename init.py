from motor.motor_asyncio import AsyncIOMotorClient
import telegram
import os

db = AsyncIOMotorClient(os.environ['MONGODB_CONNECT'])[
    os.environ.get('MONGODB_DATABASE', 'releases')
]

bot = telegram.Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])