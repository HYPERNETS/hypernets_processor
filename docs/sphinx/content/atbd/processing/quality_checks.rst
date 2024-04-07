.. quality - algorithm theoretical basis
   Author: pdv
   Email: pieter.de.vis@npl.co.uk
   Created: 07/02/2022

.. _quality:


Quality checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Throughout the different processing steps described in the
previous section, a number of quality checks are applied. These
quality checks are described below. When a given quality check fails,
there are two possible outcomes.

When the quality check is critical for having useful data, failure of
the quality check results in halting of the processing, and an
anomaly is raised and stored in the anomaly database.
See :ref:`anomalies` for which quality checks halt the
processing and what anomaly is raised.

On the other hand, there are some quality check where failure
does not necessarily mean the entire sequence cannot be used.
In some cases only part of the data might be affected (e.g., a
single series in the sequence), or in other cases the quality
check is only a warning the data should be used with caution.
In each of these cases, a quality flag is added to the data, and
the processing is continued. In some cases, it is still useful to
also raise an anomaly and store it in the anomaly database for
future reference. The anomalies are detailed in :ref:`anomalies1

The different quality checks are detailed below, the triggered
flags in :ref:`flags` and raised anomalies in :ref:`anomalies`.
First quality checks in common to water and land network will be described,
followed by sections with quality checks specific to only the water and land networks individually.


Common for both networks
---------------------------
L0A
:::::
While reading in the data, there are quality checks that verify
whether the metadata.txt file is appropriate and all required raw data
files exist. If this checks fails, an anomaly is raised (see Section 4.3) and
the processing halts. There is also a quality check which checks whether
the file with meteorological information exists. If it does not, an
anomaly is added to the SQL database, but the processing is
continued. In addition, for traceability, if the latitude and/or
longitude are unknown (i.e., not included in the metadata.txt file),
latitude and longitude are taken from the processor configuration file
and the ‘lon_default’ and/or ‘lat_default’ flags are triggered. Next, the
pointing accuracy of the pan/tilt is also verified. If the requested pan or
tilt angle differs by more than 3° with the effective pan or tilt angle, the
‘bad_pointing’ flag is raised for the given scan.

L1A
:::::
Before calibrating each of the individual scans in the L0 data, a number of quality checks is applied. 
The first of these checks looks for outliers by comparing each scan ot the other scans in the series. 
If the spectrally integrated signal of the scan is more than 3 sigma, or more that 25% (whichever is largest) 
removed from the mean, it is masked and not further used in the processing.
This process is repeated until convergance and applied to both the measured (ir)radiances as well as to the darks. 
In addition to this, a quality check is also performed to make sure the scan is not oversaturated 
(not too many pixels above an empirically defined threshold).
Scans not satisfying the quality checks are masked. A quality flag is added in the L1a data product to indicate which scan were masked (see :ref:`flags`). 
If all scans in a series are masked, an anomaly is raised (see :ref:`anomalies`).

L1B
:::::
No further quality checks are performed, but only scans that passed the L1A quality checks are used when taking the average.
In the future, we aim to add a quality check for the land network, checking the differences between the radiances for the VNIR and SWIR instruments forthe overlapping wavelengths.

L1C
:::::
Before interpolating the irradiances, a number of quality checks are applied to the irradiances. 
First, their viewing angles are checked (which must be 180°, with a tolerance of 2°, as irradiance measurements have to be pointing up).
Next, the irradiance is compared to a simulated clear-sky model. 

L2A
:::::
Currently, no further quality checks are applied. It is expected further checks will be added, either as part of the hypernets_processor, or in quality assurance pipelines per site.

Water Network quality checks
-----------------------------


Land Network quality checks
-----------------------------
There are currently no quality checks that are applied only to the land network (all land checks also apply to water network processing).