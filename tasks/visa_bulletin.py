from datetime import datetime
from io import BytesIO
import re

from PyPDF2 import PdfFileReader
from aiohttp import ClientSession, ClientError
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup

from init import mobMapBot, release_db

url = 'https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html'
chats = [
    '224473640',
    '-1001110150719'
]


class VisaBulletin:

    async def run(self):
        now = datetime.utcnow()
        next_bulletin = (
            now.replace(month=now.month+1) if now.month < 12 else now.replace(month=1, year=now.year+1)
        ).strftime('%B %Y')

        if await release_db.bulletins.find_one({'name': next_bulletin}):
            return

        self.session = ClientSession()
        async with self.session.get(url) as response:
            response_data = await response.text()

        search_result = re.search(f'<a.+?href="(.+?)".+?{next_bulletin}', response_data)

        if not search_result:
            return

        notify_new_vb(next_bulletin)
        release_db.bulletins.insert_one({'name': next_bulletin})

        pdf_name = next_bulletin.replace(' ', '').lower()
        new_cn, cn_url = await self._check_case_number(
            'https://travel.state.gov' + search_result.group(1),
            f'https://travel.state.gov/content/dam/visas/Bulletins/visabulletin_{pdf_name}.pdf'
        )
        if new_cn:
            notify_case_number(new_cn, cn_url)

    async def _check_case_number(self, vb_url, pdf_url):
        try:
            async with self.session.get(vb_url) as response:
                response_data = await response.text()

            search_result = re.search('EUROPE.+?EUROPE.+?([\\d,]+|CURRENT)', response_data, re.S|re.I)
            if search_result:
                return search_result.group(1), vb_url
        except ClientError:
            pass

        try:
            async with self.session.get(pdf_url) as response:
                pdf_file = PdfFileReader(BytesIO(await response.read()))
        except ClientError:
            return

        pages = pdf_file.numPages
        while pages:
            pages -= 1
            text = pdf_file.getPage(pages).extractText().replace('\n', '')

            if 'THE DIVERSITY (DV) IMMIGRANT CATEGORY RANK CUT-OFFS WHICH WILL APPLY' in text:
                search_result = re.search('EUROPE.+?([\\d,]+|CURRENT)', text, re.S|re.I)
                if search_result:
                    return search_result.group(1), pdf_url


def notify_new_vb(next_bulletin):
    reply_links = [[
        InlineKeyboardButton(text=next_bulletin, url=url)
    ]]

    for chat in chats:
        mobMapBot.sendMessage(
            chat_id=chat, parse_mode='Markdown',
            text=f'🇺🇸🤠🇺🇸\n*{next_bulletin}* VB has been released!',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=reply_links)
        )


def notify_case_number(cn, cn_url):
    reply_links = [[
        InlineKeyboardButton(text=cn, url=cn_url)
    ]]

    for chat in chats:
        mobMapBot.sendMessage(
            chat_id=chat, parse_mode='Markdown',
            text=f'New case number: *{cn}*\n😱',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=reply_links)
        )
