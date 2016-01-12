import os

from . import default
from .pool import Pool
from .util import expand_path, json_print
from .package import Package
from .recipe import Recipe
from .archive import Archive
from .cache import Cache
from .index import Index


# TODO support asterisks in package_strings


def install(app_name,
            app_version,
            package_name,
            data_path=default.data_path,
            repository_url=default.repository_url):

    package_name = expand_path(package_name)
    data_path = expand_path(data_path)

    pool = Pool(app_name, app_version, data_path)

    if os.path.isfile(package_name):
        archive = Archive(package_name)

    else:
        index = Index(app_name, app_version, data_path, repository_url)
        index.update()

        packages = pool.list(package_name)
        if packages:
            return packages[0]

        cache = Cache(app_name, app_version, data_path)
        archive = cache.fetch(package_name)

    path = pool.install(archive)
    return Package(path=path)


def build(package_path=default.build_package_path,
          archive_path=None):

    recipe = Recipe(expand_path(package_path))
    return recipe.build(expand_path(archive_path or package_path))


def remove(app_name,
           app_version,
           package_string,
           data_path=default.data_path):

    pool = Pool(app_name, app_version, expand_path(data_path))
    packages = pool.list(package_string)
    for pkg in packages:
        pool.remove(pkg)


def search(app_name,
           app_version,
           search_string=default.search_string,
           data_path=default.data_path,
           repository_url=default.repository_url):

    # TODO make it work without data path?
    index = Index(app_name, app_version, data_path, repository_url)
    index.update()

    cache = Cache(app_name, app_version, data_path)
    packages = cache.list(search_string)
    json_print([p.ident for p in packages])
    return packages


def find(app_name,
         app_version,
         package_string=default.find_package_string,
         meta=default.find_meta,
         cache=default.find_cache,
         data_path=default.data_path):

    cls = cache and Cache or Pool
    obj = cls(app_name, app_version, expand_path(data_path))
    packages = obj.list(package_string)
    keys = not meta and ('name', 'version') or ()
    json_print([p.to_dict(keys) for p in packages])
    return packages


def upload(app_name,
           app_version,
           package_path,
           data_path=default.data_path,
           repository_url=default.repository_url):

    # TODO make it work without data path?
    index = Index(app_name, app_version, data_path, repository_url)
    return index.upload(expand_path(package_path))


def update(app_name,
           app_version,
           data_path=default.data_path,
           repository_url=default.repository_url):

    index = Index(app_name, app_version, expand_path(data_path), repository_url)
    index.update()


def package(app_name,
            app_version,
            package_string,
            data_path=default.data_path):

    pool = Pool(app_name, app_version, expand_path(data_path))
    return pool.get(package_string)


def files(app_name,
          app_version,
          package_string,
          data_path=default.data_path):

    if os.path.isfile(package_string):
        obj = Archive(package_string)
    else:
        pool = Pool(app_name, app_version, expand_path(data_path))
        obj = pool.get(package_string)

    res = {os.path.sep.join(f['path']): {'checksum': f['checksum'], 'size': f['size']}
           for f in obj.manifest}
    json_print({obj.ident: res})
    return res


def purge(app_name,
          app_version,
          cache=False,
          pool=False,
          data_path=default.data_path):

    data_path = expand_path(data_path)

    if cache or not cache and not pool:
        Cache(app_name, app_version, data_path).purge()

    if pool or not cache and not pool:
        Pool(app_name, app_version, data_path).purge()
