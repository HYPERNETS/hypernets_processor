.. interpolate - algorithm theoretical basis
   Author: Pieter De Vis
   Email: Pieter.De.Vis@npl.co.uk
   Created: 01/10/2021

.. _interpolate:


Interpolating - Process to L1C
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Water Network
--------------

To process the water network data, the hypernets processor includes RHYMER ("Reliable processing of HYperspectral MEasurement of Radiance", version 20190718 on 16/10/2020, written by Quinten Vanhellemont and adapted for the HYPSTAR by Clémence Goyens). RHYMER provides all the required functions to process the above water measurements (currently including Mobley 1999 and 2015 and Ruddick et al., 2006 for the Fresnel correction). RHYMER is written as such that it can easily welcome any additional look-up-tables, processing functions, quality flags, ...

Note the funtion *rhymer_hypstar.process_l1c* takes as input the L1A files and not the L1B. Indeed it checks for additional (water-application specific) quality flags. Scans are then averaged per series according to these flags.

1. Quality check of the scans (flags: temp_variability_ed, temp_variability_lu):

   The first function in the *rhymer_hypstar.process_l1c* module checks for the variability within a series, i.e., it assigns flags to each scan showing a temporal jump, with the previous and following scan, of more than a given threshold (25% is the default) at 550 nm. 

2. Parse cycle (flags: angles_missing, lu_eq_missing, fresnel_angle_missing, fresnel_default, min_nbred, min_nbrlu, min_nbrlsky,):

   The second function parses the cycle, i.e., it separates downwelling and upwelling radiance, investigate if all required angles are present and if there are coincident upwelling and downwelling radiance measurements for the retrieval of the water leaving radiance. 

3. Wavelength interpolation:

   Next, since the irradiance and radiance measurements have a slight shift in wavelength, first a spectral interpolation is performed to fit the irradiance measurements to the radiance wavelengths. 

4. Averaging downwelling irradiance and radiance series to upwelling radiance scans:

   Downwelling radiance and irradiance (as well as uncertainties) are averaged per series.

5. Temporal interpolation

   The (per series) averaged downwelling irradiance and radiance data are interpolated to the timestamp of the upwelling radiance scans. Uncertainties are computed for the interpolation of the downwelling radiance and irradiance measurements, respectively. Timestamp interpolation is done, by default, with a linear interpolation (see  https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html)

6. Ancillary data retrieval:

   All the required parameters for the computation of the water leaving radiance and reflectance, i.e., wind speed, ws, and the effective fresnel reflectance coefficient (:math:`\rho(\theta,\theta_0,\Delta\phi,ws)` are retrived. Wind speed may be taken from, e.g., a default value (e.g., 2m/s), in situ measurements, ancilliary datasets such as NCEP Met data. Similarly, the Fresnel reflectance coefficient can be extracted from : (1) different look-up tables (Mobley 1999 (default); 2015), or, set to a default value, estimated as a function of wind speed (e.g., Ruddick et al. 2006). 
   The  configuration files (job and processing) determine which option is used for the processing (see Section 6.9, e.g., fresnel_option: Ruddick2006). 


7. Intermediate L1C surface reflectance:

   L1C processing also includes the retrieval of the water leaving radiance and reflectance for each single upwelling radiance scan. From the above water upwelling radiance :math:`L_u` and the above water downwelling radiance :math:`L_d`, the water leaving radiance :math:`L_w` is approximated as:

   .. math:: L_w(\theta,\Delta\phi,\lambda,\theta_0)=L_u(\theta,\Delta\phi,\lambda,\theta_0)-\rho(\theta,\Delta\phi,\lambda,\theta_0,e)L_d(\theta,\Delta\phi,\lambda,\theta_0)
   with
      * :math:`\theta` being the viewing zenith angle (0° is pointing vertically down, measuring upwelling light and 180° is pointing vertically upward, measuring downwelling light),
      * :math:`\theta_0` is the sun zenith angle (equals 0°  when the sun is at zenith and 90° when the sun is at sunset), and,
      * :math:`\Delta\phi` is the relative azimuth angle between sun and sensor measured with respect to sun and clockwise from sun to target (0° means that the radiance sensors are pointing into the sun glint direction, while 180° corresponds to a viewing azimuth with the sun behind).

   The term :math:`\rho` is the air-water interface reflectance coefficient expressed as a function of viewing geometry and sun zenith angle and environmental factors (:math:`e`). When the water surface is perfectly flat, :math:`\rho` is the Fresnel reflectance and the environmental factor only depends on the relative refractive index of the air-water interface. When the water is not perfectly flat, :math:`\rho` needs to account, in addition to the fresnel reflectance, for the geometric effects of the wave facets created by the roughened water surface (often called the “effective Fresnel reflectance coefficient”, Ruddick et al., 2019). Therefore, :math:`\rho` is commonly approximated as a function of the viewing and illumination geometry and wind speed, ws, and can be written as :math:`\rho(\theta,\theta_0,\Delta\phi,ws)` (Mobley, 1999 and 2015).

   The water leaving radiance is then converted into water reflectance as follows:

   .. :math:: \rho_w_nosc =\pi\frac{L_w}{E_d}

   with :math:`E_d` being the downwelling irradiance. And `nosc` stands for non similarity corrected reflectance. 

7. Intermediate L1C similarity corrected reflectance (flag: simil_fail):

   Although most acquisition protocols attempt to avoid sun glint, over wind roughened surfaces, sun glint may still be present when measuring the target radiance. Therefore a spectrally flat measurement error, :math:`\epsilon`, based on the “near infrared (NIR) similarity spectrum” correction, is applied. :math:`\epsilon` is estimated using two wavelengths in the NIR (Ruddick et al., 2006), where :math:`\lambda_1` = 780 nm and :math:`\lambda_2` = 870 nm.

   .. :math: \epsilon =\frac{\alpha\rho_w_nosc(\lambda_2)-\rho_w_nosc(\lambda_1)}{(\lambda_2-\lambda_1)}
   
   If :math:`epsilon` exceeds x * :math:`\rho_nosc(\lambda_ref)` with x a given percentage (default: 5%) and :math:`\lambda_ref` a reference wavelength (default: 670 nm) the *simil_fail* flag is raised.
   Next the *similarity corrected* reflectance product is computed as follows:
   
   .. :math:: \rho_w(\lambda) =\rho_w^nosc(\lambda)-\epsilon

Land Network
--------------

TBC - Pieter
