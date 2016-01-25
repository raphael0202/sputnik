import shutil
import json
import io
import os
import re
import platform
import sys

import semver

from .__about__ import __version__


class InvalidPathPartsException(Exception): pass
class InvalidAppNameException(Exception): pass
class UnknownAppNameException(Exception): pass


def default_data_path(app_name):
    if app_name is None:
        raise InvalidAppNameException(app_name)
    try:
        mod = __import__(app_name, globals(), locals(), [], 0)
    except ImportError:
        raise UnknownAppNameException(app_name)
    return os.path.abspath(os.path.join(os.path.dirname(mod.__file__), 'data'))


def constraint_match(constraint, name, version=None):
    if not constraint:
        return True
    m = re.match(r'([a-z_]+)\s*([><=][=]?\d+\.\d+\.\d+)?', constraint)
    if not m:
        return False
    c_name, c_version = m.groups()
    return c_name == name and (not c_version or semver.match(version, c_version))


def get_path(*path_parts, **kwargs):
    sep = kwargs.pop('sep', os.path.sep)
    if any(p for p in path_parts if '/' in p or '\\' in p):
        raise InvalidPathPartsException('avoid / and \\ in path parts: %s' % path_parts)
    return sep.join(path_parts)


def user_agent(name, version):
    uname = platform.uname()
    user_agent_vars = [
        ('Sputnik', __version__),
        (name, version),
        (platform.python_implementation(), platform.python_version()),
        (platform.uname()[0], uname[2]),
        ('64bits', sys.maxsize > 2**32)]

    return ' '.join(['%s/%s' % (k, v) for k, v in user_agent_vars if k])


def system_info(name, version):
    return {'app_name': name,
            'app_version': version,
            'sputnik_version': __version__,
            'py': platform.python_implementation(),
            'py_version': platform.python_version(),
            'os': platform.uname()[0],
            'os_version': platform.uname()[2],
            'bits': 64 if sys.maxsize > 2**32 else 32}


def expand_path(path):
    return path and os.path.expanduser(path) or path


def is_enough_space(path, size):
    if hasattr(shutil, "disk_usage"):  # python >= 3.3
        free = shutil.disk_usage(path).free
        return free >= size
    return True


def archive_filename(name, version, suffix=False):
    res = "%s-%s" % (name, version)
    if suffix:
        res += ".sputnik"
    return res


def json_dump(obj):
    defaults = {'sort_keys': True, 'indent': 2, 'separators': (',', ': ')}
    return json.dumps(obj, **defaults).encode('utf8')


def json_load(path):
    with io.open(path, "rb") as f:
        return json.loads(f.read().decode('utf8'))


def json_print(obj):
    defaults = {'sort_keys': True, 'indent': 2, 'separators': (',', ': ')}
    sys.stdout.write(json.dumps(obj, **defaults) + '\n')


def makedirs(path):
    path = os.path.dirname(path)
    if path and not os.path.exists(path):
        os.makedirs(path)


def unquote(s):
    if (s[0] == s[-1]) and s.startswith(("'", '"')):
        return s[1:-1]
    return s


def s3_header(value):
    if not re.match(r'[A-Za-z0-9-]+', value):
        raise Exception('invalid value for S3 header: %s' % value)
    return 'x-amz-meta-%s' % value.lower()


def dirpath(path):
    if os.path.isdir(path):
        return path
    return os.path.split(path)[0]


def dirname(path):
    return os.path.basename(dir(path))
