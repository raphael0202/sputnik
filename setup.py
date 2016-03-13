import os

from setuptools import setup, find_packages


base_dir = os.path.dirname(__file__)

with open(os.path.join(base_dir, 'sputnik', 'about.py')) as f:
    about = {}
    exec(f.read(), about)

with open(os.path.join(base_dir, 'README.rst')) as f:
    readme = f.read()


setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__summary__'],
    long_description=readme,
    url=about['__uri__'],
    author=about['__author__'],
    author_email=about['__email__'],
    license=about['__license__'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'sputnik = sputnik.__main__:main'
        ]
    },
    install_requires=['semver'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering']
)
