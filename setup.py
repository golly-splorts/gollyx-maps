from setuptools import setup, find_packages
import glob
import os

with open('requirements.txt') as f:
    required = [x for x in f.read().splitlines() if not x.startswith("#")]
with open('requirements-dev.txt') as f:
    required_dev = [x for x in f.read().splitlines() if not x.startswith("#")]

# read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'Readme.md'), encoding='utf-8') as f:
    long_description = f.read()

# Note: the _program variable is set in __init__.py.
# it determines the name of the command line tool.
from gollyx_maps import __version__

setup(
    name='gollyx-maps',
    version=__version__,
    packages=['gollyx_maps'],
    package_data = {
      'gollyx_maps': ['data/*.json', 'b3s23_patterns/*.txt', 'b357s238_patterns/*.txt']
    },
    description='gollyx-maps is a package for turning cellular autonoma patterns into GollyX maps',
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
