import os
import logging
import shutil

import semver

from . import default
from . import util
from .package_stub import PackageStub


class CompatiblePackageNotFoundException(Exception): pass
class PackageNotFoundException(Exception): pass
class InvalidDataPathException(Exception): pass


class PackageList(object):

    package_class = PackageStub

    def __init__(self, app_name, app_version, path, **kwargs):
        super(PackageList, self).__init__()

        self.logger = logging.getLogger(__name__)

        self.app_name = app_name
        self.app_version = app_version

        self.path = path
        self.data_path = kwargs.get('data_path') or path

        if not self.data_path:
            raise InvalidDataPathException(self.data_path)

        self.load()

    def packages(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        for path in os.listdir(self.path):
            if path.endswith('.tmp'):
                continue

            meta_path = os.path.join(self.path, path, default.META_FILENAME)
            if not os.path.isfile(meta_path):
                continue

            yield self.__class__.package_class(path=os.path.join(self.path, path))

    def load(self):
        self._packages = {}
        for package in self.packages():
            self._packages[package.ident] = package

    def get(self, package_string):
        candidates = sorted(self.find(package_string, only_compatible=False),
                            key=lambda c: (self.is_compatible(c), c))

        if not candidates:
            raise PackageNotFoundException(package_string)

        package = candidates[-1]

        if not self.is_compatible(package):
            raise CompatiblePackageNotFoundException(
                'running %s %s but requires %s' %
                (self.app_name, self.app_version, package.compatibility))

        return package

    def find(self, package_string=None, only_compatible=True):
        res = []
        for package in self._packages.values():
            if util.constraint_match(package_string, package.name, package.version):
                if not only_compatible or self.is_compatible(package):
                    res.append(package)
        return res

    def purge(self):
        self.logger.info('purging %s', self.__class__.__name__)
        for package in self.find():
            self.remove(package)

    def is_compatible(self, package):
        def c(app_version, version_match):
            # TODO allow app_version to be in compact form (e.g., 0.1 instead of 0.1.0)
            if app_version:
                return semver.match(app_version, version_match.strip())
            return True

        if not package.compatibility:
            return True

        compatibility = package.compatibility.get(self.app_name)
        if not compatibility:
            return not self.app_name

        return all(c(self.app_version, v) for v in compatibility.split(','))

    def remove(self, package):
        if not os.path.isdir(package.path):
            raise Exception('Package not correctly installed: %s' % package.ident)

        # cleanup remove
        if os.path.exists(package.path):
            self.logger.info('pending remove %s', package.ident)
            tmp = package.path + '.tmp'
            shutil.move(package.path, tmp)
            self.logger.info('remove %s', package.ident)
            shutil.rmtree(tmp)

        self.load()
