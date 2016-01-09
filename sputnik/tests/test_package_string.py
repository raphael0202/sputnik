import pytest

from ..package_string import PackageString


def test_string_match():
    x = PackageString('test 1.0.0')
    y = PackageString(name='test', version='1.0.0')
    assert x.name == y.name
    assert x.version == y.version
    assert x == y


def test_no_string_match():
    x = PackageString('test 1.0.0')
    y = PackageString(name='abc', version='1.0.0')
    assert x.name != y.name
    assert x.version == y.version
    with pytest.raises(Exception):
        x != y


def test_version_match():
    assert PackageString('test>=1.0.0').match(PackageString('test 1.0.0'))
    assert PackageString('test==1.0.0').match(PackageString('test 1.0.0'))
    assert PackageString('test<=1.0.0').match(PackageString('test 1.0.0'))
    assert PackageString('test>1.0.0').match(PackageString('test 1.1.0'))
    assert PackageString('test<1.0.0').match(PackageString('test 0.1.0'))

    assert PackageString('test >=1.0.0').match(PackageString('test 1.0.0'))
    assert PackageString('test ==1.0.0').match(PackageString('test 1.0.0'))
    assert PackageString('test <=1.0.0').match(PackageString('test 1.0.0'))
    assert PackageString('test >1.0.0').match(PackageString('test 1.1.0'))
    assert PackageString('test <1.0.0').match(PackageString('test 0.1.0'))


def test_no_version_match():
    assert not PackageString('test').match(PackageString('abc'))

    assert not PackageString('test>=1.0.0').match(PackageString('test 0.1.0'))
    assert not PackageString('test==1.0.0').match(PackageString('test 0.1.0'))
    assert not PackageString('test<=1.0.0').match(PackageString('test 1.1.0'))
    assert not PackageString('test>1.0.0').match(PackageString('test 0.1.0'))
    assert not PackageString('test<1.0.0').match(PackageString('test 1.1.0'))

    assert not PackageString('test >=1.0.0').match(PackageString('test 0.1.0'))
    assert not PackageString('test ==1.0.0').match(PackageString('test 0.1.0'))
    assert not PackageString('test <=1.0.0').match(PackageString('test 1.1.0'))
    assert not PackageString('test >1.0.0').match(PackageString('test 0.1.0'))
    assert not PackageString('test <1.0.0').match(PackageString('test 1.1.0'))
