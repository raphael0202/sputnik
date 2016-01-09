import os

import pytest

from .. import install, build, remove, search, find, upload, update, files, purge
from ..archive import PackageNotCompatibleException


def test_build(sample_package_path):
    archive = build(None, None, sample_package_path)
    assert os.path.isfile(archive.path)


def test_build_install_remove(sample_package_path, tmp_path):
    archive = build(None, None, sample_package_path)
    assert os.path.isfile(archive.path)

    packages = find(None, None, data_path=tmp_path)
    assert len(packages) == 0

    package = install(None, None, archive.path, data_path=tmp_path)
    assert os.path.isdir(package.path)

    packages = find(None, None, data_path=tmp_path)
    assert len(packages) == 1
    assert packages[0].ident == package.ident

    remove(None, None, package.name, data_path=tmp_path)
    assert not os.path.isdir(package.path)

    packages = find(None, None, data_path=tmp_path)
    assert len(packages) == 0


def test_install_incompatible(sample_package_path, sample_package_path2, tmp_path):
    archive1 = build('test', '1.0.0', sample_package_path)
    package1 = install('test', '1.0.0', archive1.path, data_path=tmp_path)

    archive2 = build('test', '1.0.0', sample_package_path2)
    with pytest.raises(PackageNotCompatibleException):
        install('test', '1.0.0', archive2.path, data_path=tmp_path)

    packages = find('test', '1.0.0', data_path=tmp_path)
    assert len(packages) == 1
    assert packages[0].ident == package1.ident


def test_install_upgrade(sample_package_path, sample_package_path2, tmp_path):
    archive = build('test', '1.0.0', sample_package_path)
    install('test', '1.0.0', archive.path, data_path=tmp_path)

    packages = find('test', '2.0.0', data_path=tmp_path)
    assert len(packages) == 0


def test_purge_raw(sample_package_path, tmp_path):
    assert len(find('test', '1.0.0', data_path=tmp_path)) == 0

    purge('test', '1.0.0', data_path=tmp_path)

    assert os.path.isdir(tmp_path)


def test_purge(sample_package_path, tmp_path):
    archive = build('test', '1.0.0', sample_package_path)
    install('test', '1.0.0', archive.path, data_path=tmp_path)

    assert len(find('test', '1.0.0', data_path=tmp_path)) == 1

    purge('test', '1.0.0', data_path=tmp_path)

    assert len(find('test', '1.0.0', data_path=tmp_path)) == 0
