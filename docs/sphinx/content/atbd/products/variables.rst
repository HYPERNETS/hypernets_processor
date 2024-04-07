.. files - algorithm theoretical basis
   Author: seh2
   Email: sam.hunt@npl.co.uk
   Created: 6/11/20

.. _files:


HYPERNETS Product variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~
The different L0A-L2B NetCDF files contain a range of different
variables and metadata. The different product levels are detailed in
:ref:`files`. There are a number of main measurands (such as radiance,
irradiance, reflectance, water-leaving radiance,...), which each have uncertainty
variables for each of the components described in :ref:`uncertainty` as
well as error-correlation variables for the systematic uncertainty
components.

In addition to these there are coordinate variables,
wavelength and series/scans, as well as a number of common
variables (i.e., present in each of the data products) that provide
additional details about the measurement. Acquisition time,
viewing zenith and azimuth angle, solar zenith and azimuth
angle are examples of common variables with series or scans
as dimension. Bandwidth is also a common variable which has
the wavelength dimension. Then there are a few additional
variables such as the quality flag variable and variables
specifying the number of valid and total VNIR scans and
specifying the number of valid and total SWIR scans (for the
LANDHYPERNET network). The quality flag field consists of 32 bits. Every bit is related to the
absence or presence of a flag as described in :ref:`flags`.

There are also a number of variables that are only present in
some of the data products. For example, there is some additional
information in the L0A files, such as integration times, values of
the accelerometers, the requested and returned pan/tilt angles.
This information is propagated to the L1A and L0B files, but
not beyond.

There is also a range of metadata contained within the files.
For each variable, there is metadata such as the standard name,
long name, units and uncertainty components (where relevant).
The uncertainty variables will have additional metadata
describing their error correlation (see :ref:`uncertainty` and :ref:`using_hypernets`). Finally,
there is also a range of global metadata, describing
information about how, and when the data was processed,
what data files it used, information about the site (e.g.,
latitude and longitude) etc.

A full list of the available variables in provided in Table 1.

**Table 1: List of variables**

.. csv-table::
   :file: table_variables.csv
   :class: longtable
   :widths: 1 1 2 2 4 1
   :header-rows: 1





