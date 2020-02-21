from setuptools import find_packages, setup

from os import path
from io import open

# Get package __version__.
# Same effect as "from s import __version__",
# but avoids importing the module which may not be installed yet:
__version__ = None
here = path.abspath(path.dirname(__file__))
with open('hypernets_processor/version.py') as f:
    exec(f.read())

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='hypernets_processor',
      version=__version__,
      description='Software for processing Hypernets field data',
      author='Sam Hunt',
      long_description=long_description,
      author_email='sam.hunt@npl.co.uk',
      url='http://hypernets.eu',
      packages=find_packages(exclude=['contrib', 'docs', 'tests']),
      install_requires=['numpy', 'netCDF4', 'xarray'],
      entry_points={
          'console_scripts': [
          ],
                    }
      )
