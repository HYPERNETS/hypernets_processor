.. hypernets_reader - algorithm theoretical basis
   Author: seh2
   Email: sam.hunt@npl.co.uk
   Created: 6/11/20

.. _hypernets_reader:


HYPERNETS Reader - Process to L0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Radiometer measurements are taken in a defined set of geometries called a sequence. Each geometry in a sequence is called a series, as it is composed of a set of repeat measurements called scans (see :ref:`data_structure`). A suite of different series thus creates a sequence. A sequence scheduler is used to order the different sequences that need to be executed during the day. Within the sequence scheduler each sequence is executed according to a start and end time
(HH:MM UTC with a 24 hours format and an automatic update of the system to UTC time when connecting to the internet), the time-lapse between each sequence (in minutes), the filename in which the sequence is defined and the number of times the sequence needs to be repeated.

Once a sequence has been completed succesfully, the data is sent to the server with the following data format, name convention and data structure:
   * Sequence directory:
      Data from a single sequence (see data structure) are contained in a SEQUENCE directory with the following name convention *SEQ[date of acquisition with format %Y%m%d]T[time of acquisition with format %H%M%S]*
   * Data structure:
      * *metadata.txt*:
         1. This files contains a header with PyxisVersion, DateTime, PI, Site Name, Latitude, Longitude, and, SN of the sensor, followed by,
         2. A full description of the sequence with for each series, the number of scans, the type of measurement (radiance/irradiance), wavelength range (VNIR/SWIR), and, the viewing geometry (relative to the sun, to the park position of the sensor and the North), followed by the name of the file containing the spectra.
      * *SPE files*:
         File containing the spectra concatenated per series (as mentioned in the metadata file)
      * *meteo.csv*:
         File with the measured relative humidity, light and temperature (auxilliary sensors)


The *data_io.hypernets_reader* module processes the raw dataset (in spe-binary datafile format) to
the L0 data product (readable netcdf file). The main function in this module is  read_sequence.
It calls (1) read_metadata to read the metadata file of the sequence (ASCII file),
(2) read_series to read the different scans concatenated per series in a single spe-binary data file.
According to the metadata file and the filename of the spe-binary file the processing reorders the
scans to L0 radiance, irradiance and black data and outputs for each of those a netcdf with the different scans. The *data_io.hypernets_reader* module also copies and renames the RGB images taken from the target and/or the sky during the sequence with the time of acquisition, the series number and the viewing and (relative) azimuth angle. All the L0 outputs also includes the processing time and the version number of the processor, for instance:

*'/BSBE/2022/01/01/HYPERNETS_W_BSBE_L0_RAD_20220101T1316_20220101T1615_v1.2.nc'*

*'/BSBE/2022/01/01/HYPERNETS_W_BSBE_L0_BLA_20220101T1316_20220101T1615_v1.2.nc'*

*'/BSBE/2022/01/01/HYPERNETS_W_BSBE_L0_IRR_20220101T1316_20220101T1615_v1.2.nc'*

*'/BSBE/2022/01/01/HYPERNETS_W_BSBE_IMG_20220101T1316_20220101T1615_006_140_90_v1.2.jpg'*

*'/BSBE/2022/01/01/HYPERNETS_W_BSBE_IMG_20220101T1316_20220101T1615_003_180_90_v1.2.jpg'*


