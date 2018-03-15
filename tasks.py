import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from init import db, bot
from provider.packagist import Packagist

loop = asyncio.get_event_loop()


def mongo_tasks():
    wait_tasks = asyncio.wait([get_tasks()])
    loop.run_until_complete(wait_tasks)
    return 'ok'


async def get_tasks():
    processing = []
    for task in await db.tasks.find().to_list(1000):
        processing.append(process_task(task))
    await asyncio.wait(processing)


async def process_task(task):
    api = Packagist(task['product'])
    last_release = None

    if 'version' in task:
        last_release = await api.get_new_version(task['version'])
        if last_release:
            await notify_consumers(task, last_release)
    else:
        releases = await api.get_releases()
        if len(releases):
            last_release = releases[-1]

    if last_release and task.get('version') != last_release['version']:
        db.tasks.update_one(
            {'_id': task['_id']},
            {'$set': {'version': last_release['version']}}
        )


async def notify_consumers(item, release):
    for consumer in await db.consumers.find(filter={'task': item['_id']}, projection={'chat_id': True}).to_list(1000):
        text = 'Вышла новая версия *{}*:  `{}`'.format(
            item.get('description', release['description']),
            release['version']
        )
        reply_links = [[
            InlineKeyboardButton('Packagist', url='https://packagist.org/packages/{}'.format(item['product']))
        ]]

        release_url = release['source']['url']
        if release_url[-4:] == '.git' and release_url[:19] == 'https://github.com/':
            reply_links[0].append(InlineKeyboardButton(
                'Github', url=release_url[:-4]
            ))

        bot.send_message(
            chat_id=consumer['chat_id'], text=text, parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(reply_links)
        )


if __name__ == '__main__':
    mongo_tasks()
