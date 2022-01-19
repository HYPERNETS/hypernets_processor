.. interpolate - algorithm theoretical basis
   Author: Pieter De Vis
   Email: Pieter.De.Vis@npl.co.uk
   Created: 01/10/2021

.. _interpolate:


Interpolating - Process to L1C
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Water Network
--------------

.. surface_reflectance - algorithm theoretical basis
   Author: Pieter De Vis
   Email: Pieter.De.Vis@npl.co.uk
   Created: 01/10/2021

.. _surface_reflectance:


Surface Reflectance - Process to L2A
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Water Network
--------------

To process the water network data, the hypernets processor includes RHYMER ("Reliable processing of HYperspectral MEasurement of Radiance", version 20190718 on 16/10/2020, written by Quinten Vanhellemont and adapted for the HYPSTAR by Clémence Goyens). RHYMER provides all the required functions to process the above water measurements (currently including Mobley 1999 and 2015 and Ruddick et al., 2006 for the Fresnel correction). 
**Note the funtion process to L1C takes as input the L1A files and not the L1B as it checks for additional quality flags and scans are averaged per series afterwards**

1. Quality check of the scans:

The first function in the rhymer_hypstar.process_l1c module performs a quality check per series, i.e., it assigns flags to each spectrum showing a temporal jump of more than a given threshold (25% is the default) at 550 nm. 

2. Parse cycle:

The second function parses the cycle, i.e., it separates downwelling and upwelling radiance, investigate if all required angles are present and if there are coincident upwelling and downwelling radiance measurements for the retrieval of the water leaving radiance. 

3. Wavelength interpolation:

Next, since the irradiance and radiance measurements have a slight shift in wavelength, first a spectral interpolation is performed to fit the irradiance measurements to the radiance wavelengths. 

4. Averaging downwelling irradiance and radiance series:

Downwelling radiance and irradiance (as well as uncertainties) are averaged per series.

5. Temporal interpolation

Downwelling irradiance and radiance are interpolated to the timestamp of the upwelling radiance. For each upwelling radiance measurement, a time coincident downwelling radiance and irradiance measurement is retrieved. Uncertainties are computed for the interpolation of the downwelling radiance and irradiance measurements, respectively. The default measurement function returns interpolated downwelling irradiance or radiance values at the upwelling radiance time stamps using linear interpolation (see  https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html)

6. Ancillary data retrieval:

All the required parameters for the computation of the water leaving radiance and reflectance, i.e., wind speed, ws, and the effective fresnel reflectance coefficient (:math:`\rho(\theta,\theta_0,\Delta\phi,ws)` are retrived. Wind speed may be taken from, e.g., a default value (e.g., 2m/s), in situ measurements, ancilliary datasets such as NCEP Met data. Similarly, the Fresnel reflectance coefficient can be extracted from (1) different look-up tables (Mobley 1999; 2015, default is Mobley 1999)), (2) set to a default value, estimated as a function of wind speed (e.g., Ruddick et al. 2006). The  configuration files (job and processing) determine which option is used for the processing (see Section 6.9, e.g., fresnel_option: Ruddick2006). 


7. Intermediate L1C surface reflectance:

L1C processing also includes the retrieval of the water leaving radiance and reflectance for each single upwelling radiance scan. 






Land Network
--------------

TBC - Pieter
