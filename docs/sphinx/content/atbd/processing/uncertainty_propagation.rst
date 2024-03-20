.. uncertainty - algorithm theoretical basis
   Author: seh2
   Email: sam.hunt@npl.co.uk
   Created: 6/11/20

.. _uncertainty:


Uncertainty Propagation 
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Uncertainties are propagated from product to product using Monte Carlo (MC) approach (see `Supplement 1 to the “Guide
to the expression of uncertainty in measurement”<https://www.bipm.org/documents/20126/2071204/JCGM_101_2008_E.pdf>`_)
This MC approach is implemented using the punpy module (see also `the punpy ATBD <https://punpy.readthedocs.io/en/latest/content/atbd.html>`_)
from the open-source `CoMet toolkit<https://www.comet-toolkit.org/>`_. A metrological approach is followed, where for each processing stage, a measurement function is defined,
as well as the input quantities and the measurand.

Here we summarise the main steps and detail how these were implemented for HYPERNETS.
The main stages consist of:

-  Formulation: Defining the measurand (output quantity Y), the input quantities :math:`X = (X_{i},\ldots,\ X_{N})`, and the measurement function (as a model relating Y and X).
   One also needs to asign Probability Density Functions (PDF) of each of the input quantities, as well as define the correlation between them (through joint PDF).
   In our method, the joint PDF's are are made by first generating uncorrelated PDF, which are then correlated using the Cholesky decomposition method.

-  Propagation: propagate the PDFs for the :math:`X_i` through the model to obtain the PDF for Y. 

-  Summarizing: Use the PDF for Y to obtain the expectation of Y, the standard uncertainty u(Y) associated with Y (from the standard deviation), and the covariance between the different values in Y.


For the HYPERNETS processing, the first propagation of uncertainties is applied when calibrating the L1A scans. The measurement function for this step is given in :ref:`calibrate`. 
The input quantities are the measured signal (in digital numbers), the dark signal, the calibration coefficients, the non-linearity coefficients, and the integration time of the measurement.
All that remains to be done in order to complete the `Formulation' stage of MC, we need to define the uncertainties and error-correlations for each of the input quantities as well as their PDF.

For the measured signal and dark signal, the random uncertainties can be determined from calculating the standard deviation between the different scans.
In addition, systematic uncertainties in the measured signal will cancel with systematic uncertainties in the dark signal. 
We can thus treat these two input quantities as having entirely random uncertainties.
The calibration coefficients and non-linearity coefficients were characterised in the lab by Tartu University. 
Uncertainties were quantified for 16 different uncertainty contributions, and preliminary error correlation structures were defined.
The uncertainties on the integration times were assumed to be neglibible.
All PDF are assumed to be Gaussian with the input quantities as the mean and their uncertainties as the width.

Once all the uncertainties and their correlation have been quantified, punpy can be used to perform the Propagation and summarizing stage of MC. 
Punpy returns the measurand (calibrated (ir)radiances for L1A) as well as the uncertainties and correlation matrix w.r.t. wavelength.
All the HYPERNETS products are stored as digital effects tables (see `<https://www.comet-toolkit.org/tools/obsarray/>`_), meaning that all the uncertainties and error correlation information
have been stored in a machine-readable format using a structured metadata standard.

For the processing to L1B, the input quantities are simply the measurands from L1A, for which the uncertainties and error-correlation are already defined. 
The measurement function is a simple averaging function. Uncertainties are again propagated with punpy.

Similarly, the input quantities and their uncertainties for the L1C processing are defined by the previous processing levels.
The main steps in the L1C processing are the 2 interpolations. Here the measurement function is implemented within the interpolation tool in the CoMet toolkit. 
This tool also handles uncertainty propagation (which internally uses punpy) in an entirely analogous way.
The measurand (interpolated irradiances) and asoociated uncertainties and error-correlations are returned by the tool.

Finally, uncertainty are propagated to L2A with punpy using the measurement functions in :ref:`calibrate` and the input quantities from the L1C products. 
Some basic information on how to interface with the information with the uncertainty information in the HYPERNETS products is given in the :ref:`user_using_hypernets` page.
Further information and examples can be found on the CoMet website (``https://www.comet-toolkit.org/`_).

Storing uncertainty information as digital effects tables
#########################################################
As previously mentioned, detailed error-correlation information is calculated as part of the uncertainty
propagation. Storing this information in a space-efficient way is not trivial. To do this we use the `obsarray module<https://obsarray.readthedocs.io/en/latest/>`_
of the CoMet toolkit. obsarray uses a concept called ‘digital effects tables’ to store the errorcorrelation
information. This concept takes the parameterised error-correlation forms defined in the Quality
Assurance Framework for Earth Observation (`QA4EO<https://www.QA4EO.org>`_) and stores them in a standardised metadata
format. By using these parameterised error-correlation forms, it is not necessary to explicitely store the
error-correlation along all dimensions. Instead only the error-correlation with wavelength is explicitly
stored, and error-correlation with scans/series is captured as the ‘random’ or ‘systematic’ error-correlation
forms.

Another benefit to using obsarray, is that it allows for straightforward encoding of the uncertainty
and error-correlation variables. The error-correlation (with respect to wavelength) does not need to be
known at a very high precision. It can be saved as an 8-bit integer (leading to about a 0.01 precision in
the error-correlation coefficient). Similarly, the uncertainties can be encoded using a 16-bit integer to a
precision of 0.01%. Together, these encodings significantly reduce the amount of space required to store
the uncertainty information.

Finally, having the HYPERNETS products saved as ‘digital effects tables’ means they can easily be used
in further uncertainty propagation where all the error-correlation information is automatically taken into
account. See De Vis & Hunt (in prep.) and the `CoMet toolkit examples<https://www.comet-toolkit.org/examples/>`_ for further information (note
there is one example specific to HYPERNETS).

Uncertainty contributions
############################
Three uncertainty contributions are tracked throughout the processing:
-  Random uncertainty: Uncertainty component arising from the noise in the measurements, which
   does not have any error-correlation between different wavelengths or different repeated measurements
   (scans/series/sequences). The random uncertainties on the L0 data are taken to be the standard deviation
   between the scans that passed the quality checks. These uncertainties are then propagated all the way
   up to L2A.

-  Systematic independent uncertainty: Uncertainty component combining a range of different
   uncertainty contributions in the calibration. Only the components for which the errors are not correlated
   between radiance and irradiance are included. These include contributions from the uncertainties
   on the distance, alignment, non-linearity, wavelength, lamp (power, alignment, interpolation) and
   panel (calibration, alignment, interpolation, back reflectance) used during the calibration. Since
   the same lab calibration is used within the HYPERNETS PROCESSOR for repeated measurements
   (scans/series/sequences), the errors in the systematic independent uncertainty are assumed to be fully
   systematic (error-correlation of one) with respect to different scans/series/sequences. With respect to
   wavelength, we combine the different error-correlations of the different contributions and calculate a
   custom error-correlation matrix between the different wavelengths. These uncertainties are included in
   the L1A-L2A data products.

-  Systematic uncertainty correlated between radiance and irradiance: Uncertainty component
   combining a range of different uncertainty contributions in the calibration. Only the components for
   which the errors are correlated between radiance and irradiance are included. This error-correlation
   means this component will become negligible when taking the ratio of radiance and irradiance (i.e. in
   the L2A reflectance products), which is why we separate it from the systematic independent uncertainty.
   The systematic uncertainty correlated between radiance and irradiance includes contributions from
   the uncertainties on the lamp (calibration, age). Since the same lab calibration is used within the
   HYPERNETS PROCESSOR for repeated measurements (scans/series/sequences), the errors in the
   systematic independent uncertainty are assumed to be fully systematic (error-correlation made up
   of ones) with respect to different scans/series/sequences. With respect to wavelength, we combine
   the different error-correlations of the different contributions and calculate a custom error-correlation
   matrix between the different wavelengths. These uncertainties are present in the L1A-L1C products.

The temperature and spectral straylight uncertainties will be improved in future versions.
Additionally, there is an uncertainty to be added on the HYPSTAR responsivity change since calibration
(drift/ageing of spectrometer and optics). More post-deployment calibrations are necessary before we can
quantify this contribution. Other uncertainty contributions not yet included in the uncertainty budget will
also be considered in the future, such as uncertainties on the sensitivity to polarisation, uncertainties in
the cosine response of the irradiance optics, the effects of the platform/mast on the observed upwelling
radiances (e.g. Talone and Zibordi, 2018), or on the air-water interface reflectance corrections. Uncertainties
on the Spectral Response Functions (SRF) of the radiance and irradiance sensors (particularly the difference
between the two is important when calculating reflectance) should also be considered (see also Ruddick
et al., 2023). To account for these missing uncertainty contributions, a placeholder uncertainty of 2% is
added to the systematic independent uncertainty, assuming systematic spectral correlation. In the strong
atmospheric absorption features (i.e., 757.5-767.5 nm and 1350-1390 nm), an additional placeholder
uncertainty of 50% (assuming random spectral error correlation) is added to account for the difference in
SRF becoming dominant.



