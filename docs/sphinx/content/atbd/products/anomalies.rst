.. anomalies - algorithm theoretical basis
   Author: Pieter De Vis
   Email: pieter.de.vis@npl.co.uk
   Created: 12/04/2023

.. _anomalies:


Anomalies (processing errors)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are a number of anomalies that are defined to track where there are issues in the processing of the data.
Each of the anomalies is identified with a letter or combination of letters (see table below).
Some of these anomalies will raise an error (e.g. metadata file missing), and cause the processing of the data to be stopped (as indicated by column in the table).
Other anomalies (e.g. no_clear_sky_sequence) indicate an issue, but don't halt the processing of the data (e.g. measurements where the clear sky check failed (i.e. overcast conditions) might still be useful to some users).
In such cases, a quality flag is added to the data so that users can easily identify the affected sequences without having to look in the anomaly database.
The different quality flags are described on the :ref:`flags` page.

The following table lists the different anomalies, their description and whether they stop the processing.

**Table 1: Anomalies description**

.. csv-table::
   :file: table_anomalies.csv
   :class: longtable
   :widths: 1 2 1 1 5 1 1
   :header-rows: 1
