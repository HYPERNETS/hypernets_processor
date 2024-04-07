.. average - algorithm theoretical basis
   Author: Pieter De Vis
   Email: Pieter.De.Vis@npl.co.uk
   Created: 01/10/2021

.. _average:


Averaging - Process to L1B
~~~~~~~~~~~~~~~~~~~~~~~~~~~
In order to get the best averaged results per series, the most robust approach is to first average the L0 data
(i.e. radiance, irradiance and dark scans in digital numbers) and then calibrate the averaged results using the same approach as in :ref:`calibrate`.
The L0 scans are quality checked and only the scans that passed the quality checks are used in the mean (see :ref:`quality`).
The random uncertainties on the L0 data are then taken to be the standard deviation between the scans that passed the quality checks.
Once averaged, the mean radiances, irradiances and blacks are then used in the same calibration equation as was used for the L1A calibration.
The random uncertainties from the L0 data are propagated to the L1B product together with the systematic uncertainties from the calibration files.

Water Network
--------------

For a standard water protocol the series for which the L0 data are averaged and then calibrated are the following:

   1. irradiance scans taken at the start of the sequence (standard protocol requires minimum 3 scans),
   2. downwelling radiance following (1) (standard protocol requires minimum 3 scans),
   3. upwelling radiance scans (standard protocol requires minimum 6 scans), and finally,
   4. irradiance scans taken at the end of the sequence (standard protocol requires minimum 3 scans).

Land Network
--------------

Simlarly for the land network, the L1B data processing starts by averaging the L0 data and then calibrating them. For a standard land protocol the series are the following:

   1. VNIR irradiance scans taken at the start of the sequence (standard protocol requires minimum 3 scans, typically >10 are used),
   2. SWIR irradiance scans taken at the start of the sequence (standard protocol requires minimum 3 scans, typically 10 are used),
   3. VNIR upwelling radiance scans for several angles (standard protocol requires minimum 6 scans, typically >10 are used),
   4. SWIR upwelling radiance scans for several angles (standard protocol requires minimum 6 scans, typically 10 are used),
   5. VNIR irradiance scans taken at the end of the sequence (standard protocol requires minimum 3 scans, typically >10 are used).
   6. SWIR irradiance scans taken at the end of the sequence (standard protocol requires minimum 3 scans, typically 10 are used).

The number of scans in the VNIR is typically larger than the number of scans in the SWIR since SWIR scans have longer integration times, and thus more VNIR scans can be taken within the same amount of time.
The average per series is calculated excluding scans which did not pass the :ref:`quality`.

The next stage of the L1B processing consists of combining the VNIR and SWIR data. 
For the current version of the processor, this is done by simply appending all VNIR measurements with wavelengths smaller than 1000nm with all SWIR measurements with wavelengths larger than 1000nm.
In future versions of the processor an option will likely be added to do this using a sliding average where, for the overlapping wavelengths, a weighted mean is taken between VNIR and SWIR so that there is a smooth transition.
For now this sliding average is not applied so that the effects of a missing temperature correction are clearly visible.

The L1B output is thus an average per series for VNIR and SWIR combined.

