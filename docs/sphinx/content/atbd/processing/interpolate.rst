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

Note the funtion *rhymer_hypstar.process_l1c* takes as input the L1A files and not the L1B. Indeed it checks for additional (water-application specific) quality flags. The L1C processor will then average the series (often at the start and end of the sequence) of downwelling radiance and irradiance scans and interpolate these averages to the upwelling radiance scans (standard configuration file requires 6 scans for upwelling radiance). Hence, the final dimensions for the upwelling radiance, downwelling irradiance and radiance and reflectance outputs for the L1C data level is wavelength and upwelling radiance scans (default 6).

1. **Quality check of the scans** (flags: temp_variability_ed, temp_variability_lu):

   The first function in the *rhymer_hypstar.process_l1c* module checks for the variability within a series, i.e., it assigns flags to each scan showing a temporal jump, with the previous and following scan, of more than a given threshold (25% is the default) at 550 nm. 


2. **Parse cycle** (flags: angles_missing, lu_eq_missing, fresnel_angle_missing, fresnel_default, min_nbred, min_nbrlu, min_nbrlsky,):

   The second function parses the cycle, i.e., it separates downwelling and upwelling radiance, investigate if all required angles are present and if there are coincident upwelling and downwelling radiance measurements for the retrieval of the water leaving radiance. 


3. **Wavelength interpolation**:

   Next, since the irradiance and radiance measurements have a slight shift in wavelength, first a spectral interpolation is performed to fit the irradiance measurements to the radiance wavelengths. 


4. **Averaging downwelling irradiance and radiance series to upwelling radiance scans**:

   Downwelling radiance and irradiance (as well as uncertainties) are averaged per series.


5. **Temporal interpolation**:

   The (per series) averaged downwelling irradiance and radiance data are interpolated to the timestamp of the upwelling radiance scans. Uncertainties are           computed for the interpolation of the downwelling radiance and irradiance measurements, respectively. Timestamp interpolation is done, by default, with a linear     interpolation (see  https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html)


6. **Ancillary data retrieval**:

   All the required parameters for the computation of the water leaving radiance and reflectance, i.e., wind speed, ws, and the effective fresnel reflectance        coefficient (:math:`\rho(\theta,\theta_0,\Delta\phi,ws)` are retrived. Wind speed may be taken from, e.g., a default value (e.g., 2m/s), in situ measurements,    ancilliary datasets such as NCEP Met data. Similarly, the Fresnel reflectance coefficient can be extracted from : (1) different look-up tables (Mobley 1999       (default); 2015), or, set to a default value, estimated as a function of wind speed (e.g., Ruddick et al. 2006). 
   The  configuration files (job and processing) determine which option is used for the processing (see Section 6.9, e.g., fresnel_option: Ruddick2006). 


7. **Intermediate L1C surface reflectance**:

   L1C processing also includes the retrieval of the water leaving radiance and reflectance for each single upwelling radiance scan. From the above water upwelling radiance :math:`L_u` and the above water downwelling radiance :math:`L_d`, the water leaving radiance :math:`L_w` is approximated as:

   .. math:: L_w(\theta,\Delta\phi,\lambda,\theta_0)=L_u(\theta,\Delta\phi,\lambda,\theta_0)-\rho(\theta,\Delta\phi,\lambda,\theta_0,e)L_d(\theta,\Delta\phi,\lambda,\theta_0)
   with
      * :math:`\theta` being the viewing zenith angle (0° is pointing vertically down, measuring upwelling light and 180° is pointing vertically upward, measuring downwelling light),
      * :math:`\theta_0` is the sun zenith angle (equals 0°  when the sun is at zenith and 90° when the sun is at sunset), and,
      * :math:`\Delta\phi` is the relative azimuth angle between sun and sensor measured with respect to sun and clockwise from sun to target (0° means that the radiance sensors are pointing into the sun glint direction, while 180° corresponds to a viewing azimuth with the sun behind).

   The term :math:`\rho` is the air-water interface reflectance coefficient expressed as a function of viewing geometry and sun zenith angle and environmental        factors (:math:`e`). When the water surface is perfectly flat, :math:`\rho` is the Fresnel reflectance and the environmental factor only depends on the            relative refractive index of the air-water interface. When the water is not perfectly flat, :math:`\rho` needs to account, in addition to the fresnel              reflectance, for the geometric effects of the wave facets created by the roughened water surface (often called the “effective Fresnel reflectance coefficient”,    `Ruddick et al. (2019) <https://odnature.naturalsciences.be/downloads/publications/ruddick_remsens_lwprotocols-published.pdf>`_). Therefore, :math:`\rho` is commonly approximated as a function of the viewing and illumination geometry and wind speed, ws, and can be      written as :math:`\rho(\theta,\theta_0,\Delta\phi,ws)` (`Mobley, 1999 <https://www.researchgate.net/profile/Curtis-Mobley-2/publication/5528648_Estimation_of_the_Remote-Sensing_Reflectance_from_Above-Surface_Measurements/links/53dbaed20cf216e4210bfe33/Estimation-of-the-Remote-Sensing-Reflectance-from-Above-Surface-Measurements.pdf?_sg%5B0%5D=2eTIpadyRgORqc3f_kMWeO_Ca5GifXv_LVk2-ZxEWx9YXbEh_-kt4Av1OpeEGh95xyyikCbTcDFGWbkjr6iAXw.-x4KezAP80LKp_7LVLS1l0PQimSZSvx-IGX7mJLAtLYN8xpiIg5E-LqKHMJaY5ovcDgvEH4X30or5B6wxs4NVw&_sg%5B1%5D=ngxmRt2SyaOb-sCb8fw6qHZnI9orXTspaqcKi5gz6_A4xSMaEf85SUcUzJlVTVNO7hhSjzwqgB-RCurMuXc3ElvHT35G651j3QrrV67Up4D4.-x4KezAP80LKp_7LVLS1l0PQimSZSvx-IGX7mJLAtLYN8xpiIg5E-LqKHMJaY5ovcDgvEH4X30or5B6wxs4NVw&_iepl=>`_ and `2015 <https://www.researchgate.net/profile/Curtis-Mobley-2/publication/277906925_Polarized_reflectance_and_transmittance_properties_of_windblown_sea_surfaces/links/56ec6f5508ae59dd41c4fddf/Polarized-reflectance-and-transmittance-properties-of-windblown-sea-surfaces.pdf?_sg%5B0%5D=Og1CYnelLZa892f43Qf6jrHOIk8Hr6Y386284hb7shQLT05doZwjg8jq0s-En_BU0gKY7-J-mJNh0gHMnaNiCw.eIAGWzI_tw8PHq9VZOTh0-oFxkvpx9QqpuXULFa3KWQB8deTMFKC1jtRx1h5-qpRAYINodST1LVorY6cELxs1Q&_sg%5B1%5D=9Pi4CqPOdtqhrAiLPplr5TV_k9H5HIHBKPa3LQPmyxROruELTC8bJKD9S6tC0EKrQSR8hThsvna3g4AqABc0BqZ5UIvPDk4wzRklSj9I6rLe.eIAGWzI_tw8PHq9VZOTh0-oFxkvpx9QqpuXULFa3KWQB8deTMFKC1jtRx1h5-qpRAYINodST1LVorY6cELxs1Q&_iepl=>`_).

   The water leaving radiance is then converted into water reflectance as follows:

   .. math:: \rho_wnosc =\pi L_w /E_d

   with :math:`E_d` being the downwelling irradiance. And `nosc` stands for non similarity corrected reflectance. 

8. **Intermediate L1C similarity corrected reflectance** (flag: simil_fail):

   Although most acquisition protocols attempt to avoid sun glint, over wind roughened surfaces, sun glint may still be present when measuring the target            radiance. Therefore a spectrally flat measurement error, :math:`\epsilon`, based on the “near infrared (NIR) similarity spectrum” correction, is applied.          :math:`\epsilon` is estimated using two wavelengths in the NIR `(Ruddick et al. (2016) <https://odnature.naturalsciences.be/downloads/publications/ruddick_et_al-2006-limnology_and_oceanography21.pdf>`_, where :math:`\lambda_1` = 780 nm and :math:`\lambda_2` = 870 nm.

   .. math:: \epsilon = [ \alpha\rho_wnosc(\lambda_2)-\rho_wnosc(\lambda_1)]/[(\alpha-1)]

   and :math:`\alpha` is the similarity spectrum `(Ruddick et al. (2016) <https://odnature.naturalsciences.be/downloads/publications/ruddick_et_al-2006-limnology_and_oceanography21.pdf>`_ ratio for the bands used; the default is, :math:`\alpha(780, 870)` equals 1/0.523 = 1.912.

   
   To avoid negative reflectance data, if :math:`\epsilon` exceeds a given percentage of the reflectance at a reference wavelength the *simil_fail* flag is raised (see :doc:`flags description <../products/flags.rst>`. The default percentage is 5% and reference wavelength is 670 nm.
   Next the *similarity corrected* reflectance product is computed as follows:
   
   .. math:: \rho_w(\lambda) =\rho_wnosc(\lambda)-\epsilon
      
  

Land Network
--------------

The L1C processing for the land network consists of two interpolation steps that are applied to the irradiance measurements in order to bring them to the same wavelength scale and timestamps as the radiance measurements. 

1. **Spectral interpolation**: 
The irradiances are spectrally interpolated to the wavelengths of the radiance measurements (which are not identical to the irradiance measurements).
Currently, we use a simple linear interpion, but this will substitud by the following:
To perform the interpolation, we want to account for the spectral variability that is expected for typical solar irradiance measurements. In order to do this, we take a reference simulated solar spectrum, convolved with the HYPERNETS spectral response function, but sampled at 0.1 nm intervals. This high resolution spectrum is used to inform us on the spectral variability between the given data points.
We then use the interpolation tool within the NPL CoMet toolkit to interpolate between the irradiance wavelengths using this high-resolution reference. The resulting interpolation function goes through the irradiance data at the given irradiance wavelengths, but follows the high-resolution spectrum between these wavelengths.
The irradiances at the new set of wavelengths are then calculated using this interpolation function.

2. **Temporal interpolation**: 
Next, we use a similar method to perform a temporal interpolation. In this case, we interpolate the irradiance measurements at the start and end of the sequence, to each of the timestamps of the radiance measurements. Here the high-resolution model is the known daily cycle of irradiance, approximately proportional to the cosine of the solar zenith angle.
The NPL CoMet interpolation tool is again used for the interpolation. 

The output of the L1C processing is a product with irradiances that now have the same wavelengths and timestamps as the radiance measurements.



