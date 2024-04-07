.. surface_reflectance - algorithm theoretical basis
   Author: Pieter De Vis
   Email: Pieter.De.Vis@npl.co.uk
   Created: 01/10/2021

.. _surface_reflectance:


Surface Reflectance - Process to L2A
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Water Network
--------------
For each L1C data file (one per relative azimuth angle), the
surface reflectances and water radiances (computed at each :math:`L_u`
timestamp) are averaged, respectively. This results in L2A files
containing one spectrum for each variable (i.e., water-leaving
radiance, and, water reflectance with and without the NIR
similarity correction) and the associated uncertainties.

Land Network
--------------
For the land network, the surface reflectances can now be calculated from the L1C radiances (:math:`L_u`) and irradiances (:math:`E_d`) as:

.. math:: \rho =\pi\frac{L_u}{E_d}

We note that this surface reflectance is technically the hemispherical-conical
reflectance factor and not the bidirectional reflectance factor, as
the contribution from sky reflectance is included in the measurements
and the field-of-view of the LANDHYPERNET instruments is 5°.

