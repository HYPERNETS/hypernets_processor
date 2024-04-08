.. software_design - defines design of software
   Author: seh2
   Email: sam.hunt@npl.co.uk
   Created: 23/3/20

.. _version_note:

Version Notes
===============

The version number is made up of two numbers. The first
indicates the major version number. Changes to this number
indicate significant changes and improvements to the code, and
major changes to the datafiles. The second number, called the minor
version, is incremented when there are minor feature changes or
notable fixes which do not significantly change how the data
products should be used.

V2.0
------------
The current version of the HYPERNETS_PROCESSOR is v2.0. This is
the first version that is intended for operational use. This version is described in `De Vis et al. (2024a)<https://doi.org/10.3389/frsen.2024.1347230>`_.

Compared to the v1.0, there are a few changes in the
v2.0 HYPERNETS_PROCESSOR worth noting, so that any HYPERNETS
results using the v1.0 data products can be understood.

• The first important difference is in the definition of the
  viewing azimuth angles, which have changed by 180° in
  order to be consistent with satellite viewing azimuth angles
  in v2.0 (see :ref:`data_structure`). The pointing azimuth angles in
  v2.0 are equal to the viewing azimuth angles in v1.0.
  Pointing azimuth angles are mainly of interest for the
  WATERHYPERNET network as it is commonly used
  (Ruddick et al., 2019, and references therein) to compute
  the relative azimuth angles.

• Uncertainty propagation is now consistently applied to all
  WATERHYPERNET products, in the same way as for the
  LANDHYPERNET network.

• Output files and their names have slightly changed, e.g. there
  are now L0A and L0B files as opposed to only L0 files, and, the
  relative azimuth angle, used for the approximation of the airwater
  interface reflection factor within the
  WATERHYPERNET network, is also added to the L1C and
  L2A product names.

• Reflectance files with site specific quality checks applied are
  called L2B files in v2.0, as opposed to L2A
  files in v1.0. These are the main files to be distributed.

• There were many minor changes (e.g. to the metadata and the
  quality checks) that are not worth noting individually but do
  make a difference to the produced HYPERNETS products.

V1.0
--------
This version was used to produce the first public dataset on Zenodo.

Beta
-----
This version is described in `Goyens et al. (2021)<https://doi.org/10.1109/IGARSS47720.2021.9553738>`_


