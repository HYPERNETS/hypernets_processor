.. getting_started - user introduction page
   Author: seh2
   Email: sam.hunt@npl.co.uk
   Created: 23/3/20

.. _users_getting_started:

Getting Started
===============

Dependencies
------------

The hypernets_processor has the following dependencies:

* Python (3.7 or above)
* `xarray <http://xarray.pydata.org/en/stable/>`_
* `netcdf4 <https://unidata.github.io/netcdf4-python/netCDF4/index.html>`_
* `numpy <https://numpy.org>`_
* `matplotlib <https://matplotlib.org>`_

Installation
------------

First clone the project repository from GitHub::

   $ git clone https://github.com/HYPERNETS/hypernets_processor.git

Then install the module with pip::

   $ pip install hypernets_processor/

This should automatically install the dependencies.

If you are installing the module to contribute to developing it is recommended you follow the install instructions on the :ref:`developers` page.

Usage
-----

There are two main use cases for the hypernets_processor package. The primary function of the software is the regular automated processing of data retrieved from Hypernets field sites. Additionally, the software may also be used for ad-hoc processing of particular field acquisitions, for example for testing instrument operation in the field. For information on each these use cases click on one of the following links:

* :ref:`use_field`
* :ref:`use_processing`
