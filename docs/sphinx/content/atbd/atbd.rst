.. atbd - algorithm theoretical basis
   Author: Pieter De Vis
   Email: Pieter.De.Vis@npl.co.uk
   Created: 01/10/21

.. _atbd:


Algorithm Theoretical Basis
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The processing algorithm for the `HYPERNETS <http://hypernets.eu/from_cms/summary>`_ network is called hypernets_processor. The hypernets_processor 
is a Python software package to process the HYPSTAR land and water in situ hyperspectral visible-near 
infrared (and short-wave infrared for the land unit) measurements from the HYPERNETS network to surface 
reflectance products for distribution to users. It is designed to convert the raw data collected from the measurement 
network under the standard measurement protocols to the designated products. We here describe the products 
being produced (in :ref:`products`), as well as the manner of their production (in :ref:`processing`). This document details the theoretical and 
practical implementation of the methods used. 

.. toctree::
   :maxdepth: 1
   :caption: ATBD

   content/atbd/definitions
   content/atbd/processing
   content/atbd/products
