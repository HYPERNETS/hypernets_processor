"""
Averaging class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.dataset_util import DatasetUtil
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter

import numpy as np


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


    def average_l1b(self, measurandstring, dataset_l1a):

        if self.context.get_config_value("network") == "w":
            dataset_l1b = self.templ.l1b_template_from_l1a_dataset_water(measurandstring, dataset_l1a)
        else:
            dataset_l1b = self.templ.l1b_template_from_l1a_dataset_land(measurandstring, dataset_l1a)

        if self.context.get_config_value("network") == "l":
            flags=["outliers"]
        else:
            flags = []

        dataset_l1b[measurandstring].values = self.calc_mean_masked(dataset_l1a, measurandstring,flags)

        dataset_l1b["u_random_" + measurandstring].values = self.calc_mean_masked(\
            dataset_l1a,"u_random_" + measurandstring,flags,rand_unc=True)
        dataset_l1b["u_systematic_indep_"+measurandstring].values = self.calc_mean_masked\
        (dataset_l1a,"u_systematic_indep_"+measurandstring,flags)
        dataset_l1b["u_systematic_corr_rad_irr_"+measurandstring].values = self.calc_mean_masked\
        (dataset_l1a,"u_systematic_corr_rad_irr_"+measurandstring,flags)

        dataset_l1b["corr_random_" + measurandstring].values = np.eye(
                len(dataset_l1b["u_random_" + measurandstring].values))
        dataset_l1b["corr_systematic_indep_"+measurandstring].values = \
                dataset_l1a["corr_systematic_indep_"+measurandstring].values
        dataset_l1b["corr_systematic_corr_rad_irr_"+measurandstring].values = \
                dataset_l1a["corr_systematic_corr_rad_irr_"+measurandstring].values

        return dataset_l1b

    def average_L2(self,dataset):

        dataset_l2a = self.templ.l2_from_l1d_dataset(dataset)

        flags = ["saturation","nonlinearity","bad_pointing","outliers",
                         "angles_missing","lu_eq_missing","fresnel_angle_missing",
                         "fresnel_default","temp_variability_ed","temp_variability_lu",
                         "min_nbred","min_nbrlu","min_nbrlsky"]

        for measurandstring in ["water_leaving_radiance","reflectance_nosc",
                                "reflectance"]:
            dataset_l2a[measurandstring].values = self.calc_mean_masked(
                dataset,measurandstring,flags)
            dataset_l2a["u_random_"+measurandstring].values = self.calc_mean_masked(
                dataset,"u_random_"+measurandstring,flags,rand_unc=True)
            dataset_l2a["u_systematic_"+measurandstring].values = self.calc_mean_masked(
                dataset,"u_systematic_"+measurandstring,flags)
            dataset_l2a["corr_random_"+measurandstring].values = np.eye(
                len(dataset_l2a["u_systematic_"+measurandstring].values))
            dataset_l2a["corr_systematic_"+measurandstring].values = \
                dataset["corr_systematic_"+measurandstring].values

        return dataset_l2a

    def calc_mean_masked(self, dataset, var, flags, rand_unc=False, corr=False):
        series_id = np.unique(dataset['series_id'])
        if corr:
            out = np.empty\
                ((len(series_id), len(dataset['wavelength']), len(dataset['wavelength'])))


            for i in range(len(series_id)):
                flagged = np.any(
                    [DatasetUtil.unpack_flags(dataset['quality_flag'])[x] for x in
                     flags],axis=0)
                ids = np.where(
                    (dataset['series_id'] == series_id[i]) & (flagged == False))
                out[i] = np.mean(dataset[var].values[:,:,ids],axis=3)[:,:,0]

            out = np.mean(out, axis=0)

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
