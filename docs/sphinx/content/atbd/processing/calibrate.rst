.. calibrate - algorithm theoretical basis
   Author: seh2
   Email: sam.hunt@npl.co.uk
   Created: 6/11/20

.. _calibrate:


Calibrate - process to L1A
~~~~~~~~~~~~~~~~~~~~~~~~~~~

After the raw L0 data has been read in, it needs to be calibrated and quality checked in order to get the radiance and irradiance L1a data prodcuts.
The calibration itself applies the calibration coefficients and non-linearity coefficients (as determined in the lab by Tartu University) to the raw data. 
The exact measurement function to be used can be specified manually by providing the measurement function as a standalone python script.
If no custom measurement function is provided, a default measurement function is used (labelled StandardMeasurementFunction). 
This measurement function is defined by::

	def function(digital_number,gains,dark_signal,non_linear,int_time):
        
        DN=digital_number-dark_signal
        DN[DN==0]=1
        corrected_DN = DN /(non_linear[0]+non_linear[1]*DN+
                                       non_linear[2]*DN**2+
                                       non_linear[3]*DN**3+
                                       non_linear[4]*DN**4+
                                       non_linear[5]*DN**5+
                                       non_linear[6]*DN**6+
                                       non_linear[7]*DN**7)

        return gains*corrected_DN/int_time*1000

where digital_number gives the measured signal (in digital numbers), dark_signal gives the dark signal in digital numbers, 
gains gives the calibration coefficients, non_linear has the (8th order polynomial) non-linearity coefficients, and int_time 
is the integration time of the measurement. 
An update to this default measurement function is foreseen, which will include termperature and straylight coccerctions.
The gains and non-linearity coefficients are taken from the closest calibration data in time for the given instrument. 
In a future version of the processor and when post-deployment calibration files are available,  calibration data for a 
single measurement will be estimated from a linear interpolation in time of the calibration data.


The same measurement function is applied for radiance and irradiance measurements, but the gains and non_linearity coefficients 
(as well as the measurements themselves) will be different. For the land network, the VNIR and SWIR sensors also both use the 
same measurement function, and each have their own set of calibration and non-linearity coefficients.

Uncertainties on each of the input quantities (i.e. digital_number, gains, dark_signal, non_linear and int_time) are propagated to the L1a products
using the punpy uncertainty propagation package. More detail are provided in :ref:`uncertainty`.

Before calibrating each of the individual scans in the L0 data, a number of quality checks is applied. 
The first of these checks looks for outliers by comparing each scan ot the other 9 scans in the series. 
If the spectrally integrated signal of the scan is more than 3 sigma, or more that 25% (whichever is largest) removed from the mean, it is masked and not further used in the processing.
This process is repeated until convergance and applied to both the measured (ir)radiances as well as to the darks. 
In addition to this, a quality check is also performed to make sure the scan is not oversaturated (not too many pixels above an empirically defined threshold).
Scans not satisfying the quality checks are masked. A quality flag is added in the L1a data product to indicate which scan were masked. If all scans in a series are masked, there will additionally be an anomaly raised (see :ref:`anomalies`).
