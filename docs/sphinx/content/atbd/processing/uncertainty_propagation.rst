.. uncertainty - algorithm theoretical basis
   Author: seh2
   Email: sam.hunt@npl.co.uk
   Created: 6/11/20

.. _uncertainty:


Uncertainty Propagation 
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Uncertainties are propagated from product to product using the punpy tool (see also `the punpy ATBD' <https://punpy.readthedocs.io/en/latest/content/atbd.html>`_), which is part of the NPL CoMet toolkit.
A metrological approach is followed, where for each processing stage, a measurement function is defined, as well as the input quantities and the measurand. 
The uncertainties are then propagated from product to product using a Monte Carlo (MC) approach. For a detailed description of the MC method, we refer to `Supplement 1 to the
"Guide to the expression of uncertainty in measurement" - Propagation of distributions using a Monte Carlo method <https://www.bipm.org/utils/common/documents/jcgm/JCGM_101_2008_E.pdf>`_.

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





