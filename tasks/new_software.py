import asyncio
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup

from init import releaseDb, releaseBot
from provider.npmjs import NpmJS
from provider.packagist import Packagist

PROVIDERS = {
    'Packagist': Packagist,
    'NpmJS': NpmJS,
}


async def mongo_tasks():
    processing = []
    for task in await releaseDb.tasks.find().to_list(1000):
        processing.append(process_task(task))
    return await asyncio.wait(processing)


async def process_task(task):
    api = PROVIDERS[task['provider']](task['product'])
    last_release = None

    if 'version' in task:
        last_release = await api.get_new_version(task['version'])
        if last_release:
            last_release['provider'] = task['provider']
            await notify_consumers(task, last_release)
    else:
        releases = await api.get_releases()
        if len(releases):
            last_release = releases[-1]

    if last_release and task.get('version') != last_release['version']:
        releaseDb.tasks.update_one(
            {'_id': task['_id']},
            {'$set': {'version': last_release['version']}}
        )


async def notify_consumers(item, release):
    for consumer in await releaseDb.consumers.find(filter={'task': item['_id']}, projection={'chat_id': True}).to_list(1000):
        text = 'Вышла новая версия *{}*:  `{}`'.format(
            item.get('description', release['description']),
            release['version']
        )
        reply_links = [[]]
        release_url = ''

        if release['provider'] == 'Packagist':
            reply_links[0].append(
                InlineKeyboardButton(text='Packagist', url=f'https://packagist.org/packages/{item["product"]}')
            )
            release_url = release.get('source', {}).get('url', '')
        elif release['provider'] == 'NpmJS':
            reply_links[0].append(
                InlineKeyboardButton(text='npmjs.com', url=f'https://www.npmjs.com/package/{item["product"]}')
            )
            release_url = release.get('repository', {}).get('url', '').replace('git+http', 'http')

        if release_url[-4:] == '.git' and release_url[:19] == 'https://github.com/':
            reply_links[0].append(
                InlineKeyboardButton(text='Github', url=release_url[:-4])
            )

        releaseBot.sendMessage(
            chat_id=consumer['chat_id'], text=text, parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=reply_links)
        )


if __name__ == '__main__':
    mongo_tasks()
