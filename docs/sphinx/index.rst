.. hypernets_processor documentation master file, created by
   sphinx-quickstart on Fri Mar 20 17:28:40 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

hypernets_processor: Hypernets water and land network data processor
====================================================================

The **hypernets_processor** module is a Python software package to process the `HYPERNETS <http://hypernets.eu/from_cms/summary>`_ land and water network in-situ hyperspectral data to surface reflectance products for distribution to users. The HYPERNETS project is funded by the European Union’s Horizon 2020 research and innovation program under grant agreement No 775983.

There are two main use cases for the **hypernets_processor** module. The primary function of the software is the automated preparation of data retrieved from network sites for distribution to users. Additionally, the software may also be used for ad-hoc processing of particular field acquisitions, for example for testing instrument operation in the field.

This documentation aimed at both users and developers of the software, find the relevant sections below.

.. toctree::
   :maxdepth: 1
   :caption: User Guide

   content/users/adhoc
   content/users/using_hypernets
   content/users/data_distribution

.. toctree::
   :maxdepth: 1
   :caption: ATBD

   content/atbd/atbd
   content/atbd/definitions
   content/atbd/processing
   content/atbd/products

.. toctree::
   :maxdepth: 1
   :caption: Developer Guide

   content/developers/getting_started
   content/developers/automated
   content/developers/software_design

.. toctree::
   :maxdepth: 2
   :caption: API Documentation

   content/API/hypernets_processor
