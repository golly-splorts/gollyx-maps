from setuptools import setup, find_packages
import glob
import os

with open('requirements.txt') as f:
    required = [x for x in f.read().splitlines() if not x.startswith("#")]

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'Readme.md'), encoding='utf-8') as f:
    long_description = f.read()

# Note: the _program variable is set in __init__.py.
# it determines the name of the command line tool.
from golly_maps import __version__

setup(
    name='golly-maps',
    version=__version__,
    packages=['golly_maps'],
    package_data = {
      'golly_maps': ['data/*.json', 'patterns/*.txt']
    },
    description='golly-maps is a core package for generating map patterns for Golly',
    url='https://golly.life',
    author='Ch4zm of Hellmouth',
    author_email='ch4zm.of.hellmouth@gmail.com',
    license='MIT',
    install_requires=required,
    tests_require=required_dev,
    keywords=[],
    zip_safe=False,
    long_description=long_description,
    long_description_content_type='text/markdown'
)
