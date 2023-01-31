"""
Averaging class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.calibration.measurement_functions.measurement_function_factory import\
    MeasurementFunctionFactory

import time
import numpy as np
from obsarray.templater.dataset_util import DatasetUtil
import punpy

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "04/11/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"

class Average:
    def __init__(self,context):
        self.templ = DataTemplates(context=context)
        self.context = context
        self.writer=HypernetsWriter(context)
        self._measurement_function_factory = MeasurementFunctionFactory


    def average_l0(self, measurandstring, dataset_l0, dataset_l0_bla):
        """

        :param measurandstring:
        :type measurandstring:
        :param dataset_l0:
        :type dataset_l0:
        :param dataset_l0_bla:
        :type dataset_l0_bla:
        :param calibration_data:
        :type calibration_data:
        :return:
        :rtype:
        """
        dataset_l0b = self.templ.l0b_template_from_l0_dataset_land(measurandstring, dataset_l0)
        flags = ["outliers","L0_thresholds", "L0_discontinuity"]
        for var in dataset_l0b.variables:
            if var=="dark_signal":
                meanvar=self.calc_mean_masked(dataset_l0_bla, "digital_number",flags)
                dataset_l0b["dark_signal"].values=self.calc_mean_masked(dataset_l0_bla, "digital_number",flags)
            elif var=="u_rel_random_dark_signal":
                dataset_l0b["u_rel_random_dark_signal"].values=self.calc_mean_masked(dataset_l0_bla, "u_rel_random_digital_number",flags,rand_unc=True)
            elif "series" in dataset_l0b[var].dims:
                if "u_rel_random" in var:
                    dataset_l0b[var].values=self.calc_mean_masked(dataset_l0,var,flags,rand_unc=True)
                elif "err_corr_" in var:
                    dataset_l0b[var].values=dataset_l0[var].values
                else:
                    dataset_l0b[var].values=self.calc_mean_masked(dataset_l0,var,flags)

        return dataset_l0b

    def average_l1a(self, measurandstring, dataset_l1a):

        dataset_l1b = self.templ.l1b_template_from_l1a_dataset_water(measurandstring, dataset_l1a)
        flags = ["outliers","L0_thresholds", "L0_discontinuity"]

        for var in dataset_l1b.variables:
            if measurandstring in var:
                if "u_rel_random" in var:
                    dataset_l1b[var].values=self.calc_mean_masked(dataset_l1a,var,flags,rand_unc=True)
                elif "err_corr_" in var:
                    dataset_l1b[var].values=dataset_l1a[var].values
                else:
                    dataset_l1b[var].values=self.calc_mean_masked(dataset_l1a,var,flags)

        return dataset_l1b

    def average_L2(self,dataset):
        # flags = ["saturation","nonlinearity","bad_pointing","outliers",
        #                  "angles_missing","lu_eq_missing","fresnel_angle_missing",
        #                  "fresnel_default","temp_variability_ed","temp_variability_lu",
        #                  "min_nbred","min_nbrlu","min_nbrlsky", "simil_fail"]

        flags = ["saturation","nonlinearity","bad_pointing","outliers",
                         "angles_missing","lu_eq_missing","fresnel_angle_missing",
                         "fresnel_default","temp_variability_ed","temp_variability_lu", "simil_fail"]

        dataset_l2a = self.templ.l2_from_l1c_dataset(dataset, flags)


        for measurandstring in ["water_leaving_radiance","reflectance_nosc",
                                "reflectance"]:
            dataset_l2a[measurandstring].values = self.calc_mean_masked(
                dataset,measurandstring,flags)
            dataset_l2a["u_rel_random_"+measurandstring].values = self.calc_mean_masked(
                dataset,"u_rel_random_"+measurandstring,flags,rand_unc=True)
            dataset_l2a["u_rel_systematic_"+measurandstring].values = self.calc_mean_masked(
                dataset,"u_rel_systematic_"+measurandstring,flags)
            dataset_l2a["err_corr_systematic_"+measurandstring].values = \
                dataset["err_corr_systematic_"+measurandstring].values

        return dataset_l2a

    def calc_mean_masked(self, dataset, var, flags, rand_unc=False, corr=False):
        """

        :param dataset:
        :type dataset:
        :param var:
        :type var:
        :param flags:
        :type flags:
        :param rand_unc:
        :type rand_unc:
        :param corr:
        :type corr:
        :return:
        :rtype:
        """
        series_id = np.unique(dataset['series_id'])
        vals=dataset[var].values
        if corr:
            out = np.empty\
                ((len(series_id), len(dataset['wavelength']), len(dataset['wavelength'])))
            for i in range(len(series_id)):
                flagged = DatasetUtil.get_flags_mask_or(dataset['quality_flag'],flags)
                ids = np.where(
                    (dataset['series_id'] == series_id[i]) & (flagged == False))
                out[i] = np.mean(vals[:,:,ids],axis=3)[:,:,0]

            out = np.mean(out, axis=0)

        elif vals.ndim==1:
            out = np.empty((len(series_id),))

            for i in range(len(series_id)):
                flagged = DatasetUtil.get_flags_mask_or(dataset['quality_flag'],flags)
                ids = np.where(
                    (dataset['series_id'] == series_id[i]) & (flagged == False))
                out[i] = np.mean(dataset[var].values[ids])

                if rand_unc:
                    out[i] = (np.sum(dataset[var].values[ids]**2))**0.5 / len(ids[0])
        else:
            out = np.empty((len(series_id), len(dataset['wavelength'])))

            for i in range(len(series_id)):
                flagged = DatasetUtil.get_flags_mask_or(dataset['quality_flag'],flags)
                ids = np.where(
                    (dataset['series_id'] == series_id[i]) & (flagged == False))
                out[i] = np.mean(dataset[var].values[:, ids], axis=2)[:, 0]
                if rand_unc:
                    out[i] = (np.sum(dataset[var].values[:, ids]**2, axis=2)[:, 0])**0.5 / len(ids[0])

        return out.T
