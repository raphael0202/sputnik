import io
import types
import contextlib
from collections import OrderedDict

from . import util


class PackageStub(object):
    keys = ['name', 'version', 'description', 'license', 'compatibility']

    def __init__(self, defaults=None):
        defaults = defaults or {}
        for key in self.keys:
            setattr(self, key, defaults.get(key))

    def is_valid(self, raise_exception=False):
        res = False
        if self.name and self.version:
            res = True

        if raise_exception and not res:
            raise Exception('invalid package')
        return res

    @property
    def ident(self):
        if self.is_valid(True):
            return util.archive_filename(self.name, self.version)

    def to_json(self, keys=None):
        return util.json_dump(self.to_dict(keys))

    def to_dict(self, keys=None):
        keys = keys or []
        if hasattr(self, 'is_valid'):
            self.is_valid()
        return OrderedDict([
            (k, getattr(self, k))
            for k in self.keys
            if not keys or k in keys])

    def has_file(self, *path_parts):
        raise NotImplementedError

    def file_path(self, *path_parts):
        raise NotImplementedError

    def dir_path(self, *path_parts):
        raise NotImplementedError

    @contextlib.contextmanager
    def open(self, path_parts, mode='r', encoding='utf8', default=IOError):
        if self.has_file(*path_parts):
            f = io.open(self.file_path(*path_parts),
                        mode=mode, encoding=encoding)
            yield f
            f.close()

        else:
            if isinstance(default, types.TypeType) and issubclass(default, Exception)(default):
                raise default(self.file_path(*path_parts))
            elif isinstance(default, Exception):
                raise default
            else:
                yield default
