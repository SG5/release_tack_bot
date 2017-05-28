import requests

URL = 'https://packagist.org/p/{}.json'


class Packagist:
    package = None
    package_data = None

    def __init__(self, package):
        super().__init__()
        self.package = package

    def get_releases(self):
        self.__fetch_releases()
        return self.package_data

    def get_new_version(self, last_version):
        self.__fetch_releases()

    def __fetch_releases(self):
        if self.package_data is None:
            package_data = requests.get(URL.format(self.package)).json()
            package_data = {k:v for k, v in package_data['packages'][self.package].items() if -1 == k.find('-')}
            self.package_data = sorted(package_data.values(), key=lambda r: r['time'])
        return self
