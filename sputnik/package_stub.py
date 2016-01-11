from . import util
from .base import Base


class PackageStub(Base):
    keys = ['name', 'version', 'description', 'license', 'compatibility']

    def __init__(self, defaults=None, **kwargs):
        defaults = defaults or {}
        self.name = defaults.get('name')
        self.version = defaults.get('version')
        self.description = defaults.get('description')
        self.license = defaults.get('license')
        self.compatibility = defaults.get('compatibility')

        super(PackageStub, self).__init__()

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
