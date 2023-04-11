from io import open
import os
import sys
from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.install import install

# Get package __version__.
# Same effect as "from s import __version__",
# but avoids importing the module which may not be installed yet:
__version__ = None
here = os.path.abspath(os.path.dirname(__file__))
with open("hypernets_processor/version.py") as f:
    exec(f.read())

# Get the long description from the README file
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


def pre_install_processor_setup():
    pass


def post_install_processor_setup():
    sys.argv = sys.argv[:1]
    from hypernets_processor.cli.setup_processor_cli import cli

    print("\nSet up processor\n----------------\n")
    cli()

    return None


class SetupDevelopCommand(develop):
    """
    Custom installation for development mode.
    """

    user_options = develop.user_options + [
        ("setup-processor", None, "Option to run additional processor setup."),
    ]

    def initialize_options(self):
        develop.initialize_options(self)
        self.setup_processor = 0

    def run(self):

        if self.setup_processor:
            pre_install_processor_setup()

        develop.run(self)

        if self.setup_processor:
            post_install_processor_setup()


class SetupInstallCommand(install):
    """
    Custom installation for installation mode
    """

    user_options = install.user_options + [
        ("setup-processor", None, "Option to run additional processor setup."),
    ]

    def initialize_options(self):
        install.initialize_options(self)
        self.setup_processor = 0

    def run(self):

        if self.setup_processor:
            pre_install_processor_setup()

        install.run(self)

        if self.setup_processor:

            post_install_processor_setup()


setup(
    name="hypernets_processor",
    version=__version__,
    description="Software for processing Hypernets field data",
    authors=["Pieter De Vis", "Clemence Goyens", "Sam Hunt"],
    long_description=long_description,
    author_email="Pieter.De.Vis@npl.co.uk",
    url="http://hypernets.eu",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    include_package_data=True,
    cmdclass={
        "develop": SetupDevelopCommand,
        "install": SetupInstallCommand,
    },
    package_data={
        "hypernets_processor": [
            os.path.join("etc", "processor.config"),
            os.path.join("etc", "scheduler.config"),
            os.path.join("etc", "jobs.txt"),
            os.path.join("etc", "job_template.config"),
            os.path.join("etc", "processor_land_defaults.config"),
            os.path.join("etc", "processor_water_defaults.config"),
            "calibration/calibration_files/*/*/*/*"],
    },
    install_requires=[
        "numpy",
        "netCDF4",
        "xarray==0.19.0",
        "schedule",
        "matplotlib",
        "pysolar",
        "dataset",
        "sqlalchemy==1.3.20",
        "sqlalchemy-utils",
        "punpy>=0.40.0",
        "matheo",
        "comet_maths>=0.19.10",
        "obsarray",
        "freezegun",
        "importlib-metadata==4.0.1",
        # "psycopg2",
    ],
    entry_points={
        "console_scripts": [
            "hypernets_sequence_processor = hypernets_processor.cli.sequence_processor_cli:cli",
            "hypernets_scheduler = hypernets_processor.cli.scheduler_cli:cli",
            "hypernets_processor_setup = hypernets_processor.cli.setup_processor_cli:cli",
            "hypernets_processor_job_init = hypernets_processor.cli.init_job_cli:cli"
        ],
    },
)
