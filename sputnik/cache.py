import os
import shutil
import hashlib
import io
import sys
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from . import uget
from . import util
from . import default
from .package_list import PackageList
from .package_stub import PackageStub
from .archive import Archive
from .session import Session


class CachedPackage(PackageStub):
    keys = PackageStub.keys + ['path']

    def __init__(self, **kwargs):
        meta = kwargs.pop('meta')
        cache = kwargs.pop('package_list')

        super(CachedPackage, self).__init__(defaults=meta['package'])

        self.data_path = cache.data_path
        self.meta = meta
        self.cache = cache
        self.path = os.path.join(cache.path, self.ident)

        assert os.path.isfile(os.path.join(self.path, default.META_FILENAME))

    @property
    def manifest(self):
        return self.meta['manifest']

    def remove(self):
        if not os.path.isdir(self.path):
            raise Exception("not installed")

        # cleanup remove
        if os.path.exists(self.path):
            tmp = self.path + '.tmp'
            shutil.move(self.path, tmp)
            shutil.rmtree(tmp)

        self.cache.load()


class Cache(PackageList):

    package_class = CachedPackage

    def __init__(self, app_name, app_version, data_path, **kwargs):
        cache_path = os.path.join(data_path, default.CACHE_DIRNAME)
        kwargs['data_path'] = data_path

        super(Cache, self).__init__(app_name, app_version, cache_path, **kwargs)

    def exists(self, ident, etag):
        packages = [p for p in self.list() if p.ident == ident]
        if packages:
            assert len(packages) <= 1
            return packages[0].meta['etag'] == etag
        return False

    def update(self, meta, url, etag=None):
        assert len(meta['archive']) == 2
        meta = dict(meta)

        package = PackageStub(meta['package'])

        meta['archive'].append(urljoin(url, meta['archive'][0]))
        meta['etag'] = etag

        path = os.path.join(self.path, package.ident,
                            default.META_FILENAME)

        util.makedirs(path)
        with io.open(path, 'wb') as f:
            f.write(util.json_dump(meta))

        # TODO optimize for calling update in a loop
        self.load()

    def fetch(self, package_string):
        package = self.get(package_string)
        path, checksum, url = package.meta['archive'][:3]

        full_path = os.path.join(package.path, path)
        util.makedirs(full_path)

        session = Session(self.app_name, self.app_version, self.data_path)
        uget.download(session, url, full_path,
                      console=sys.stdout,
                      checksum=hashlib.md5(),
                      checksum_header=util.s3_header('md5'))

        # TODO: use checksum

        return Archive(package.path)
