import os
import io

from . import default
from . import util
from .archive import Archive
from .pool import Pool
from .package import Package, PackageRecipe
from .index import Index
from .base import Base
from .cache import Cache


def expand_path(path):
    return path and os.path.expanduser(path) or path


class Command(Base):
    def install(self, package_name, data_path=default.data_path,
                repository_url=default.repository_url):

        package_name = expand_path(package_name)
        data_path = expand_path(data_path)

        if os.path.isfile(package_name):
            archive = Archive(package_name, s=self.s)

        else:
            index = Index(data_path, repository_url, s=self.s)
            index.update()

            cache = Cache(data_path, s=self.s)
            package = cache.get(package_name)
            archive = package.fetch()

        pool = Pool(data_path, s=self.s)
        path = archive.install(pool)
        return Package(path=path, s=self.s)

    def build(self, package_path=default.build_package_path,
              archive_path=None):

        recipe = PackageRecipe(expand_path(package_path), s=self.s)
        return recipe.build(expand_path(archive_path or package_path))

    def remove(self, package_string, data_path=default.data_path):
        pool = Pool(expand_path(data_path), s=self.s)
        packages = pool.list(package_string)
        for package in packages:
            package.remove()

    def search(self, search_string=default.search_string,
               data_path=default.data_path,
               repository_url=default.repository_url):

        # TODO make it work without data path?
        index = Index(data_path, repository_url, s=self.s)
        index.update()

        cache = Cache(data_path, s=self.s)
        packages = cache.list(search_string)
        util.json_print(self.s.log, [p.ident for p in packages])
        return packages

    def list(self, package_string=default.list_package_string,
             meta=default.list_meta, cache=default.list_cache,
             data_path=default.data_path):

        cls = cache and Cache or Pool
        obj = cls(expand_path(data_path), s=self.s)
        packages = obj.list(package_string)
        keys = not meta and ('name', 'version') or ()
        util.json_print(self.s.log, [p.to_dict(keys) for p in packages])
        return packages

    def upload(self, package_path, data_path=default.data_path,
               repository_url=default.repository_url):

        # TOD make it work without data path?
        index = Index(data_path, repository_url, s=self.s)
        return index.upload(expand_path(package_path))

    def update(self, data_path=default.data_path,
               repository_url=default.repository_url):

        index = Index(expand_path(data_path), repository_url, s=self.s)
        index.update()

    def file(self, package_string, path, data_path=default.data_path):
        pool = Pool(expand_path(data_path), s=self.s)
        package = pool.get(package_string)
        file_path = package.file_path(expand_path(path))
        util.json_print(self.s.log, file_path)
        return io.open(file_path, 'rb')

    def files(self, package_string, data_path=default.data_path):
        if os.path.isfile(package_string):
            obj = Archive(package_string, s=self.s)
        else:
            pool = Pool(expand_path(data_path), s=self.s)
            obj = pool.get(package_string)

        files = {f['path']: {'checksum': f['checksum'], 'size': f['size']}
                 for f in obj.manifest}
        util.json_print(self.s.log, {obj.ident: files})
        return files

    def purge(self, cache=False, pool=False, data_path=default.data_path):
        data_path = expand_path(data_path)

        if cache or not cache and not pool:
            self.s.log('purging cache')
            Cache(data_path, s=self.s).purge()

        if pool or not cache and not pool:
            self.s.log('purging pool')
            Pool(data_path, s=self.s).purge()
