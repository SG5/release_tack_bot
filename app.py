from provider.packagist import Packagist

api = Packagist('laravel/framework')
api.get_releases()