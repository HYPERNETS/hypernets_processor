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


    def average_l0(self, dataset_l0, dataset_l0_bla):
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
        dataset_l0b = self.templ.l0b_template_from_l0_dataset_land(dataset_l0)
        flags = ["outliers","L0_thresholds", "L0_discontinuity"]
        for var in dataset_l0b.variables:
            if var=="digital_number":
                measurand, measurand_std,n_valid=self.calc_mean_masked(
                    dataset_l0, "digital_number",flags,return_std=True)
                dataset_l0b["digital_number"].values=measurand
                dataset_l0b["std_digital_number"].values=measurand_std.astype(dataset_l0b["std_digital_number"].values.dtype)
                dataset_l0b["n_valid_scans"].values=n_valid.astype(dataset_l0b["n_valid_scans"].values.dtype)
            elif var=="dark_signal":
                dataset_l0b["dark_signal"].values=self.calc_mean_masked(
                    dataset_l0_bla, "digital_number",flags)
            elif var=="u_rel_random_dark_signal":
                dataset_l0b["u_rel_random_dark_signal"].values=self.calc_mean_masked(dataset_l0_bla, "u_rel_random_digital_number",flags,rand_unc=True)
            elif "series" in dataset_l0b[var].dims:
                if "u_rel_random" in var:
                    dataset_l0b[var].values=self.calc_mean_masked(dataset_l0,var,flags,rand_unc=True)
                elif "err_corr_" in var:
                    dataset_l0b[var].values=dataset_l0[var].values
                elif (not "std" in var) and (not "n_valid" in var):
                    dataset_l0b[var].values=self.calc_mean_masked(dataset_l0,var,flags)

        return dataset_l0b


    def average_l1b(self, measurandstring, dataset_l1a):
        if self.context.get_config_value("network") == "w":
            dataset_l1b = self.templ.l1b_template_from_l1a_dataset_water(measurandstring, dataset_l1a)
            flags = ["outliers"]
            out, out_std, n_valid = self.calc_mean_masked(dataset_l1a, measurandstring, flags, return_std=True)
            dataset_l1b[measurandstring].values = out
            dataset_l1b["std_{}".format(measurandstring)].values = out_std
            dataset_l1b["n_valid_scans"].values=n_valid

        else:
            dataset_l1b = self.templ.l1b_template_from_l1a_dataset_land(measurandstring, dataset_l1a)
            flags=["outliers"]
            dataset_l1b[measurandstring].values=self.calc_mean_masked(dataset_l1a, measurandstring,flags)

        dataset_l1b["u_rel_random_" + measurandstring].values = self.calc_mean_masked(\
            dataset_l1a,"u_rel_random_" + measurandstring,flags,rand_unc=True)
        dataset_l1b["u_rel_systematic_indep_"+measurandstring].values = self.calc_mean_masked\
        (dataset_l1a,"u_rel_systematic_indep_"+measurandstring,flags)
        dataset_l1b["u_rel_systematic_corr_rad_irr_"+measurandstring].values = self.calc_mean_masked\
        (dataset_l1a,"u_rel_systematic_corr_rad_irr_"+measurandstring,flags)

        dataset_l1b["err_corr_systematic_indep_"+measurandstring].values = \
                dataset_l1a["err_corr_systematic_indep_"+measurandstring].values
        dataset_l1b["err_corr_systematic_corr_rad_irr_"+measurandstring].values = \
                dataset_l1a["err_corr_systematic_corr_rad_irr_"+measurandstring].values
        accel_var=["acceleration_x_mean","acceleration_x_std",
                   "acceleration_y_mean","acceleration_y_std",
                   "acceleration_z_mean","acceleration_z_std"]
        for a in accel_var:
            dataset_l1b[a].values = self.calc_mean_masked(dataset_l1a,a,flags)

        return dataset_l1b


    def average_l1a(self, measurandstring, dataset_l1a):
        dataset_l1b = self.templ.l1b_template_from_l1a_dataset_water(measurandstring, dataset_l1a)
        flags = ["outliers","L0_thresholds", "L0_discontinuity"]

        for var in dataset_l1b.variables:
            if var==measurandstring:
                measurand, measurand_std, n_valid=self.calc_mean_masked(
                    dataset_l1a,measurandstring,flags,return_std=True)
                dataset_l1b[measurandstring].values = measurand
                dataset_l1b["std_"+measurandstring].values = measurand_std.astype(dataset_l1b["std_"+measurandstring].values.dtype)
                dataset_l1b["n_valid_scans"].values = n_valid.astype(dataset_l1b["n_valid_scans"].values.dtype)

            elif measurandstring in var:

                if "u_rel_random" in var:
                    dataset_l1b[var].values=self.calc_mean_masked(dataset_l1a,var,flags,rand_unc=True)
                elif "err_corr_" in var:
                    dataset_l1b[var].values=dataset_l1a[var].values
                elif (not "std" in var) and (not "n_valid" in var):
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
                                "reflectance","epsilon"]:
            measurand, measurand_std, n_valid=self.calc_mean_masked(
                dataset,measurandstring,flags,return_std=True)
            dataset_l2a[measurandstring].values = measurand
            dataset_l2a["std_"+measurandstring].values = measurand_std.astype(dataset_l2a["std_"+measurandstring].values.dtype)
            dataset_l2a["n_valid_scans"].values = n_valid.astype(dataset_l2a["n_valid_scans"].values.dtype)
            dataset_l2a["u_rel_random_"+measurandstring].values = self.calc_mean_masked(
                dataset,"u_rel_random_"+measurandstring,flags,rand_unc=True)
            dataset_l2a["u_rel_systematic_"+measurandstring].values = self.calc_mean_masked(
                dataset,"u_rel_systematic_"+measurandstring,flags)
            if not measurandstring=="epsilon":
                dataset_l2a["err_corr_systematic_"+measurandstring].values = \
                    dataset["err_corr_systematic_"+measurandstring].values

        return dataset_l2a

    def calc_mean_masked(self, dataset, var, flags, rand_unc=False, corr=False, return_std=False):
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
                ((len(series_id), len(dataset['wavelength']), len(dataset['wavelength'])),dtype=dataset[var].values.dtype)
            for i in range(len(series_id)):
                flagged = DatasetUtil.get_flags_mask_or(dataset['quality_flag'],flags)
                ids = np.where(
                    (dataset['series_id'] == series_id[i]) & (flagged == False))
                out[i] = np.mean(vals[:,:,ids],axis=3)[:,:,0]

            out = np.mean(out, axis=0)

        elif vals.ndim==1:
            out = np.empty((len(series_id),),dtype=dataset[var].values.dtype)
            if return_std:
                out_std = np.empty((len(series_id),),dtype=np.float32)
                n_valid = np.empty((len(series_id),),dtype=np.uint16)

            for i in range(len(series_id)):
                flagged = DatasetUtil.get_flags_mask_or(dataset['quality_flag'],flags)
                ids = np.where(
                    (dataset['series_id'] == series_id[i]) & (flagged == False))
                out[i] = np.mean(dataset[var].values[ids])
                if return_std:
                    out_std[i]=np.std(dataset[var].values[ids])
                    n_valid[i]=len(ids[0])
                if rand_unc:
                    out[i] = (np.sum(dataset[var].values[ids]**2))**0.5 / len(ids[0])
        else:
            out = np.empty((len(series_id), len(dataset['wavelength'])),dtype=dataset[var].values.dtype)
            if return_std:
                out_std = np.empty((len(series_id), len(dataset['wavelength'])),dtype=np.float32)
                n_valid = np.empty((len(series_id),),dtype=np.uint16)

            for i in range(len(series_id)):
                flagged = DatasetUtil.get_flags_mask_or(dataset['quality_flag'],flags)
                ids = np.where(
                    (dataset['series_id'] == series_id[i]) & (flagged == False))
                out[i] = np.mean(dataset[var].values[:, ids], axis=2)[:, 0]
                if return_std:
                    out_std[i]=np.std(dataset[var].values[:, ids], axis=2)[:, 0]
                    n_valid[i]=len(ids[0])
                if rand_unc:
                    out[i] = (np.sum(dataset[var].values[:, ids]**2, axis=2)[:, 0])**0.5 / len(ids[0])

        if return_std:
            return out.T, out_std.T, n_valid
        else:
            return out.T

    def calc_std_masked(self, dataset, var, flags, rand_unc=False, corr=False):
        series_id = np.unique(dataset['series_id'])

        out = np.empty((len(series_id), len(dataset['wavelength'])))

        for i in range(len(series_id)):
            flagged = np.any(
                [DatasetUtil.unpack_flags(dataset['quality_flag'])[x] for x in
                 flags],axis=0)
            ids = np.where(
                (dataset['series_id'] == series_id[i]) & (flagged == False))
            out[i] = np.std(dataset[var].values[:, ids], axis=2)[:, 0]

        return out.T