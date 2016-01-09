[![Travis CI](https://travis-ci.org/spacy-io/sputnik.svg?branch=master)](https://travis-ci.org/spacy-io/sputnik)

# Sputnik: a data package manager library

Sputnik is a library for managing data packages for another library, e.g., models for a machine learning library.

It also comes with a command-line interface, run ```sputnik --help``` or ```python -m sputnik --help``` for assistance.

Sputnik is a pure Python library licensed under MIT, has minimal dependencies (only ```semver```) and is tested against python 2.7, 3.4 and 3.5.

## Installation

Sputnik is available from [PyPI](https://pypi.python.org/pypi/sputnik) via ```pip```:

```
pip install sputnik
```

## Build a package

Add a ```package.json``` file with following JSON to a directory ```sample``` and add some files in ```sample/data``` that you would like to have packaged, e.g., ```sample/data/model```. See a sample layout [here](https://github.com/spacy-io/sputnik/tree/master/sample).

```
{
  "name": "my_model",
  "include": ["data/*"],
  "version": "1.0.0"
}
```

Build the package with following code, it should produce a new file and output its path: ```sample/my_model-1.0.0.sputnik```.

```
import sputnik
archive = sputnik.build(<app_name>, <app_version>, 'sample')
print(archive.path)
```

Replace ```<app_name>``` and ```<app_version>``` with your app's name and version. This information is used to check for package compatibility. You can also provide ```None``` instead to disable package compatibility checks. Read more about package compatibility under the Compatibility section below.

## Install a package

Decide for a location for your installed packages, e.g., ```packages```. Then install the previously built package with following code, it should output the path of the now installed package: ```packages/my_model-1.0.0```

```
package = sputnik.install(<app_name>, <app_version>, 'sample/my_model-1.0.0.sputnik', data_path='packages')
print(package.path)
```

## List installed packages

This should output the package strings for all installed packages, e.g., ```['my_model-1.0.0']```:

```
packages = sputnik.find(<app_name>, <app_version>, data_path='packages')
print([p.ident for p in packages])
```

## Access package data

Sputnik makes it easy to access packaged data files without dealing with filesystem paths or archive file formats.

First, get a Sputnik package object with:

```
sputnik.package(<app_name>, <app_version>, 'my_model', data_path='packages')
```

On the package object you can check for the existence of a file or directory, get it's path or directly open it. Note that each directory in a path must be provided as separate argument. Do not address paths with slashes or backslashes as this will lead to platform-compatibility issues.

```
if package.has_path('data', 'model'):
  # get filesystem path and use built-in open()
  f = io.open(package.file_path('data', 'model'), mode='r', encoding='utf8')
  res = f.read()
  f.close()

  # use Sputnik's open() wrapper
  f = package.open('data', 'model', mode='r', encoding='utf8')
  res = f.read()
  f.close()

  # use Sputnik's open() wrapper in a with statement
  with package.open('data', 'model', mode='r', encoding='utf8') as f:
    res = f.read()
```

Note that ```package.file_path()``` only works on files, not directory. Use ```package.dir_path()``` on directories.

If you want to list all file contents of a package use ```sputnik.files('my_model', data_path='packages')```.

## Remove package

```
sputnik.remove(<app_name>, <app_version>, 'my_model', data_path='packages')
```

## Purge package pool/cache

```
sputnik.purge(<app_name>, <app_version>, data_path='packages')
```

## Versioning

```install```, ```find```, ```package````, ```files```, ```search``` and ```remove``` commands accept version strings that follow [semantic versioning](http://semver.org/), e.g.:

```
sputnik.install(<app_name>, <app_version>, 'my_model ==1.0.0', data_path='packages')
sputnik.find(<app_name>, <app_version>, 'my_model >1.0.0', data_path='packages')
sputnik.package(<app_name>, <app_version>, 'my_model >=1.0.0', data_path='packages')
sputnik.search(<app_name>, <app_version>, 'my_model <1.0.0', data_path='packages')
sputnik.files(<app_name>, <app_version>, 'my_model <=1.0.0', data_path='packages')
sputnik.remove(<app_name>, <app_version>, 'my_model ==1.0.0', data_path='packages')
```

## Compatibility

Sputnik ensures compatibility with an app's name and version. An app in this context is the project that imports Sputnik (e.g., name/version of a library) using [semantic versioning](http://semver.org/). Let's see an example where this is useful:

my_model/package.json:
```
{
  "name": "my_model",
  "description": "this model is awesome",
  "include": ["data/*"],
  "version": "2.0.0",
  "license": "public domain",
  "compatibility": {
    "my_library": ">=0.6.1"
  }
}
```

This means that this package has version ```2.0.0``` and requires version ```0.6.1``` of ```my_library```, to be installed/used.

Let's get another Sputnik reference - now passing our library name and version to it - and build/install the package:

```
archive = sputnik.build('my_library', '0.6.0', 'my_model', data_path='packages')
sputnik.install('my_library', '0.6.0', archive.path, data_path='packages')
```

This should throw an exception as it requires version ```0.6.1``` of our library:

```
sputnik.archive.PackageNotCompatibleException:
running my_library 0.6.0 but requires {'my_library': '>=0.6.1'}
```

Upgrading our library to version ```0.6.1```:

```
archive = sputnik.build('my_library', '0.6.1', 'my_model', data_path='packages')
sputnik.install('my_library', '0.6.1', archive.path, data_path='packages')
```
