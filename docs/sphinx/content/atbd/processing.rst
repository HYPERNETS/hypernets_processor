.. processing - algorithm theoretical basis
   Author: Pieter De Vis
   Email: Pieter.De.Vis@npl.co.uk
   Created: 01/10/21

.. _processing:


Processing Algorithm Description
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this section, we describe the algorithms used within the **hypernets_processor** in order to process 
the raw data taken by the HYPSTAR instruments to reflectances products for both the WATERHYPERNET and LANDHYPERNET networks.
The HYPSTAR systems have been deployed at various sites, and collect measurements periodically and send these to the HYPERNETS servers for processing.
Within this ATBD, we focus on the processing of these automatically collected data.
The main goal of this processing is to produce quality-controlled (ir)radiance and reflectance data with well-characterised 
uncertainties for all automated sequences measured by the network, and make these available to the international user community.
The **hypernets_processor** produces various products ranging from L0 (raw data in NetCDF format) to L2A (reflectance products), 
with various intermediate products (L1A, L1b, L1c). For a full description of the data products see :ref:`products`.

In the following subsections, we will discuss the processing that is performed at each processing stages.
In the L0 processing, the HYPERNETS data is read in from the spe files together with metadata. 
The L1A stage consists of calibrating each of the scans and performing quality checks. 
The next stage (L1B) consists of averaging the scans per series (and combining VNIR and SWIR ranges for the land network). 
In the L1C processing the downwelling irradiances are spectrally and temporally interpolated. 
For the water network, L1C additionally consists of some intermediate steps such as e.g. temporally interpolating downwelling radiances, 
retrieving ancillary parameters and additional quality checks.
Then reflectances are calculated in the next stage (L2A) of the processing (together with water leaving radiances for water network).
Finally, there are some post-processing quality checks that happen periodicly and produce L1D (from L1B) and L2B (from L2A) files for public distribution.

Finally, we also detail the quality checks that were performed throughout the processing chain, as well as how uncertainties were propagated from product to product (and how the error-correlation was calculated).
The last subsection informs how the processing can be configured using various configuration files.
Links to each of the subsections can be found here:

.. toctree::
   :maxdepth: 1

   processing/hypernets_reader
   processing/calibrate
   processing/average
   processing/interpolate
   processing/surface_reflectance
   processing/post_processing
   processing/quality_checks
   processing/uncertainty_propagation
   processing/processing_config
   






