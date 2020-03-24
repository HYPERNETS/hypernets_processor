.. getting_started - developer introduction page
   Author: seh2
   Email: sam.hunt@npl.co.uk
   Created: 23/3/20

.. _developers_getting_started:

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

In your development python environment install the module in develop mode::

   $ pip install -e hypernets_processor/

This will allow you to edit and call the code where it is, avoiding having to re-install every time you make changes. Dependencies should automatically be installed by pip.

Contributing to Development
---------------------------

The software is defined by the following:

* The processing algorithm is defined in the :ref:`atbd` section.
* The software design is defined in the :ref:`software_design` section.

Tasks are then organised in the GitHub `project board <https://github.com/HYPERNETS/hypernets_processor/projects/1>`_. Discuss how you can contribute to this with either Sam or Clémence :)


