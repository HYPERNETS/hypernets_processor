.. files - algorithm theoretical basis
   Author: seh2
   Email: sam.hunt@npl.co.uk
   Created: 6/11/20

.. _files:


HYPERNETS Product files
~~~~~~~~~~~~~~~~~~~~~~~~~~~

File Name conventions
---------------------

The naming convention is intended to allow the unique identification of all product files and summarise the contents. It is composed of a defined sequence of data fields, separated by an underscore. For the HYPERNETS measurement data, the file name is composed as in the following way:

**SYSTEM_NETWORK_SITEID_LEVEL_TYPE_ACQUISITIONDATETIME_PROCESSINGDATETIME_VERSION.nc**

For the HYPSTAR calibration data, the file name is similar except that it includes the system_id and the date and time of the calibration.

**SYSTEM_NETWORK_SYSTEMID_TYPE_CALIBRATIONDATETIME_VERSION.nc**

For the RGB images taken during the measurements, the file name is similar except that it also includes the series ID, viewing and azimuth angle. 

**SYSTEM_NETWORK_SITEID_TYPE_ACQUISITIONDATETIME_PROCESSINGDATETIME_SERIESID_ZENITH_AZIMUTH_VERSION.nc**

The files are stored in the NetCDF data format and so have the extension “.nc” (except for the RGB images taken during the measurements by the instrument). The definition of the data fields and their allowed contents is described as follows:

**Table 1: File name conventions**

+----------------------+------------------------------------------------------------------------------------------------------+
|Field Name            | Description                                                                                          |
+======================+======================================================================================================+
| SYSTEM               | “HYPERNETS”                                                                                          |
+----------------------+------------------------------------------------------------------------------------------------------+
| NETWORK              | Name of product network, i.e., W and L for Water and Land network, respectively.                     |
+----------------------+------------------------------------------------------------------------------------------------------+
| SITEID               | Abbreviated site names defined in  Table 2.                                                          |
+----------------------+------------------------------------------------------------------------------------------------------+
| LEVEL                | Data processing Level as defined in  Table 3. For the RGB images the level is “IMG”.                 |
+----------------------+------------------------------------------------------------------------------------------------------+
| TYPE                 | Name of product type. Values may be abbreviated product type names defined in  Table 4               |
+----------------------+------------------------------------------------------------------------------------------------------+
| DATETIME_ACQUISITION | Denotes the acquisition end date and time as UTC, formatted as “YYYYMMDDTHHMM”.                      |
+----------------------+------------------------------------------------------------------------------------------------------+
| DATETIME_PROCESSING  | Denotes the processing date and time as UTC, formatted as “YYYYMMDDTHHMM”.                           |
+----------------------+------------------------------------------------------------------------------------------------------+
| ZENITH               |For the RGB images only – viewing nadir angle ranging from 0° (looking down) to 180° (looking up).    |
+----------------------+------------------------------------------------------------------------------------------------------+
| AZIMUTH              | For the RGB images only – relative azimuth angle between sun and sensor ranging from 0° to 360°.     |
+----------------------+------------------------------------------------------------------------------------------------------+
| VERSION              | Denotes data version number, formatted as “vXX.X”.                                                   |
+----------------------+------------------------------------------------------------------------------------------------------+


Example:
For version 1 of water network L1B product, acquired at Blankaart South at 11:30 on 4/2/2020 and processed at 11:30 on 5/2/2020, the filename should be:

*HYPERNETS_W_BSBE_L1B_RAD_20200204T1130_20200205T1130 _v01.0.nc*

Table 2 defines the abbreviated name convention applicable to the individual Hypernets sites. Site name convention is a 4 letter abbreviation [LLCC] with LL standing for the location abbreviation and CC for the country abbreviation.

**Table 2: Examples of site name conventions for water sites**

+---------+----------------------------------------------------------+
| Site ID | Site Name                                                |
+=========+==========================================================+
| BSBE    | Blankaart South, Belgium                                 |
+---------+----------------------------------------------------------+
| TCBE    | Thornton-C, Belgium                                      |
+---------+----------------------------------------------------------+
| ZBBE    | Zeebrugge MOW-1, Belgium                                 |
+---------+----------------------------------------------------------+
| MAFR    | MAGEST station, Gironde estuary, France                  |
+---------+----------------------------------------------------------+
| LPAR    | LA PLATA, La Plata River, Argentina                      |
+---------+----------------------------------------------------------+
| BEFR    | Lac de BERRE, France                                     |
+---------+----------------------------------------------------------+
| VEIT    | Aqua Alta Oceanographic Tower, Venice, Italy             |
+---------+----------------------------------------------------------+

Data level
----------
The end-to-end prototype processor takes the data from acquisition (raw data) to application of calibration and quality controls, computation of correction factors (e.g., Fresnel correction for water processing), temporal interpolation to coincident timestamps, processing to surface reflectance and averaging per series. To account for all these steps different data levels have been defined (see Table 3). See :ref:`data_structure <../processing/data_structure>` for a detailed explanantion of the terminology used.

**Table 3: List Hypernets Processor processing levels**

.. csv-table::
   :file: table_datalevel.csv
   :class: longtable
   :widths: 1 1 4 4
   :header-rows: 1


Product output format
----------------------
Files are in netcdf CF-convention version 1.8 format. Detailed file format per data level is given in Table 4.

**Table 4: Hypernets products definition including level and abvreviated names used for the file conventions, main variables and file scope.**

.. csv-table::
   :file: table_dataformat.csv
   :class: longtable
   :widths: 1 1 4 4 4
   :header-rows: 1













