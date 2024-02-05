.. config - algorithm theoretical basis
   Author: pdv
   Email: pieter.de.vis@npl.co.uk
   Created: 07/02/2022

.. _config:


Processing Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are a lot of options that can alter the details of how the data is processed.
These options can be controlled by changing the values in three .config files, which are each stored in the
HYPERNETS working directory (details on how to set up the initial values for each of these from the default templates
can be found on the :ref:`user_automated` page):

1. **processor.config**: This file has all the main options for the processing of the data, which are in common between all the different sites.
These options range from the paths to the different database and relevant folders, to controlling which files and plots are created (and their format), options for which measurement functions to use for each of the processing steps (as well as optional parameters for these steps) as well as options for the uncertainty processing and quality checks.

2. **job.config**: This file has site_specific options. There will be individual jobs for each of the sites, and each can be given their own options (which overwrite the options in processor.config if present).

3. **scheduler.config**: This file has the options for the scheduling of jobs (e.g. how often to check for new data,
logging path, whether or not to use parallel_processing, etc). We also note here that the different jobs that should
be included in the current run can be edited in the jobs.txt file in the HYPERNETS working directory.

Together these files allow for the detailed control of the processing of the HYPERNETS data.

Water processing configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default water processing configuration file can be found in `hypernets_processor/hypernets_processor/etc/processor_water_defaults.config`. When autonomous processing is launched, the configuration files are stored in the working directory in `processor.config`. These can be changed before launching the hypernets scheduler.
When add-hoc processing is launched, if the configuration parameters are not explicitly given in the command line (see :ref:`user_adhoc`), these are taken from the default processing configuration file for the considered network.
Default configuration files can be changed in `hypernets_processor/hypernets_processor/etc/processor_water_defaults.config`.

.. list-table:: [Site_specific]
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - siteid
     - offset_pan
     - offset_tilt
     - azimuth_switch
     - latitude
     - longitude
     - angle2use
   * - site id as given in the jobs list
     - offset pan with true North
     - offset tilt with Nadir
     - angle for which the system switches 180° relative to the requested angle
     - system latitude
     - system longitude
     - Ange used to compute the viewing geometry (i.e., pt_ref is the pan
        and tilt angles with the HYPSTAR as reference - use offset pan and tilt to retrieve viewing geometry with true North)
   * - e.g., VEIT
     - default 0°
     - default 0°
     - default 0°
     - latitude of site
     - longitude of site
     - pt_ref, pt_ask or pt_abs



.. list-table:: [Processor]
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - version
     - network
     - mcsteps
     - max_level
     - uncertainty_l1a
     - bad_wavelenth_ranges
     - verbose
   * - version number of the processor
     - network, i.e.,'l' for land network or 'w' for water network
     - number of photons for MC simulation for computation of the uncertainties (if 0, no uncertainties)
     - maximum level of processing
     - uncertainty computation of the level L1A
     - wavelength ranges for which uncertainties are expected to be high and ignored when triggering flags and anomalies
     - printing warnings and errors in terminal
   * -
     - l/w
     - 0 no uncertainties, suggested > 100 when uncertainties
     - default: L2A
     - default: False
     - default: 757.5-767.5, 1350-1390
     - default: False



.. list-table:: [Databases]
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - to_archive
     - metadata_db_url
     - archive_db_url
     - anomaly_db_url
   * - if True, the processor will save all products, anomalies and metadata in the archive, anomaly and metadata database.
     - path to sql database for the metadata
     - path to sql database for the archive
     - path to sql database for the anoamlies
   * - True/False
     - e.g., sqlite:////home/cgoyens/waterhypernet/HYPSTAR/Processed/metadata.db
     - e.g., sqlite:////home/cgoyens/waterhypernet/HYPSTAR/Processed/archive.db
     - e.g., sqlite:////home/cgoyens/waterhypernet/HYPSTAR/Processed/anomaly.db


.. list-table:: [Databases]
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - to_archive
     - metadata_db_url
     - archive_db_url
     - anomaly_db_url
   * - if True, the processor will save all products, anomalies and metadata in the archive, anomaly and metadata database.
     - path to sql database for the metadata
     - path to sql database for the archive
     - path to sql database for the anoamlies
   * - True/False
     - e.g., sqlite:////home/cgoyens/waterhypernet/HYPSTAR/Processed/metadata.db
     - e.g., sqlite:////home/cgoyens/waterhypernet/HYPSTAR/Processed/archive.db
     - e.g., sqlite:////home/cgoyens/waterhypernet/HYPSTAR/Processed/anomaly.db


.. list-table:: [Metadata]
   :widths: 25 50
   :header-rows: 1

   * - Configuration parameter
     - Definition
   * - comment
     - creator_name
     - creator_email
     - responsible_party
   * - Comment that should be added within the metadata of each processed file.
     - Name of the creator of the processed files.
     - Contact email of the creator.
     - Responsible party

.. list-table:: [Reading]
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
   * - model
   * - Model that should be followed by the processor to read the filenames of the raw SPE files.
   * - default: series_rep,series_id,vaa,azimuth_ref,vza,mode,action,it,scan_total,series_time


.. list-table:: [Quality]
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - l0_threshold
     - l0_discontinuity
     - bad_pointing_threshold_zenith
     - bad_pointing_threshold_azimuth
     - irradiance_zenith_treshold
     - n_valid_irr
     - n_valid_dark
     - n_valid_rad
     - irr_variability_percent
     - ld_variability_percent
     - diff_wave
     - diff_threshold
     - clear_sky_check
   * - Threshold for the maximum digital number over which the spectrum is considered to saturate (triggering saturation flag)
     - Threshold for the maximum difference in digital number between two neighbouring wavelengths (triggering discontinuity flag)
     - Maximum allowed difference between the requested (sequence protocol) and reported (by the system in the raw metadata file) viewing angle (in degrees, i.e., difference between pt_ref and pt_abs).
     - Maximum allowed difference between the requested (sequence protocol) and reported (by the system in the raw metadata file) azimuth angle (in degrees, i.e., difference between pt_ref and pt_abs).
     - Maximum allowed difference between the requested (sequence protocol) and reported (by the system in the raw metadata file) viewing angle for irradiance measurements (in degrees, i.e., difference between pt_ref and pt_abs).
     - Minimum number of valid irradiance scans for a single series.
     - Minimum number of valid dark scans for a single series.
     - Minimum number of valid radiance scans for a single series.
     - Threshold for the coefficient of variation (in percentage) between series of irradiance within a singe sequence (if only one series within a sequence this quality check is not raised).
     - Threshold for the coefficient of variation (in percentage) between series of downwelling radiance within a singe sequence
     - Wavelength used to check temporal variability in downwelling, upwelling radiance and irradiance (for water network only)
     - Threshold used for the temporal variability in downwelling, upwelling radiance and irradiance (for water network only) between scans in L1C data.
     - Compare irradiance series with simulated clear sky
   * - Default: 64000
     - Default: 10000
     - Default: 3
     - Default: 3
     - Default: 2
     - Default: 3
     - Default: 3
     - Default: 3
     - Default: 10
     - Default: 25
     - Default: 550
     - Default: 0.25
     - Default: True

.. list-table:: [Calibration]
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - hypstar_cal_number:120241
     - measurement_function_calibrate: StandardMeasurementFunction
   * - HYPSTAR ID number (usually overwritten by the ID number given in the metadata file from the sequence directory)
     - measurement function used for the calibration of the radiance and irradiance scans
   * - e.g., 120241
     - e.g., StandardMeasurementFunction

.. list-table:: [Interpolate]
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - measurement_function_interpolate_time
     - measurement_function_interpolate_time_skyradiance
     - measurement_function_interpolate_wav
     - measurement_function_interpolate
   * - Measurement function used to interpolate the irradiance scans at the timestamp of the upwelling radiance (for the computation of the reflectance).
     - Measurement function used to interpolate the downwelling radiance scans (for water network only) at the timestamp of the upwelling radiance (for the air-water interface reflectance correction).
     - Measurement function used to interpolate the irradiance scans at the wavelengths of the upwelling radiance.
   * - e.g., InterpolationTimeLinearCoscorrected
     - e.g., WaterNetworkInterpolationSkyRadianceLinearCoscorrected
     - e.g., InterpolationWavLinear

.. list-table:: [SurfaceReflectance]
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - measurement_function_surface_reflectance: WaterNetworkProtocol
     - measurement_function_water_leaving_radiance = WaterNetworkProtocolWaterLeavingRadiance
   * - Measurement function used for the computation of the surface reflectance.
     - Measurement function used for the computation of the water leaving radiance (for water network only).
   * - e.g., WaterNetworkProtocol
     - e.g., WaterNetworkProtocolWaterLeavingRadiance

.. list-table:: [WaterStandardProtocol]
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - protocol
     - n_upwelling_rad
     - n_downwelling_rad
   * - Protocol for the water network
     - Minimum number of the water network protocol for upwelling radiance
     - Minimum number of the water network protocol for downwelling radiance
   * - e.g., WaterNetworkProtocol
     - Default: 3
     - Default: 3

[Air_water_inter_correction]
rhof_option: Mobley1999
rhof_default: 0.0256
wind_ancillary: GDAS
wind_default: 2.0
wind_max_time_diff: 10
met_dir=/home/cgoyens/waterhypernet/Ancillary/GDAS/
thredds_url=https://thredds.rda.ucar.edu/thredds
rhymer_data_dir:./rhymer/data
rholut:rhoTable_AO1999

[VariabilityCheck]
## scale ed with cos sun zenith for variability check
ed_cos_sza: True
no_go_zone:/home/cgoyens/HYPSTAR/Ancillary/nogo_zone/azimuth_range.config

[SimSpecSettings]
similarity_test: False
similarity_correct: True
similarity_wr: 670
similarity_wp: 0.05
similarity_w1: 780
similarity_w2: 870
similarity_alpha: 0.523

[WaterFinalMeasurementTest]
test_measurement: True
test_sun_wave: 750
test_sun_threshold: 0.05
test_var_wave: 780
test_var_threshold: 0.10

[Output]
product_format = netcdf
remove_vars_strings:
remove_vars_strings_L2:
write_l0a: True
write_l0b: True
write_l1a: True
write_l1b: True
write_l1c: True
write_l2a: True

[Plotting]
plotting_format = png
plot_fontsize = 14
plot_legendfontsize = 10
plot_l0: True
plot_l1a: True
plot_l1a_diff: True
plot_l1b: True
plot_l1c: False
plot_l2a: True
plot_uncertainty: True
plot_correlation: False
plot_clear_sky_check=True