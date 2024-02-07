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
   :widths: 10 20 10
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
   :widths: 10 20 10
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
   :widths: 10 20 10
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
   :widths: 10 20 10
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
   :widths: 10 20
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
   :widths: 10 20 10
   :header-rows: 1

   * - Configuration parameter
     - Definition
   * - model
   * - Model that should be followed by the processor to read the filenames of the raw SPE files.
   * - default: series_rep,series_id,vaa,azimuth_ref,vza,mode,action,it,scan_total,series_time


.. list-table:: [Quality]
   :widths: 10 20 10
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
   :widths: 10 20 10
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
   :widths: 10 20 10
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
   :widths: 10 20 10
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
   :widths: 10 20 10
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


.. list-table:: [Air_water_inter_correction]
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - rhof_option
     - rhof_default
     - wind_ancillary
     - wind_default
     - met_dir
     - thredds_url
     - rhymer_data_dir
     - rholut
   * - Option to be used for the correction of the air-water interface reflectance factor.
     - Default value to be used in case above method fails and/or if no method is given.
     - Source for wind speed to be used for the air-water interface reflectance factor.
     - Default wind speed value if above method fails and/or no wind speed is provided.
     - Path to directory with ancillary data files for wind speed. If `wind_ancillary` is set to GDAS and no wind speed is present for the given dat and location, wind speed is extracted from https://thredds.rda.ucar.edu/thredds and saved in the `met_dir` directory for later (re)processing.
     - URL for wind source if no wind speed is found for time and location in `met_dir`.
     - Data directory for ancillary data to be used within RHYMER (e.g., directory including LUT for air-water interface reflectance correction).
     - Name of LUT to be used to retrieve the air-water interface reflectance factor.
   * - e.g., Mobley1999
     - Default: 0.0256
     - e.g.,  GDAS
     - Default: 2.0
     - e.g., /waterhypernet/Ancillary/GDAS/
     - e.g., https://thredds.rda.ucar.edu/thredds
     - e.g., ./rhymer/data
     - e.g., rhoTable_AO1999


.. list-table:: [Air_water_inter_correction]
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - ed_cos_sza
     - no_go_zone
   * - Boolean wether or not the irradiance is normalized by the cosinus of the solar zenith angle before the above quality checks are applied (i.e., irr_variability_percent)
     - Place holder to include the path to an site specific configuration file
   * - True or flase
     - e.g., /waterhypernet/Ancillary/nogo_zone/azimuth_range.config (not used yet)


.. list-table:: [SimSpecSettings]
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - similarity_test
     - similarity_correct
     - similarity_wr
     - similarity_wp
     - similarity_w1
     - similarity_w2
     - similarity_alph
   * - Apply the NIR Similarity correction test (see Ruddick et al., 2005, DOI: 10.1117/12.615152)
     - Apply similarity correction
     - Reference wavelength to apply the NIR Similarity correction test (see Ruddick et al., 2005, DOI: 10.1117/12.615152).
     - Threshold to be used to apply the NIR Similarity correction test (see Ruddick et al., 2005, DOI: 10.1117/12.615152).
     - Reference wavelength 1 to apply the NIR Similarity Correction (see Ruddick et al., 2006 DOI: 10.2307/3841124).
     - Reference wavelength 2 to apply the NIR Similarity Correction (see Ruddick et al., 2006 DOI: 10.2307/3841124).
     - Similarity reflectance spectrum for the two wavelength, similarity_w1 and similarity_w2, to apply the NIR Similarity Correction (see Table 1 in Ruddick et al., 2006 DOI: 10.2307/3841124).
   * - Default: False
     - Default: True
     - Default: 670
     - Default: 0.05
     - Default: 780
     - Default: 870
     - Default: 0.523

.. list-table:: [WaterFinalMeasurementTest]
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - test_measurement
     - test_sun_wave
     - test_sun_threshold
     - test_var_wave
     - test_var_threshold
   * - Extra quality controls on final products to retain or reject spectra (placeholder, not used yet).
     - Wavelength to consider to check the Ld /Ed data (placeholder, not used yet).
     - Threshold to apply on the Ld/Ed ratio (placeholder, not used yet).
     - Wavelength to consider to check the final water reflectance data (placeholder, not used yet).
     - Threshold to apply on the final reflectance data (placeholder, not used yet).
   * - Default: True (placeholder, not used yet).
     - Default: 750 (placeholder, not used yet).
     - Default: 0.05 (placeholder, not used yet).
     - Default: 780 (placeholder, not used yet).
     - Default: 0.10 (placeholder, not used yet).


.. list-table:: [Output]
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - product_format
     - remove_vars_strings
     - remove_vars_strings_L2
     - write_l0a
     - write_l0b
     - write_l1a
     - write_l1b
     - write_l1c
     - write_l2a
   * - Product format for output file
     - List of names from variables to remove from output files
     - List of names from variables to remove from L2 files
     - Write output file L0A
     - Write output file L0B
     - Write output file L1A
     - Write output file L1B
     - Write output file L1C
     - Write output file L2A
   * - default: netcdf
     -
     -
     - default: True
     - default: True
     - default: True
     - default: True
     - default: True
     - default: True

.. list-table:: [Plotting]
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - plotting_format
     - plot_fontsize
     - plot_legendfontsize
     - plot_l0
     - plot_l1a
     - plot_l1a_diff
     - plot_l1b
     - plot_l1c
     - plot_l2a
     - plot_uncertainty
     - plot_correlation
     - plot_clear_sky_check
   * - Format of the figures for the different plots
     - Fontsize for the axis of the plots
     - Fontsize for the legends in the plots
     - Plotting L0 data
     - Plotting L1A data
     - Plotting differences in L1A data
     - Plotting L1B data
     - Plotting L1C data
     - Plotting L2A data
     - Plotting uncertainties
     - Plotting error correlation matrices
     - Plotting the irradiance L1B data with the clear-sky simulations used for the clear-sky check.
   * - default: png
     - default: 14
     - default: 10
     - default: True
     - default: True
     - default: True
     - default: True
     - default: False
     - default: True
     - default: True
     - default: False
     - default: True
