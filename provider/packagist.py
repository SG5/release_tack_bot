import ssl

import certifi as certifi
from aiohttp import ClientSession

URL = 'https://packagist.org/p/{}.json'

sslcontext = ssl.create_default_context(cafile=certifi.where())

class Packagist:
    package = None
    package_data = None
    session = None

    def __init__(self, package):
        super().__init__()
        self.package = package

    async def get_releases(self):
        await self.__fetch_releases()
        return self.package_data

    async def get_new_version(self, since):
        self.package_data = None
        await self.__fetch_releases()
        if self.package_data[-1]['version'] != since:
            return self.package_data[-1]
        return None

    async def __fetch_releases(self):
        if not Packagist.session:
            Packagist.session = ClientSession()

        if self.package_data is None:
            response = await Packagist.session.get(URL.format(self.package), ssl=sslcontext)
            package_data = await response.json()
            package_data = {k:v for k, v in package_data['packages'][self.package].items()
                            if -1 == v['version_normalized'].find('-') and 'time' in v
                            }
            self.package_data = sorted(package_data.values(), key=lambda r: r['time'])
        return self
