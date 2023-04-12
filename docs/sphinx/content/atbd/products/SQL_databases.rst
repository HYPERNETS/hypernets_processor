.. sql - algorithm theoretical basis
   Author: Pieter De Vis
   Email: pieter.de.vis@npl.co.uk
   Created: 12/04/2023

.. _sql:


SQL Databases
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The hypernets_processor produces SQL Database entries to keep track of successfully processed sequences and anomalies
in the processing. These entries are combined into an archive database (for successful sequences), an anomaly database
(for sequences with processing or quality issues), and a metadata database (which stores the relevant metadata for
the listings in the other two databases). Each of these databases is stored in the SQLite format.

Archive Database
----------------------
SQLite database listing all succesfully processed data products, together with auxiliary information to enable queries
(product_name,datetime,sequence_name,site_id,system_id,product_level,product_path,rel_product_dir,sequence_path,
latitude,longitude,solar_zenith_angle_min,solar_zenith_angle_max,solar_azimuth_angle_min,solar_azimuth_angle_max,
viewing_zenith_angle_min,viewing_zenith_angle_max,viewing_azimuth_angle_min,viewing_azimuth_angle_max,percent_zero_flags).
Anomaly Database
----------------------
SQLite database recording occurrences of defined anomalies, e.g. incomplete sequence data, instrument failure etc.
(the different anomalies are listed on the :ref:`anomalies` page), together with auxiliary information to enable queries
(anomaly_id,sequence_name,sequence_path,site_id,datetime,rel_product_dir,product_level_last,product_path_last,
solar_zenith_angle_min,solar_zenith_angle_max,solar_azimuth_angle_min,solar_azimuth_angle_max,viewing_zenith_angle_min,
viewing_zenith_angle_max,viewing_azimuth_angle_min,viewing_azimuth_angle_max).

Metadata Database
----------------------
SQLite database of all network metadata, e.g. site info, instrument info etc. Contains all the metadata that is also present in the product files (stored in database to enable querying this information).
