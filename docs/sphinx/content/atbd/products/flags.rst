.. flags - algorithm theoretical basis
   Author: seh2
   Email: sam.hunt@npl.co.uk
   Created: 6/11/20

.. _flags:

The quality flag field consists of 32 bits. Every bit is related to the absence or presence of a a flag as described in Table 6. The quality flag value given in each data level is the compound value of the specific bits of each raised flag. Some flags in Table 6 are left as placeholders for future updates. Note, additional flags can be added, Table 6 presents the flags used in the current version. 

Flags description 
~~~~~~~~~~~~~~~~~~~~~~~~~~~
+------+---------------+
| Item | Character     |
+======+===============+
| 1    | Puss in Boots |
+------+---------------+
| 2    | Cinderella    |
|      |               |
+------+---------------+


+-------+------------+-------------------------------------+-----------------------------+
| Bit # | Symbol     | Description                         | Comment                     |
+=======+============+=====================================+=============================+
| 1     | Saturation | Pixel saturation                    |                             |
+-------+------------+-------------------------------------+-----------------------------+
| 2     | non-linear | Non-linearity                       |                             |
+-------+------------+-------------------------------------+-----------------------------+
| 3     | bad_pointing | Bad pointing (pointing > pan-tilt uncertainty)                    |                             |
+-------+------------+-------------------------------------+-----------------------------+
| 4     | placeholder1 | Non-linearity                       |                             |
+-------+------------+-------------------------------------+-----------------------------+
| 5     | lon_default | Pixel saturation                    |                             |
+-------+------------+-------------------------------------+-----------------------------+
| 6     | lat_default | Non-linearity                       |                             |
+-------+------------+-------------------------------------+-----------------------------+
| 7     | outliers | Pixel saturation                    |                             |
+-------+------------+-------------------------------------+-----------------------------+
| 8     | non-linear | Non-linearity                       |                             |
+-------+------------+-------------------------------------+-----------------------------+
| 9     | L0_thresholds | Pixel saturation                    |                             |
+-------+------------+-------------------------------------+-----------------------------+
| 10    | L0_discontinuity | Non-linearity                       |                             |
+-------+------------+-------------------------------------+-----------------------------+
| 11    | dark_outliers | Non-linearity                       |                             |
+-------+------------+-------------------------------------+-----------------------------+
| 12    | angles_missing | Non-linearity                       |                             |
+-------+------------+-------------------------------------+-----------------------------+
| 13    | lu_eq_missing | Non-linearity                       |                             |
+-------+-----------------------+-------------------------------------+-----------------------------+
| 14    | fresnel_angle_missing | Non-linearity                       |                             |
+-------+-----------------------+-------------------------------------+-----------------------------+
| 15    | fresnel_default | Non-linearity                       |                             |
+-------+------------+-------------------------------------+-----------------------------+
| 16    | temp_variability_ed | Non-linearity                       |                             |
+-------+------------+-------------------------------------+-----------------------------+
| 17    | temp_variability_lu | Non-linearity                       |                             |
+-------+------------+-------------------------------------+-----------------------------+
| 18    | min_nbred | Non-linearity                       |                             |
+-------+------------+-------------------------------------+-----------------------------+
| 19    | min_nbrlu | Non-linearity                       |                             |
+-------+------------+-------------------------------------+-----------------------------+
| 20    | min_nbrlsky | Non-linearity                       |                             |
+-------+------------+-------------------------------------+-----------------------------+
| 21    | def_wind_flag | Non-linearity                       |                             |
+-------+------------+-------------------------------------+-----------------------------+
| 22    | simil_fail | Non-linearity                       |                             |
+-------+------------+-------------------------------------+-----------------------------+


2
non-linearity
Non-linearity
NYI

3
bad_pointing
Bad pointing 
Pan/tilt angle versus requested angle -NYI

4
placeholder1

Placeholder for other potential calibration related quality flags

5
lon_default
Missing longitude
When raised use default
Quality control #1
6
lat_default
Missing latitude
When raised use default
Quality control #1
7
outliers
Outliers and NaN 
Mask the scans that lie more than 3 standard-deviations away from the mean
Quality control #2
8
angles_missing
Missing angles

Quality control #3
9
lu_eq_missing
missing azimuthal equivalent for upwelling radiance 
 
Quality control #3
10
fresnel_angle_missing
no appropriate fresnel angle for downwelling radiance


Quality control #3
11
fresnel_default
Default/Fixed fresnel reflectance/fresnel angles out of range for Mobleys look up table
fresnel_default
in get_fresnelrefl
Quality control #4
12
temp_variability_ed
Temporal variability in ED
diff_threshold from processing config
Quality control #3
13
temp_variability_lu
Temporal variability in Lsky
diff_threshold from processing config
Quality control #3
14
min_nbred
Min number of Ed
Nbred from processing config
Quality control #3
15
min_nbrlu
Min number of Lt
Nrblu from processing config
Quality control #3
16
min_nbrlsky
Min number of Lsky
Nbrlsky from processing config
Quality control #3
17
def_wind_flag
Default wind value for fresnel retrieval
In get_wind
Quality control #4
18
simil_fail
Similarity test failure
Reference wavelength  from processing config and LUT from Ruddick et al. (2006).
Quality control #5





