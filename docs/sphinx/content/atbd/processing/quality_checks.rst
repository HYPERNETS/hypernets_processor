.. quality - algorithm theoretical basis
   Author: pdv
   Email: pieter.de.vis@npl.co.uk
   Created: 07/02/2022

.. _quality:


Quality checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Throughout the processing chain, a number of quality checks are performed on the HYPERNETS data.
Each of the quality checks will be described in this section. First quality checks in common to water and land network will be described,
followed by sections with quality checks specific to only the water and land networks individually.


Common for both networks
---------------------------
L0
:::::
No quality checks are done on the L0 data itself, and all measured scans are provided.
The only checks that are performed are whether the metadata.txt file is appropriate and whether all required raw data files exists.
If either of these checks fail, an anomaly is raised (see :ref:`anomalies`).

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