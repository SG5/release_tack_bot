from aiohttp import ClientSession

URL = 'https://api.antizapret.info/all.php'
WHITE_LIST = {
    'rutor.info',
    'dou.ua',
    'rutracker.org',
    'linkedin.com',
    'pornhub.com',
}


async def generate_ipset():
    result = 'create rublack_tmp hash:ip family inet hashsize 65536 maxelem 900000\n'
    result += 'add rublack_tmp 138.201.14.212\n'

    for ip in await fetch_ips():
        result += f'add rublack_tmp {ip}\n'

    return result


async def fetch_ips():
    ips = set()

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

            ips.update(parse_ips(
                line[0:new_line_index].decode()
            ))
            line = line[new_line_index + 1:]

    return ips


def parse_ips(csv_line: str):
    csv_line = csv_line.split(';')
    if csv_line[2] == '':
        return []

    for domain in WHITE_LIST:
        if domain in csv_line[2]:
            return csv_line[3].split(',')

    return []
