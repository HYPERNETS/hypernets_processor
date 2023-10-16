.. surface_reflectance - algorithm theoretical basis
   Author: Pieter De Vis
   Email: Pieter.De.Vis@npl.co.uk
   Created: 01/10/2021

.. _surface_reflectance:


Surface Reflectance - Process to L2A
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Water Network
--------------
From the above water upwelling radiance :math:`L_u` and the above water downwelling radiance :math:`L_d`, the water leaving radiance :math:`L_w` can be approximated as:

.. math:: L_w(\theta,\Delta\phi,\lambda,\theta_0)=L_u(\theta,\Delta\phi,\lambda,\theta_0)-\rho(\theta,\Delta\phi,\lambda,\theta_0,e)L_d(\theta,\Delta\phi,\lambda,\theta_0)
with
   * :math:`\theta` being the viewing zenith angle (0° is pointing vertically down, measuring upwelling light and 180° is pointing vertically upward, measuring downwelling light),
   * :math:`\theta_0` is the sun zenith angle (equals 0°  when the sun is at zenith and 90° when the sun is at sunset), and,
   * :math:`\Delta\phi` is the relative azimuth angle between sun and sensor measured with respect to sun and clockwise from sun to target (0° means that the radiance sensors are pointing into the sun glint direction, while 180° corresponds to a viewing azimuth with the sun behind).

The term :math:`\rho` is the air-water interface reflectance coefficient expressed as a function of viewing geometry and sun zenith angle and environmental factors (:math:`e`). When the water surface is perfectly flat, :math:`\rho` is the Fresnel reflectance and the environmental factor only depends on the relative refractive index of the air-water interface. When the water is not perfectly flat, :math:`\rho` needs to account, in addition to the fresnel reflectance, for the geometric effects of the wave facets created by the roughened water surface (often called the “effective Fresnel reflectance coefficient”, Ruddick et al., 2019). Therefore, :math:`\rho` is commonly approximated as a function of the viewing and illumination geometry and wind speed, ws, and can be written as :math:`\rho(\theta,\theta_0,\Delta\phi,ws)` (Mobley, 1999 and 2015). The appropriate :math:`\rho` is calculated in the L1C processing, see :ref:`interpolate`.

The water leaving radiance is then converted into water reflectance as follows:

.. math:: \rho_w_nosc =\pi\frac{L_w}{E_d}

with :math:`E_d` being the downwelling irradiance. And `nosc` stands for non similarity corrected reflectance. Indeed, although most acquisition protocols attempt to avoid sun glint, over wind roughened surfaces, sun glint may still be present when measuring the target radiance. Therefore a spectrally flat measurement error, :math:`\epsilon`, based on the “near infrared (NIR) similarity spectrum” correction, is applied. :math:`\epsilon` is estimated using two wavelengths in the NIR (Ruddick et al., 2006), where :math:`\lambda_1` = 780 nm and :math:`\lambda_2` = 870 nm. The :math:`\epsilon` correction factor is calculated in the L1C processing, see :ref:`interpolate`.

The final L2a product is the averaged water reflectance corrected for the NIR similarity spectrum:

.. math:: \rho_w(\lambda)=\rho_wnosc(\lambda)-\epsilon

Note, the final L2A average product is only computed for sequences that does not show any of the following flags : "outliers", "angles_missing","lu_eq_missing","fresnel_angle_missing", "min_nbred","min_nbrlu","min_nbrlsky", "simil_fail"

Land Network
--------------
For the land network, the surface reflectances can now be trivially calculated from the L1C radiances (:math:`L_u`) and irradiances (:math:`E_d`) as:

.. math:: \rho =\pi\frac{L_u}{E_d}

The L1C products alreay contained (ir)radiance averaged per series, so no further steps are necessary.


