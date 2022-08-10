"""
Averaging class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.calibration.measurement_functions.measurement_function_factory import\
    MeasurementFunctionFactory
from hypernets_processor.data_utils.propagate_uncertainties import PropagateUnc

import numpy as np
from obsarray.templater.dataset_util import DatasetUtil

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
        self._measurement_function_factory = MeasurementFunctionFactory()
        self.prop = PropagateUnc(context, parallel_cores=0)


    def average_l1b(self, measurandstring, dataset_l0, dataset_l0_bla, calibration_data):
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
        if self.context.get_config_value("network") == "w":
            dataset_l1b = self.templ.l1b_template_from_l1a_dataset_water(measurandstring, dataset_l0)
        else:
            dataset_l1b = self.templ.l1b_template_from_l1a_dataset_land(measurandstring, dataset_l0)

        if self.context.get_config_value("network") == "l":
            flags = ["outliers"]
        else:
            flags = ["outliers"]

        calibrate_function = self._measurement_function_factory.get_measurement_function(
            self.context.get_config_value("measurement_function_calibrate"))
        input_vars = calibrate_function.get_argument_names()

        input_qty = []
        u_random_input_qty = []
        for var in input_vars:
            if var=="dark_signal":
                meanvar=self.calc_mean_masked(dataset_l0_bla, "digital_number",flags)
                input_qty.append(meanvar)
                u_random_input_qty.append(self.calc_mean_masked(dataset_l0_bla, "u_rel_random_digital_number",flags,rand_unc=True)*meanvar)
            elif var=="integration_time":
                input_qty.append(self.calc_mean_masked(dataset_l0,var,flags))
                u_random_input_qty.append(None)
            else:
                try:
                    meanvar=self.calc_mean_masked(dataset_l0, var,flags)
                    input_qty.append(meanvar)
                except:
                    meanvar=calibration_data[var].values.astype("float32")
                    input_qty.append(meanvar)
                try:
                    u_random_input_qty.append(self.calc_mean_masked(dataset_l0, "u_rel_random_" + var,flags,rand_unc=True)*meanvar)
                except:
                    try:
                        u_random_input_qty.append((calibration_data["u_rel_random_"+var].values*
                                                   calibration_data[var].values).astype("float32"))
                    except:
                        u_random_input_qty.append(None)

        u_systematic_input_qty_indep,u_systematic_input_qty_corr,\
        corr_systematic_input_qty_indep,corr_systematic_input_qty_corr = self.prop.find_u_systematic_input_l1a(input_vars, dataset_l0, calibration_data)

        dataset_l1b = self.prop.process_measurement_function_l1a(measurandstring,
                                                                 dataset_l1b,
                                                                 calibrate_function.function,
                                                                 input_qty,
                                                                 u_random_input_qty,
                                                                 u_systematic_input_qty_indep,
                                                                 u_systematic_input_qty_corr,
                                                                 corr_systematic_input_qty_indep,
                                                                 corr_systematic_input_qty_corr)

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
            dataset_l2a["corr_random_"+measurandstring].values = np.eye(
                len(dataset_l2a["u_rel_systematic_"+measurandstring].values))
            dataset_l2a["corr_systematic_"+measurandstring].values = \
                dataset["corr_systematic_"+measurandstring].values

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
                flagged = np.any(
                    [DatasetUtil.unpack_flags(dataset['quality_flag'])[x] for x in
                     flags],axis=0)
                ids = np.where(
                    (dataset['series_id'] == series_id[i]) & (flagged == False))
                out[i] = np.mean(vals[:,:,ids],axis=3)[:,:,0]

            out = np.mean(out, axis=0)

        elif vals.ndim==1:
            out = np.empty((len(series_id),))

            for i in range(len(series_id)):
                flagged = np.any(
                    [DatasetUtil.unpack_flags(dataset['quality_flag'])[x] for x in
                     flags],axis=0)
                ids = np.where(
                    (dataset['series_id'] == series_id[i]) & (flagged == False))
                out[i] = np.mean(dataset[var].values[ids])

                if rand_unc:
                    out[i] = np.mean(dataset[var].values[ids])/len(
                        ids[0])
        else:
            out = np.empty((len(series_id), len(dataset['wavelength'])))

            for i in range(len(series_id)):
                flagged = np.any(
                    [DatasetUtil.unpack_flags(dataset['quality_flag'])[x] for x in
                     flags],axis=0)
                ids = np.where(
                    (dataset['series_id'] == series_id[i]) & (flagged == False))
                out[i] = np.mean(dataset[var].values[:, ids], axis=2)[:, 0]

                if rand_unc:
                    out[i] = (np.sum(dataset[var].values[:, ids]**2, axis=2)[:, 0])**0.5 / len(ids[0])

        return out.T
