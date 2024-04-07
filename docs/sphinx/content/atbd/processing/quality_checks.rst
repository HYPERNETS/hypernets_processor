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
In some cases only part of the data might be affected (e.g. a
single series in the sequence), or in other cases the quality
check is only a warning the data should be used with caution.
In each of these cases, a quality flag is added to the data, and
the processing is continued. In some cases, it is still useful to
also raise an anomaly and store it in the anomaly database for
future reference. The anomalies are detailed in :ref:`anomalies`.

The different quality checks are detailed below, the triggered
flags in :ref:`flags` and raised anomalies in :ref:`anomalies`.

L0A: Read raw data
:::::::::::::::::::
While reading in the data, there are quality checks that verify
whether the metadata.txt file is appropriate and all required raw data
files exist. If these checks fail, an anomaly is raised (see :ref:`anomalies`) and
the processing halts. There is also a quality check which checks whether
the file with meteorological information exists. If it does not, an
anomaly is added to the SQL database, but the processing is
continued. In addition, for traceability, if the latitude and/or
longitude are unknown (i.e. not included in the metadata.txt file),
latitude and longitude are taken from the processor configuration file
and the ‘lon_default’ and/or ‘lat_default’ flags are triggered. Next, the
pointing accuracy of the pan/tilt is also verified. If the requested pan or
tilt angle differs by more than 3° with the effective pan or tilt angle, the
‘bad_pointing’ flag is raised for the given scan.

L1A: Check raw data prior to calibrating
:::::::::::::::::::::::::::::::::::::::::::
Before calibrating each of the individual scans in the
L0 data, a number of quality checks is applied. If the
spectrally integrated signal of a scan is more than 3 times
the standard deviation, or more than 25% (whichever is
largest) removed from the mean, it is masked and will not be
used when averaging the series. This process is repeated until
convergence and applied to the measured (ir)radiances and to
the darks. The L0 data is also checked for saturation (digital
number :math:`DN ≥ 64,000`) and for discontinuities (missing values or
:math:`\Delta DN > 10^4`). A flag is also added to the L1 data if any of the dark
scans have been masked by the above processes. Scans not
satisfying the quality checks are flagged, but no data are
removed at this stage.

L0B: Average valid scans
::::::::::::::::::::::::::
When averaging, only scans that passed the L1A quality
checks are used. There are a few quality checks that check the
number of scans being averaged is sufficient. By default, the
threshold number of scans is three. If there are fewer than three
scans for one of the dark, radiance or irradiance series, no reliable
uncertainty can be calculated, and the series is flagged. If less than
half of the radiance or irradiance scans of a series pass the L1A
checks, the series is flagged, as this likely indicates something has
gone wrong.

L1B: Check calibrated data is fit for purpose
::::::::::::::::::::::::::::::::::::::::::::::::
After calibrating the L0B file, we check all the required measurements
to form a standard sequence are included and have not been flagged by
the previous ‘not_enough_dark_scans’, ‘not_enough_rad_scans’ or
‘not_enough_irr_scans’ flags. If any series are missing or flagged, the
‘series_missing’ is added to all the series in the sequence. If there are no valid
radiance or irradiance measurements, the processing is halted.

Next, quality checks on the irradiance measurements are applied.
First, their viewing angles are checked (which must be 180°, with a
tolerance of 2°, as irradiance measurements have to be pointing up).
Next, the irradiance is compared to a simulated clear-sky model. This
clear-sky model is made using the libRadtran radiative transfer software
package (Emde et al., 2016), assuming its mid-latitude summer
standard atmosphere, its standard desert surface (for land sites)
and its standard ocean surface (for water sites). Note that the surface
does not make a big difference as it is only second-order effects that
affect the downwelling irradiance used in the clear-sky model. The
surface is assumed to be at sea-level and the TSIS solar irradiance model
is used (Coddington et al., 2021). Given the downwelling irradiance
measures the full hemisphere, the only relevant angle is the solar zenith
angle. A clear-sky model is calculated using solar zenith angles of 0°, 10°,
20°, 40°, 60°, 70° and 80°. These irradiance data are provided at 0.1 nm
resolution to the HYPERNETS_PROCESSOR.

When performing the clear sky quality check, the irradiance data
are band integrated to the HYPSTAR® bands (which vary slightly
from instrument to instrument), as defined by the calibration data,
using the `matheo tool <https://matheo.readthedocs.io/en/latest/>`_.
The measured HYPERNETS irradiances are
then scaled (assuming cosine response) to match the nearest solar
zenith angle among the provided clear sky models. In Figure 11, we
show an example of the clear sky checks applied to the irradiance.
We note that the clear sky models are not always very close, as a midlatitude
summer atmosphere at sea-level was used as opposed to a
more realistic site-specific model. Therefore this quality check only
fails if there are significant differences of more than 50% with the
clear-sky model (for more than 10% of the wavelength bands).
Overcast conditions consistently trigger this quality flag.
Then, there is a quality check verifying that the irradiance has
not changed more than 10% (after correcting for differences in
solar zenith angle) between the measurements at the start and
end of the sequence. At this stage the resulting irradiance series
are flagged and the L1B file is produced. However if this ‘variable_irradiance’
check is triggered the processing will be halted at the L1C stage.

There are also some quality checks on the uncertainties. These
check that there are no negative uncertainties and that less than 50%
of the random uncertainties (i.e., less than half of the spectral
channels) on radiance and irradiance have values below 100%
(this indicates corrupted or dark data, e.g., measurements at
night fail this check).

Land Network quality checks
-----------------------------
For the LANDHYPERNET network, there is an additional check
that there is no strong discontinuity (larger than 25%) between the
VNIR and SWIR parts of the spectrum for both radiances and
irradiances.

L1C: Check if all required data for L1C processing is valid
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
Before interpolating the irradiances, there are a number of
checks verifying the data is valid. If the ‘variable_irradiance’ flag
was raised in previous levels, we cannot perform reliable
interpolation and the processing is halted. Next, the processing is
halted if there are no valid series for either radiance or irradiance
(checking ‘not_enough_dark_scans’, ‘not_enough_irr_scans’, ‘not_enough_rad_scans’
or ‘vza_irradiance’ flags). When all irradiance
series have the ‘no_clear_sky_irradiance’ flag, the processing is
continued, as overcast products might still be useful to some
users (available by request). A flag is added to all series to
indicate this is a sequence without clear sky irradiance. No L1D/
L2B data will be produced (and thus this data will not be provided
publicly). When only one irradiance series is available (due to ‘vza_irradiance’
or missing measurements), the processing is continued,
and the same irradiance is used for every radiance series (instead of
temporally interpolating), with a correction for the changing solar
zenith angle throughout the sequence. A flag is added to the entire
sequence to indicate only one irradiance has been used.

Water Network quality checks
-----------------------------
For the WATERHYPERNET network, there are a number of
additional quality checks. First, similarly to the ‘variable_irradiance’
flag, it checks if the downwelling sky radiance, Ld, at 550 nm remains
constant over the entire sequence (i.e., coefficient of variation for Ld
(550) < 10%). Indeed, if Ld varies significantly between the start and the
end of the sequence, the downwelling sky radiance can not be temporally
interpolated to the timestamps of the Lu scans and the processing is
therefore halted. Note however that the threshold of 10% difference may
be subject to further research in order to select the best threshold. Next, an
anomaly (i.e., ‘l’) is raised and the processor is halted if the upwelling and
downwelling radiance pair does not have a similar pointing azimuth angle
(within 1° accuracy), or, if the viewing geometry does not satisfy θv for Ld
equals 180-θv for Lu (within 1° accuracy).

The processor also checks for the temporal variability within each
series. Scans for Ed, Lu and Ld at 550 nm, should not vary by more than
a certain threshold with their neighbouring scans (default threshold is
25%). Note, those flags are not expected to be raised as scans with high
temporal variability should have been removed by previous flags,
i.e., ‘outliers’ or ‘L0_discontinuty’ flags. However, these flags are kept
to ensure consistency with other common water network processing
(`Ruddick et al. 2016 <https://odnature.naturalsciences.be/downloads/publications/ruddick_et_al-2006-limnology_and_oceanography21.pdf>`_; Vansteenwegen et al., 2019).

The number of scans per series is important to assess the
uncertainties. Hence, if the number of scans, not flagged by ‘bad
pointing’, ‘outliers’, ‘L0_thresholds’, or ‘L0_discontinuity’, for Ed, Lu
and Ld is below a given threshold, an anomaly is raised, and the
processing is halted. The current default value is three which is a
compromise between shortening the duration of the sequences and
ensuring enough repeating measurements.

If the viewing geometry of the upwelling and downwelling
radiance measurements are outside the viewing geometry range
of the selected LUT for the ‘rhof_option’, the flag ‘rhof_default’ is
raised. Similarly, a ‘def_wind_flag’ is used to trace spectra processed
with a default wind speed value.

Finally, the flag ‘simil_fail’ is raised if the quality check applied
on the NIR similarity spectrum is not verified as suggested by
`Ruddick et al. (2016) <https://odnature.naturalsciences.be/downloads/publications/ruddick_et_al-2006-limnology_and_oceanography21.pdf>`_. Note, this flag should only be considered
for water types satisfying the NIR Similarity spectrum theory
(i.e., clear to moderately turbid waters).

L2A: Calculate reflectance
:::::::::::::::::::::::::::
Currently, no further quality checks are applied. For the
WATERHYPERNET network, water radiance and reflectance are
averaged only for the Lu scans which are not flagged for temporal
variability, i.e., ‘temp_variability_irr’ and ‘temp_variability_rad’, or
‘rhof_default’.

L2B: Site-specific quality checks
:::::::::::::::::::::::::::::::::::::
The site-specific quality checks range from angular masks,
i.e., viewing geometries that are expected to be affected by
shadows or part of the installation (such as a mast) in the
field-of-view, to quality checks that are very specific to the
surface for a given site (e.g., ensuring vegetation is measured
for the Wytham Woods UK (WWUK) site, or checking abnormal
high reflectance values over clear or low turbid waters). Such sitespecific
checks often use thresholds (determined from analysis of
the first months/year of data) checking the reflectance (or ratios
of reflectances, e.g., epsilon for water sites, or NDVI for vegetated
sites) at specific wavelengths. Additionally, the site owners can
provide specific date-time ranges to mask, e.g., because
something went slightly wrong during the deployment of the
instrument (e.g., alignment).
Another important quality check is that the surface reflectances
are compared to a time-series of similar measurements (matching
viewing geometry and time of day) at the same site, to identify
outliers so that they can be investigated. If these outliers are found to
come from invalid data, further quality checks can be added to
remove such cases.
The resulting site-specific masks are applied on a sequence-bysequence
basis to both L2A data (resulting in L2B dataset) and to the