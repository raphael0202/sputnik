import os
import logging
from glob import glob

from . import validation
from . import util
from .package_stub import PackageStub
from .archive_writer import ArchiveWriter
from .archive import Archive


class ValidationException(Exception): pass


class Recipe(PackageStub):  # package archive
    def __init__(self, recipe_path, base_path=None):
        defaults = util.json_load(os.path.join(recipe_path, "package.json"))
        super(Recipe, self).__init__(defaults)

        self.logger = logging.getLogger(__name__)

        if not validation.is_package_path(recipe_path):
            raise Exception("%r must be a directory" % recipe_path)

        self.recipe_path = recipe_path
        self.base_path = base_path or recipe_path

        self.include = defaults.get('include')
        self.is_valid(True)

    def is_valid(self, raise_exception=False):
        required_keys = ['name', 'version', 'include']
        for key in required_keys:
            if getattr(self, key) is None:
                if raise_exception:
                    raise ValidationException('invalid %s: %s' % (key, getattr(self, key)))
                else:
                    return False
        return True

    def build(self, archive_path):
        if os.path.isdir(archive_path):
            filename = util.archive_filename(self.name, self.version, suffix=True)
            archive_path = os.path.join(archive_path, filename)

        with ArchiveWriter(archive_path, base_path=self.base_path) as archive:
            self.logger.info("build %s", archive.path)

            for include in self.include:
                for path in glob(os.path.join(self.recipe_path, os.path.sep.join(include))):
                    if os.path.isfile(path):
                        archive.add(path)
            archive.add_json('package', self.to_dict())

        return Archive(archive_path)
