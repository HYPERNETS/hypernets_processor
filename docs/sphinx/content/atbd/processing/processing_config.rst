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


**Table 1: Site_specific**

.. list-table::
   :widths: 10 20 10
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - siteid
     - site id as given in the jobs list
     - e.g., VEIT
   * - offset_pan
     - offset pan with true North
     - default 0°
   * - offset_tilt
     - offset tilt with Nadir
     - default 0°
   * - azimuth_switch
     - angle for which the system switches 180° relative to the requested angle
     - default 0°
   * - latitude
     - system latitude
     - latitude of site
   * - longitude
     - system longitude
     - longitude of site
   * - angle2use
     - Ange used to compute the viewing geometry (i.e., pt_ref is the pan and tilt angles with the HYPSTAR as reference - use offset pan and tilt to retrieve viewing geometry with true North)
     - pt_ref, pt_ask or pt_abs

**Table 2: Processor**

.. list-table::
   :widths: 10 20 10
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - version
     - version number of the processor
     -
   * - network
     - network, i.e.,'l' for land network or 'w' for water network
     - l/w
   * - mcsteps
     - number of photons for MC simulation for computation of the uncertainties (if 0, no uncertainties)
     - 0 no uncertainties, suggested > 100 when uncertainties
   * - max_level
     - maximum level of processing
     - default: L2A
   * - uncertainty_l1a
     - uncertainty computation of the level L1A
     - default: False
   * - bad_wavelenth_ranges
     - wavelength ranges for which uncertainties are expected to be high and ignored when triggering flags and anomalies
     - default: 757.5-767.5, 1350-1390
   * - verbose
     - printing warnings and errors in terminal
     - default: False


**Table 3: Databases**

.. list-table::
   :widths: 10 20 10
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - to_archive
     - if True, the processor will save all products, anomalies and metadata in the archive, anomaly and metadata database.
     - True/False
   * - metadata_db_url
     - path to sql database for the metadata
     - e.g., sqlite:///waterhypernet/HYPSTAR/Processed/metadata.db
   * - archive_db_url
     - path to sql database for the archive
     - e.g., sqlite:///waterhypernet/HYPSTAR/Processed/archive.db
   * - anomaly_db_url
     - path to sql database for the anoamlies
     - e.g., sqlite:///waterhypernet/HYPSTAR/Processed/anomaly.db

**Table 4: Metadata**

.. list-table::
   :widths: 10 20
   :header-rows: 1

   * - Configuration parameter
     - Definition
   * - comment
     - Comment that should be added within the metadata of each processed file.
   * - creator_name
     - Name of the creator of the processed files.
   * - creator_email
     - Contact email of the creator.
   * - responsible_party
     - Responsible party

**Table 5: Reading**

.. list-table::
   :widths: 10 20 10
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - model
     - Model that should be followed by the processor to read the filenames of the raw SPE files.
     - default: series_rep, series_id, vaa, azimuth_ref, vza, mode, action, it, scan_total, series_time


**Table 6: Quality**

.. list-table::
   :widths: 10 20 10
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - l0_threshold
     - Threshold for the maximum digital number over which the spectrum is considered to saturate (triggering saturation flag)
     - Default: 64000
   * - l0_discontinuity
     - Threshold for the maximum difference in digital number between two neighbouring wavelengths (triggering discontinuity flag)
     - Default: 10000
   * - bad_pointing_threshold_zenith
     - Maximum allowed difference between the requested (sequence protocol) and reported (by the system in the raw metadata file) viewing angle (in degrees, i.e., difference between pt_ref and pt_abs).
     - Default: 3
   * - bad_pointing_threshold_azimuth
     - Maximum allowed difference between the requested (sequence protocol) and reported (by the system in the raw metadata file) azimuth angle (in degrees, i.e., difference between pt_ref and pt_abs).
     - Default: 3
   * - irradiance_zenith_treshold
     - Maximum allowed difference between the requested (sequence protocol) and reported (by the system in the raw metadata file) viewing angle for irradiance measurements (in degrees, i.e., difference between pt_ref and pt_abs).
     - Default: 2
   * - n_valid_irr
     - Minimum number of valid irradiance scans for a single series.
     - Default: 3
   * - n_valid_dark
     - Minimum number of valid dark scans for a single series.
     - Default: 3
   * - n_valid_rad
     - Minimum number of valid radiance scans for a single series.
     - Default: 3
   * - irr_variability_percent
     - Threshold for the coefficient of variation (in percentage) between series of irradiance within a singe sequence (if only one series within a sequence this quality check is not raised).
     - Default: 10
   * - ld_variability_percent
     - Threshold for the coefficient of variation (in percentage) between series of downwelling radiance within a singe sequence
     - Default: 25
   * - diff_wave
     - Wavelength used to check temporal variability in downwelling, upwelling radiance and irradiance (for water network only)
     - Default: 550
   * - diff_threshold
     - Threshold used for the temporal variability in downwelling, upwelling radiance and irradiance (for water network only) between scans in L1C data.
     - Default: 0.25
   * - clear_sky_check
     - Compare irradiance series with simulated clear sky
     - Default: True


**Table 7: Calibration**

.. list-table::
   :widths: 10 20 10
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - hypstar_cal_number
     - HYPSTAR ID number (usually overwritten by the ID number given in the metadata file from the sequence directory)
     - e.g., 120241
   * - measurement_function_calibrate
     - measurement function used for the calibration of the radiance and irradiance scans
     - e.g., StandardMeasurementFunction

**Table 8: Interpolate**

.. list-table::
   :widths: 10 20 10
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - measurement_function_interpolate_time
     - Measurement function used to interpolate the irradiance scans at the timestamp of the upwelling radiance (for the computation of the reflectance).
     - e.g., InterpolationTimeLinearCoscorrected
   * - measurement_function_interpolate_time_skyradiance
     - Measurement function used to interpolate the downwelling radiance scans (for water network only) at the timestamp of the upwelling radiance (for the air-water interface reflectance correction).
     - e.g., WaterNetworkInterpolationSkyRadianceLinearCoscorrected
   * - measurement_function_interpolate_wav
     - Measurement function used to interpolate the irradiance scans at the wavelengths of the upwelling radiance.
     - e.g., InterpolationWavLinear

**Table 9: SurfaceReflectance**

.. list-table::
   :widths: 10 20 10
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - measurement_function_surface_reflectance
     - Measurement function used for the computation of the surface reflectance.
     - e.g., WaterNetworkProtocol
   * - measurement_function_water_leaving_radiance
     - Measurement function used for the computation of the water leaving radiance (for water network only).
     - e.g., WaterNetworkProtocolWaterLeavingRadiance

**Table 10: WaterStandardProtocol**

.. list-table::
   :widths: 10 20 10
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - protocol
     - Protocol for the water network
     - e.g., WaterNetworkProtocol
   * - n_upwelling_rad
     - Minimum number of the water network protocol for upwelling radiance
     - Default: 3
   * - n_downwelling_rad
     - Minimum number of the water network protocol for downwelling radiance
     - Default: 3

**Table 11: Air_water_inter_correction**

.. list-table::
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - rhof_option
     - Option to be used for the correction of the air-water interface reflectance factor.
     - e.g., Mobley1999
   * - rhof_default
     - Default value to be used in case above method fails and/or if no method is given.
     - Default: 0.0256
   * - wind_ancillary
     - Source for wind speed to be used for the air-water interface reflectance factor.
     - e.g.,  GDAS
   * - wind_default
     - Default wind speed value if above method fails and/or no wind speed is provided.
     - Default: 2.0
   * - met_dir
     - Path to directory with ancillary data files for wind speed. If `wind_ancillary` is set to GDAS and no wind speed is present for the given dat and location, wind speed is extracted from https://thredds.rda.ucar.edu/thredds and saved in the `met_dir` directory for later (re)processing.
     - e.g., /waterhypernet/Ancillary/GDAS/
   * - thredds_url
     - e.g., https://thredds.rda.ucar.edu/thredds
     - URL for wind source if no wind speed is found for time and location in `met_dir`.
   * - rhymer_data_dir
     - Data directory for ancillary data to be used within RHYMER (e.g., directory including LUT for air-water interface reflectance correction).
     - e.g., ./rhymer/data
   * - rholut
     - Name of LUT to be used to retrieve the air-water interface reflectance factor.
     - e.g., rhoTable_AO1999

**Table 12: VariabilityCheck**

.. list-table::
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - ed_cos_sza
     - Boolean wether or not the irradiance is normalized by the cosinus of the solar zenith angle before the above quality checks are applied (i.e., irr_variability_percent)
     - True or flase
   * - no_go_zone
     - Place holder to include the path to an site specific configuration file
     - e.g., /waterhypernet/Ancillary/nogo_zone/azimuth_range.config (not used yet)

**Table 13: SimSpecSettings**

.. list-table::
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - similarity_test
     - Apply the NIR Similarity correction test (see Ruddick et al., 2005, DOI: 10.1117/12.615152)
     - Default: False
   * - similarity_correct
     - Apply similarity correction
     - Default: True
   * - similarity_wr
     - Default: 670
     - Reference wavelength to apply the NIR Similarity correction test (see Ruddick et al., 2005, DOI: 10.1117/12.615152).
   * - similarity_wp
     - Threshold to be used to apply the NIR Similarity correction test (see Ruddick et al., 2005, DOI: 10.1117/12.615152).
     - Default: 0.05
   * - similarity_w1
     - Reference wavelength 1 to apply the NIR Similarity Correction (see Ruddick et al., 2006 DOI: 10.2307/3841124).
     - Default: 780
   * - similarity_w2
     - Default: 870
     - Reference wavelength 2 to apply the NIR Similarity Correction (see Ruddick et al., 2006 DOI: 10.2307/3841124).
   * - similarity_alph
     - Similarity reflectance spectrum for the two wavelength, similarity_w1 and similarity_w2, to apply the NIR Similarity Correction (see Table 1 in Ruddick et al., 2006 DOI: 10.2307/3841124).
     - Default: 0.523

**Table 14: WaterFinalMeasurementTest**

.. list-table::
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - test_measurement
     - Extra quality controls on final products to retain or reject spectra (placeholder, not used yet).
     - Default: True (placeholder, not used yet).
   * - test_sun_wave
     - Wavelength to consider to check the Ld /Ed data (placeholder, not used yet).
     - Default: 750 (placeholder, not used yet).
   * - test_sun_threshold
     - Threshold to apply on the Ld/Ed ratio (placeholder, not used yet).
     - Default: 0.05 (placeholder, not used yet).
   * - test_var_wave
     - Wavelength to consider to check the final water reflectance data (placeholder, not used yet).
     - Default: 780 (placeholder, not used yet).
   * - test_var_threshold
     - Threshold to apply on the final reflectance data (placeholder, not used yet).
     - Default: 0.10 (placeholder, not used yet).

**Table 15: Output**

.. list-table::
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - product_format
     - Product format for output file
     - default: netcdf
   * - remove_vars_strings
     - List of names from variables to remove from output files
     -
   * - remove_vars_strings_L2
     - List of names from variables to remove from L2 files
     -
   * - write_l0a
     - Write output file L0A
     - default: True
   * - write_l0b
     - Write output file L0B
     - default: True
   * - write_l1a
     - Write output file L1A
     - default: True
   * - write_l1b
     - Write output file L1B
     - default: True
   * - write_l1c
     - Write output file L1C
     - default: True
   * - write_l2a
     - Write output file L2A
     - default: True

**Table 16: Plotting**

.. list-table::
   :widths: 25 50 25
   :header-rows: 1

   * - Configuration parameter
     - Definition
     - Options/example
   * - plotting_format
     - Format of the figures for the different plots
     - default: png
   * - plot_fontsize
     - Fontsize for the axis of the plots
     - default: 14
   * - plot_legendfontsize
     - Fontsize for the legends in the plots
     - default: 10
   * - plot_l0
     - Plotting L0 data
     - default: True
   * - plot_l1a
     - Plotting L1A data
     - default: True
   * - plot_l1a_diff
     - Plotting differences in L1A data
     - default: True
   * - plot_l1b
     - Plotting L1B data
     - default: True
   * - plot_l1c
     - Plotting L1C data
     - default: True
   * - plot_l2a
     - Plotting L2A data
     - default: True
   * - plot_uncertainty
     - Plotting uncertainties
     - default: True
   * - plot_correlation
     - Plotting error correlation matrices
     - default: False
   * - plot_clear_sky_check
     - Plotting the irradiance L1B data with the clear-sky simulations used for the clear-sky check.
     - default: True
