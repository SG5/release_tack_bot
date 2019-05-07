from aiohttp import ClientSession

URL = 'https://reestr.rublacklist.net/api/v2/ips/csv'


async def generate_ipset(response):
    await response.write('create rublack_tmp hash:ip family inet hashsize 65536 maxelem 900000\n')
    await response.write('add rublack_tmp 138.201.14.212\n')

    async for ip in fetch_ips():
        if ip:
            await response.write(f'add rublack_tmp {ip}\n')


async def fetch_ips():

    async with ClientSession().get(URL) as response:
        line = b''
        while True:
            chunk = await response.content.read(20)
            if not chunk:
                break

            line += chunk
            new_line_index = line.find(b'\n')
            if -1 == new_line_index:
                continue

            yield parse_ips(
                line[0:new_line_index].decode()
            )
            line = line[new_line_index + 1:]


def parse_ips(csv_line: str):
    if '.' in csv_line and '/' not in csv_line:
        return csv_line.replace(',', '')
