import asyncio
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from init import release_db, release_bot
from provider.npmjs import NpmJS
from provider.packagist import Packagist

PROVIDERS = {
    'Packagist': Packagist,
    'NpmJS': NpmJS,
}

logger = logging.getLogger(__name__)


async def mongo_tasks() -> None:
    processing = []
    for task in await release_db.tasks.find().to_list(1000):
        processing.append(process_task(task))
        await limiter(processing, 3)
    await limiter(processing)

    for p in PROVIDERS.values():
        if p.session:
            await p.session.close()
            p.session = None

async def limiter(processing: list, limit = 0) -> None:
    if not processing:
        return
    if len(processing) < limit:
        return
    try:
        await asyncio.wait(processing)
    except Exception as ex:
        logger.exception(f"{limiter.__name__} got an exception during awaiting {len(processing)} tasks", exc_info=ex)
    processing.clear()

async def process_task(task) -> None:
    logger.info(f"{process_task.__name__} for task {task['_id']}")
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
        release_db.tasks.update_one(
            {'_id': task['_id']},
            {'$set': {'version': last_release['version']}}
        )


async def notify_consumers(item, release) -> int:
    count = 0
    logger.info(f"{notify_consumers.__name__} sending messages for task {item['_id']}")
    for consumer in await release_db.consumers.find(filter={'task': item['_id']}, projection={'chat_id': True}).to_list(1000):
        count += 1
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

        await release_bot.send_message(
            chat_id=consumer['chat_id'], text=text, parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=reply_links)
        )

    logger.info(f"{notify_consumers.__name__} sent {count} message(s) for task {item['_id']}")
    return count


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(mongo_tasks())
