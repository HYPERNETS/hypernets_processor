.. interpolate - algorithm theoretical basis
   Author: Pieter De Vis
   Email: Pieter.De.Vis@npl.co.uk
   Created: 01/10/2021

.. _interpolate:


Interpolating - Process to L1C
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Water Network
--------------
To process the water network data, the hypernets processor includes RHYMER ("Reliable processing of HYperspectral MEasurement of Radiance", version 20190718 on 16/10/2020, written by Quinten Vanhellemont). RHYMER provides all the required functions to process the above water measurements (currently including Mobley 1999 and 2015 and Ruddick et al., 2006 for the Fresnel correction). It includes 4 submodules:

1. Rhymer – process L1b:

   The first function in the rhymer_hypstar.process_l1b  module performs a quality check per series, i.e., it assigns flags to each spectrum showing a temporal jump of more than a given threshold (25% is the default) at 550 nm. The second function parses the cycle, i.e., it separates downwelling and upwelling radiance, investigate if all required angles are present and if there are coincident upwelling and downwelling radiance measurements for the retrieval of the water leaving radiance. Next, since the irradiance and radiance measurements have a slight shift in wavelength, first a spectral interpolation is performed to fit the irradiance measurements to the radiance wavelengths. After, downwelling irradiance and radiance are interpolated to the timestamp of the upwelling radiance (see function interpolate). Therefore, downwelling radiance and irradiance (as well as uncertainties) are first averaged per series (see function average). Next, averages per series are interpolated in time. Hence, for each upwelling radiance measurement (target radiance or total radiance), a time coincident downwelling radiance and irradiance measurement is retrieved. Uncertainties are computed for the interpolation of the downwelling radiance and irradiance measurements, respectively. The default measurement function returns interpolated downwelling irradiance or radiance values at the upwelling radiance time stamps using linear interpolation (see  https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html)

2. Rhymer – process L1c:

   Level L1c data is an intermediate step consisting to retrieve all the required parameters for the computation of the water leaving radiance and reflectance, i.e., wind speed, ws, and the effective fresnel reflectance coefficient (:math:`\rho(\theta,\theta_0,\Delta\phi,ws)`. Wind speed may be taken from, e.g., a default value, in situ measurements, ancilliary datasets such as NCEP Met data. Similarly, the Fresnel reflectance coefficient can be extracted from different look-up tables (Mobley 1999; 2015)), set to a default value, estimated as a function of wind speed (e.g., Ruddick et al. 2006). The  configuration files (job and processing) determine which option is used for the processing (see Section 6.9, e.g., fresnel_option: Ruddick2006). The level L1d also includes the retrieval of the water leaving radiance and reflectance for each single upwelling radiance scan. It does not include any additional correction and the uncertainty budget is not updated. Most additional corrections are applied on a first estimate of water reflectance. The level L1c data thus serve as input for the level L1d where the water leaving radiance and water reflectance are recomputed with and without additional correction factors but with the use of Punpy for the estimations of uncertainties. The level L1c is not distributed by default to the end users.

3. Surface reflectance – process L1d:

   The surface_reflectance.processe_l1d module computes the correction factors (e.g., :math:`\epsilon`, the spectrally flat measurement error, for the NIR similarity correction, Ruddick et al., 2006), using the L1c :math:`\rho_wnosc` estimates (see Eq XXX). A quality control is also performed on the value retrieved for :math:`\epsilon`, i.e., :math:`\epsilon` should not exceed 5% of the reference water reflectance value, e.g.,  :math:`\rho_wnosc` at 620 nm).

4. Surface reflectance – process L2a:

   The module surface_reflectance.process performs final quality checks (still to be defined, potentially using auxillary data from, e.g., light sensors, rain sensor, camera, …). These final quality checks are foreseen in an updated version. Next, all variables are averaged per series (i.e., all scans previously interpolated to the upwelling radiance time step are averaged, see average function). Level 2a data have thus the dimensions “wavelength” and “series” and have the same dimensions with the land network L2a data.

Land Network
--------------

TBC - Pieter
