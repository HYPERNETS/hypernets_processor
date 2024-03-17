.. calibrate - algorithm theoretical basis
   Author: pdv
   Email: pieter.de.vis@npl.co.uk
   Created: 18/10/2021

.. _calibrate:


Calibrate - process to L1A
~~~~~~~~~~~~~~~~~~~~~~~~~~~
After the raw L0A data has been read in, it needs to be quality checked and calibrated in order to get
the radiance and irradiance L1A data products. The first step consists of assigning wavelengths to each
of the spectral pixels based on laboratory characterisation measurements (and omitting pixels outside the
calibration range). Next, the L0A dark scans are combined with the L0A (ir)radiance files, assigning each
dark to the right (ir)radiance series. Next, the quality checks described in :ref:`quality` are applied. In order
to get calibrated (ir)radiances, the calibration coefficients and non-linearity coefficients (as determined by
the `calibration laboratory at Tartu University <https://kosmos.ut.ee/en/laboratory>`_) are then applied to the raw data.

When multiple calibration files are available (i.e. at different calibration dates) the one nearest to the
acquisition time is used, though only looking backward. When reprocessing data, calibration dates after the
acquisition date are thus ignored. Interpolation between pre-deployment and post-deployment calibrations
will be explored in the future (see Section 6).

The exact measurement function to be used can be specified manually by providing the measurement function as a standalone python script.
If no custom measurement function is provided, a default measurement function is used (labelled StandardMeasurementFunction). 
This measurement function is defined by::

	def meas_function(digital_number,gains,dark_signal,non_linear,int_time):
        
        	DN=digital_number-dark_signal
        	DN[DN==0]=1
        	non_lin_func = np.poly1d(np.flip(non_linear))
            corrected_DN = DN / non_lin_func(DN)

        	return gains*corrected_DN/int_time*1000

where each of the arguments is a numpy array, digital_number gives the measured signal (in digital numbers), dark_signal gives the dark signal in digital numbers,
gains gives the calibration coefficients, non_linear has the polynomial non-linearity coefficients, and int_time
is the integration time of the measurement. 
An update to this default measurement function is foreseen, which will include temperature and straylight corrections.
The gains and non-linearity coefficients are taken from the most recent calibration data for the given instrument at the time of observation.

The same measurement function is applied for radiance and irradiance measurements, but the gains and non_linearity coefficients 
(as well as the measurements themselves) will be different. For the land network, the VNIR and SWIR sensors also both use the 
same measurement function, and each have their own set of calibration and non-linearity coefficients.

Uncertainties on each of the input quantities (i.e. digital_number, gains, dark_signal, non_linear and int_time) can optionally be propagated to the L1a products
using the punpy uncertainty propagation package. More detail are provided in :ref:`uncertainty`.


