.. average - algorithm theoretical basis
   Author: Pieter De Vis
   Email: Pieter.De.Vis@npl.co.uk
   Created: 01/10/2021

.. _average:


Averaging - Process to L1B
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Water Network
--------------

The L1B data processing takes calibrated radiance and irradiance scans as input and computes the mean per series. For a standard water protocol the series are the following:

   1. L1A irradiance scans taken at the start of the sequence (standard protocol requires minimum 3 scans, typically 10 are used),
   2. L1A downwelling radiance following (1) (standard protocol requires minimum 3 scans, typically 10 are used),
   3. L1A upwelling radiance scans (standard protocol requires minimum 6 scans, typically 10 are used), and finally,
   4. L1A irradiance scans taken at the end of the sequence (standard protocol requires minimum 3 scans, typically 10 are used).

The L1B output is an average per series excluding scans which did not pass the :ref:`quality`.

Land Network
--------------

Simlarly for the land network, the L1B data processing starts by taking calibrated radiance and irradiance scans as input and computing the mean per series. For a standard land protocol the series are the following:

   1. VNIR L1A irradiance scans taken at the start of the sequence (standard protocol requires minimum 3 scans, typically >10 are used),
   2. SWIR L1A irradiance scans taken at the start of the sequence (standard protocol requires minimum 3 scans, typically 10 are used),
   3. VNIR L1A upwelling radiance scans for several angles (standard protocol requires minimum 6 scans, typically >10 are used), and finally,
   4. SWIR L1A upwelling radiance scans for several angles (standard protocol requires minimum 6 scans, typically 10 are used), and finally,
   5. VNIR L1A irradiance scans taken at the end of the sequence (standard protocol requires minimum 3 scans, typically >10 are used).
   6. SWIR L1A irradiance scans taken at the end of the sequence (standard protocol requires minimum 3 scans, typically 10 are used).

The number of scans in the VNIR is typically larger than the number of scans in the SWIR since SWIR scans have loner integration times, and thus more VNIR scans can be taken within the same amount of time.
The average per series is calculated excluding scans which did not pass the :ref:`quality`.

The next stage of the L1B processing consists of combining the VNIR and SWIR data. 
For the current version of the processor, this is done by simply appending all VNIR measurements with wavelengths smaller than 1000 with all SWIR measurements with wavelengths larger than 1000nm.
In future versions of the processor this will be done using a sliding average where, for the overlapping wavelengths, a weighted mean is taken between VNIR and SWIR so that there is a smooth transition.
For now this sliding average is not applied so that the effects of a missing temperature correction are clearly visible.

The L1B output is thus an average per series for VNIR and SWIR combined.

