.. products - algorithm theoretical basis
   Author: Pieter De Vis
   Email: Pieter.De.Vis@npl.co.uk
   Created: 01/10/21

.. _products:


Hypernets Products specification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **hypernets_processor** produces a number of different outputs. The first catagory of products consists of NetCDF files with the data products, i.e. the processed data at various stages of processing (e.g. calibrated radiances before averaging, interpolated irradiances, or final surface reflectances). Additionally, plots illustrating the data products, and allowing visual inspection, are produced as png, or pdf files (as specified in hypernets_processor configuration file). Finally, SQL Databases keep track of successfully processed sequences and anomalies in the processing. These entries are combined into an archive database (for successful sequences), an anomaly database (for sequences with processing or quality issues), and a metadata database (which stores the relevant metadata for the listings in the other two databases).

In the following subsections, we will first discuss the data structure and some of the key terminology for the HYPERNETS data. Next, we will detail the HYPERNETS Product files. We provide details on the file name conventions, data levels, and output format. Then, we will explain the various SQL Databases, and how they can be used. Finally, in the remaining subsections, we then provide further information on the included metadata, and provide explanations to each of the used flags and anomalies.



.. toctree::
   :maxdepth: 1

   products/product_files
   products/variables
   products/SQL_databases
   products/metadata 
   products/flags 
   products/anomalies 
   


