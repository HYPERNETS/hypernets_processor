from io import open
import os

from setuptools import find_packages, setup

# Get package __version__.
# Same effect as "from s import __version__",
# but avoids importing the module which may not be installed yet:
__version__ = None
here = os.path.abspath(os.path.dirname(__file__))
with open('hypernets_processor/version.py') as f:
    exec(f.read())

# Get the long description from the README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='hypernets_processor',
      version=__version__,
      description='Software for processing Hypernets field data',
      authors=['Sam Hunt', 'Clémence Goyens'],
      long_description=long_description,
      author_email='sam.hunt@npl.co.uk',
      url='http://hypernets.eu',
      packages=find_packages(exclude=['contrib', 'docs', 'tests']),
      include_package_data=True,
      package_data={
          'hypernets_processor': [os.path.join('etc', 'processor.config'),
                                  os.path.join('etc', 'scheduler.config'),
                                  os.path.join('etc', 'jobs.txt')],

      },
      install_requires=['numpy', 'netCDF4', 'xarray', 'schedule', 'matplotlib'],
      entry_points={
          'console_scripts': [
                'hypernets_processor =  hypernets_processor.cli.hypernets_processor_cli:cli'
          ],
                    }
      )
