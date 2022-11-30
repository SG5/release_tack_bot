from aiohttp import ClientSession
from distutils.version import StrictVersion

URL = 'https://registry.npmjs.org/{}'

class NpmJS:
    package = None
    package_data = None
    session = None

    def __init__(self, package):
        super().__init__()
        self.package = package
        if not NpmJS.session:
            NpmJS.session = ClientSession()

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
        if self.package_data is None:
            response = await self.session.get(URL.format(self.package))
            response_data = await response.json()
            package_data = []
            for _, v in response_data['versions'].items():
                try:
                    v['strict_version'] = StrictVersion(v['version'])
                    package_data.append(v)
                except ValueError:
                    pass

            self.package_data = sorted(package_data, key=lambda p: p['strict_version'])
        return self
