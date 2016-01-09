import sys
import platform
import os

import semver

from . import default
from .__about__ import __version__
from .pool import Pool
from .util import expand_path, json_print
from .package import Package, PackageRecipe
from .archive import Archive
from .cache import Cache
from .index import Index


# TODO support asterisks in versions


class Sputnik(object):
    def __init__(self, name=None, version=None, console=None):
        self.name = name
        if version:
            semver.parse(version)  # raises ValueError when invalid
        self.version = version
        self.console = console

    def pool(self, path):
        return Pool(path, s=self)

    def user_agent(self):
        uname = platform.uname()
        user_agent_vars = [
            ('Sputnik', __version__),
            (self.name, self.version),
            (platform.python_implementation(), platform.python_version()),
            (platform.uname()[0], uname[2]),
            ('64bits', sys.maxsize > 2**32)]

        return ' '.join(['%s/%s' % (k, v) for k, v in user_agent_vars if k])

    def log(self, message):
        if self.console:
            self.console.write(message + '\n')


def install(app_name,
            app_version,
            package_name,
            data_path=default.data_path,
            repository_url=default.repository_url,
            console=None):

    s = Sputnik(app_name, app_version, console=console)

    package_name = expand_path(package_name)
    data_path = expand_path(data_path)

    if os.path.isfile(package_name):
        archive = Archive(package_name, s=s)

    else:
        index = Index(data_path, repository_url, s=s)
        index.update()

        cache = Cache(data_path, s=s)
        pkg = cache.get(package_name)
        archive = pkg.fetch()

    pool = Pool(data_path, s=s)
    path = archive.install(pool)
    return Package(path=path, s=s)


def build(app_name,
          app_version,
          package_path=default.build_package_path,
          archive_path=None,
          console=None):

    s = Sputnik(app_name, app_version, console=console)

    recipe = PackageRecipe(expand_path(package_path), s=s)
    return recipe.build(expand_path(archive_path or package_path))


def remove(app_name,
           app_version,
           package_string,
           data_path=default.data_path,
           console=None):

    s = Sputnik(app_name, app_version, console=console)

    pool = Pool(expand_path(data_path), s=s)
    packages = pool.list(package_string)
    for pkg in packages:
        pkg.remove()


def search(app_name,
           app_version,
           search_string=default.search_string,
           data_path=default.data_path,
           repository_url=default.repository_url,
           console=None):

    s = Sputnik(app_name, app_version, console=console)

    # TODO make it work without data path?
    index = Index(data_path, repository_url, s=s)
    index.update()

    cache = Cache(data_path, s=s)
    packages = cache.list(search_string)
    json_print(s.log, [p.ident for p in packages])
    return packages


def find(app_name,
         app_version,
         package_string=default.find_package_string,
         meta=default.find_meta,
         cache=default.find_cache,
         data_path=default.data_path,
         console=None):

    s = Sputnik(app_name, app_version, console=console)

    cls = cache and Cache or Pool
    obj = cls(expand_path(data_path), s=s)
    packages = obj.list(package_string)
    keys = not meta and ('name', 'version') or ()
    json_print(s.log, [p.to_dict(keys) for p in packages])
    return packages


def upload(app_name,
           app_version,
           package_path,
           data_path=default.data_path,
           repository_url=default.repository_url,
           console=None):

    s = Sputnik(app_name, app_version, console=console)

    # TODO make it work without data path?
    index = Index(data_path, repository_url, s=s)
    return index.upload(expand_path(package_path))


def update(app_name,
           app_version,
           data_path=default.data_path,
           repository_url=default.repository_url,
           console=None):

    s = Sputnik(app_name, app_version, console=console)

    index = Index(expand_path(data_path), repository_url, s=s)
    index.update()


def package(app_name,
            app_version,
            package_string,
            data_path=default.data_path,
            console=None):

    s = Sputnik(app_name, app_version, console=console)

    pool = Pool(expand_path(data_path), s=s)
    return pool.get(package_string)


def files(app_name,
          app_version,
          package_string,
          data_path=default.data_path,
          console=None):

    s = Sputnik(app_name, app_version, console=console)

    if os.path.isfile(package_string):
        obj = Archive(package_string, s=s)
    else:
        pool = Pool(expand_path(data_path), s=s)
        obj = pool.get(package_string)

    res = {f['path']: {'checksum': f['checksum'], 'size': f['size']}
           for f in obj.manifest}
    json_print(s.log, {obj.ident: res})
    return res


def purge(app_name,
          app_version,
          cache=False,
          pool=False,
          data_path=default.data_path,
          console=None):

    s = Sputnik(app_name, app_version, console=console)

    data_path = expand_path(data_path)

    if cache or not cache and not pool:
        s.log('purging cache')
        Cache(data_path, s=s).purge()

    if pool or not cache and not pool:
        s.log('purging pool')
        Pool(data_path, s=s).purge()
