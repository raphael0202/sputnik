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
