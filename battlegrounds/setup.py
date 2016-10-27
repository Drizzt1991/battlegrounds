import codecs
import os
import re
import sys
from setuptools import setup, find_packages


with codecs.open(os.path.join(os.path.abspath(os.path.dirname(
        __file__)), 'client', '__init__.py'), 'r', 'latin1') as fp:
    try:
        version = re.findall(r"^__version__ = '([^']+)'\r?$",
                             fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')

if sys.version_info >= (3, 4):
    install_requires = []
else:
    install_requires = ['asyncio']


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()

args = dict(
    name='battlegrounds',
    version=version,
    description=('"Battlegrounds" test game'),
    long_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'],
    author='Taras Voinarovskyi',
    author_email='voyn1991@gmail.com',
    url='https://github.com/Drizzt1991/battlegrounds',
    packages=find_packages(exclude=('tests', 'manual tests')),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'client = client.main:main',
            'server = server.main:main',
        ],
    })
setup(**args)
