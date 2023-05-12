.. calibrate - algorithm theoretical basis
   Author: pdv
   Email: pieter.de.vis@npl.co.uk
   Created: 18/10/2021

.. _calibrate:


Calibrate - process to L1A
~~~~~~~~~~~~~~~~~~~~~~~~~~~

After the raw L0 data has been read in, it needs to be calibrated and quality checked in order to get the radiance and irradiance L1a data products.
The calibration itself applies the calibration coefficients and non-linearity coefficients (as determined in the lab by Tartu University) to the raw data. 
The exact measurement function to be used can be specified manually by providing the measurement function as a standalone python script.
If no custom measurement function is provided, a default measurement function is used (labelled StandardMeasurementFunction). 
This measurement function is defined by::

	def meas_function(digital_number,gains,dark_signal,non_linear,int_time):
        
        	DN=digital_number-dark_signal
        	DN[DN==0]=1
        	non_lin_func = np.poly1d(np.flip(non_linear))
            corrected_DN = DN / non_lin_func(DN)

        	return gains*corrected_DN/int_time*1000

where digital_number gives the measured signal (in digital numbers), dark_signal gives the dark signal in digital numbers, 
gains gives the calibration coefficients, non_linear has the polynomial non-linearity coefficients, and int_time
is the integration time of the measurement. 
An update to this default measurement function is foreseen, which will include temperature and straylight corrections.
The gains and non-linearity coefficients are taken from the most recent calibration data for the given instrument at the time of observation.

The same measurement function is applied for radiance and irradiance measurements, but the gains and non_linearity coefficients 
(as well as the measurements themselves) will be different. For the land network, the VNIR and SWIR sensors also both use the 
same measurement function, and each have their own set of calibration and non-linearity coefficients.

Before calibrating each of the individual scans in the L0 data, a number of quality checks is applied, which are described in :ref:`quality`. 
Uncertainties on each of the input quantities (i.e. digital_number, gains, dark_signal, non_linear and int_time) can optionally be propagated to the L1a products
using the punpy uncertainty propagation package. More detail are provided in :ref:`uncertainty`.


