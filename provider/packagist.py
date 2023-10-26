import ssl
import logging

import certifi as certifi
from aiohttp import ClientSession, ClientError

URL = 'https://packagist.org/p/{}.json'
sslcontext = ssl.create_default_context(cafile=certifi.where())
logger = logging.getLogger(__name__)


class Packagist:
    package = None
    package_data = None
    session = None

    def __init__(self, package):
        super().__init__()
        self.package = package
        if not Packagist.session:
            Packagist.session = ClientSession()

    async def get_releases(self):
        await self.__fetch_releases()
        return self.package_data

    async def get_new_version(self, since):
        self.package_data = None
        try:
            await self.__fetch_releases()
        except ClientError as ex:
            logger.exception(f"action={self.get_new_version.__name__} package={self.package}", exc_info=ex)
            return None
        if self.package_data[-1]['version'] != since:
            return self.package_data[-1]
        return None

    async def __fetch_releases(self):
        if self.package_data is None:
            response = await Packagist.session.get(URL.format(self.package), ssl=sslcontext)
            response.raise_for_status()
            package_data = await response.json()
            package_data = {k:v for k, v in package_data['packages'][self.package].items()
                            if -1 == v['version_normalized'].find('-') and 'time' in v
                            }
            self.package_data = sorted(package_data.values(), key=lambda r: r['time'])
        return self
