import io
import os
import logging

from . import util
from . import default
from .package_stub import PackageStub


class NotFoundException(Exception): pass
class NotIncludedException(Exception): pass


class Package(PackageStub):  # installed package
    def __init__(self, path):
        meta = util.json_load(os.path.join(path, default.META_FILENAME))
        super(Package, self).__init__(defaults=meta['package'])

        self.logger = logging.getLogger(__name__)
        self.meta = meta
        self.path = path

    def has_file(self, *path_parts):
        return any(m for m in self.manifest if tuple(m['path']) == path_parts)

    def file_path(self, *path_parts, **kwargs):
        require = kwargs.pop('require', True)
        assert not kwargs
        path = util.get_path(*path_parts)

        if not self.has_file(*path_parts):
            if require:
                raise NotIncludedException('package does not include file: %s' % path)
            return

        res = os.path.join(self.path, path)
        if not os.path.isfile(res):
            if require:
                raise NotFoundException('file not found: %s' % res)
            return
        return res

    def dir_path(self, *path_parts, **kwargs):
        require = kwargs.pop('require', True)
        path = util.get_path(*path_parts)

        res = os.path.join(self.path, path)
        if require and not os.path.isdir(res):
            raise NotFoundException('dir not found: %s' % res)
        # TODO check whether path is part of package
        return res

    def _load(self, func, *path_parts, **kwargs):
        require = kwargs.pop('require', True)
        default = kwargs.pop('default', None)

        try:
            path = self.file_path(*path_parts)
        except (NotIncludedException, NotFoundException):
            if require and default is None:
                raise
            return default
        with io.open(path, **kwargs) as f:
            return func(f)

    def load_utf8(self, func, *path_parts, **kwargs):
        kwargs.update({'mode': 'r', 'encoding': 'utf8'})
        return self._load(func, *path_parts, **kwargs)

    def load(self, func, *path_parts, **kwargs):
        kwargs.update({'mode': 'rb'})
        return self._load(func, *path_parts, **kwargs)

    @property
    def manifest(self):
        return self.meta['manifest']
