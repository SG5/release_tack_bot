from provider.packagist import *
from pymongo import MongoClient

import os
import telegram

client = MongoClient(os.environ['MONGODB_CONNECT'])
db = client.releases

bot = telegram.Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])

for item in db.tasks.find():
    api = Packagist(item['product'])
    last_release = None

    if 'version' not in item:
        releases = api.get_releases()
        if len(releases):
            last_release = api.get_releases()[-1]
    else:
        last_release = api.get_new_version(item['version'])

        if last_release is not None:
            for consumer in db.consumers.find({'task': item['_id']}):
                bot.send_message(chat_id=consumer['chat_id'], text='Вышла новая версия {}:  {}'.format(
                    item.get('description', last_release['description']),
                    last_release['version']
                ))

    if last_release and item.get('version') != last_release['version']:
        db.tasks.update_one(
            {'_id': item['_id']},
            {'$set': {'version': last_release['version']}}
        )