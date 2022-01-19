.. average - algorithm theoretical basis
   Author: Pieter De Vis
   Email: Pieter.De.Vis@npl.co.uk
   Created: 01/10/2021

.. _average:


Averaging - Process to L1B
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Water Network
--------------

The L1B data processing takes calibrated radiance and irradiance scans as input and computes the mean and standard deviation per series. For a standard water protocol the series are the following:

   1. L1A irradiance scans taken at the start of the sequence (standard protocol requires minimum 3 scans),
   2. L1A downwelling radiance following (1) (standard protocol requires minimum 3 scans),
   3. L1A upwelling radiance scans (standard protocol requires minimum 6 scans),
   4. L1A irradiance scans taken at the start of the sequence (standard protocol requires minimum 3 scans), and finally,
   5. L1A irradiance scans taken at the end of the sequence (standard protocol requires minimum 3 scans).

The L1B output is an average and standard deviation per series excluding scans with at least one of the following flags: "outliers".

Land Network
--------------

TBC - Pieter
