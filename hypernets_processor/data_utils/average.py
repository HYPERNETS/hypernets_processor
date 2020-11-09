"""
Averaging class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.dataset_util import DatasetUtil
from hypernets_processor.data_io.data_templates import DataTemplates

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
    
    def average_l1b(self, measurandstring, dataset_l1a):

        dataset_l1b = self.templ.l1b_template_from_l1a_dataset_land(measurandstring, dataset_l1a)

        dataset_l1b[measurandstring].values = self.calc_mean_masked(dataset_l1a, measurandstring)
        dataset_l1b["u_random_" + measurandstring].values = self.calc_mean_masked(\
            dataset_l1a,"u_random_" + measurandstring,rand_unc=True)
        dataset_l1b["u_systematic_indep_"+measurandstring].values = self.calc_mean_masked\
        (dataset_l1a,"u_systematic_indep_"+measurandstring)
        dataset_l1b["u_systematic_corr_rad_irr_"+measurandstring].values = self.calc_mean_masked\
        (dataset_l1a,"u_systematic_corr_rad_irr_"+measurandstring)

        dataset_l1b["corr_random_" + measurandstring].values = np.eye(
                len(dataset_l1b["u_random_" + measurandstring].values))
        dataset_l1b["corr_systematic_indep_"+measurandstring].values = \
                dataset_l1a["corr_systematic_indep_"+measurandstring].values
        dataset_l1b["corr_systematic_corr_rad_irr_"+measurandstring].values = \
                dataset_l1a["corr_systematic_corr_rad_irr_"+measurandstring].values

        return dataset_l1b

    def calc_mean_masked(self, dataset, var, rand_unc=False, corr=False):
        series_id = np.unique(dataset['series_id'])
        if corr:
            out = np.empty\
                ((len(series_id), len(dataset['wavelength']), len(dataset['wavelength'])))

            print("corr",dataset[var].values)
            for i in range(len(series_id)):
                ids = np.where((dataset['series_id'] == series_id[i]) & np.invert(
                    DatasetUtil.unpack_flags(dataset["quality_flag"])["outliers"]))
                out[i] = np.mean(dataset[var].values[:,:,ids],axis=3)[:,:,0]

            out = np.mean(out, axis=0)

        else:
            out = np.empty((len(series_id), len(dataset['wavelength'])))

        for i in range(len(series_id)):
            ids = np.where((dataset['series_id'] == series_id[i]) &
                           np.invert
                (DatasetUtil.unpack_flags(dataset["quality_flag"])["outliers"]))
            out[i] = np.mean(dataset[var].values[:, ids], axis=2)[:, 0]

            if rand_unc:
                out[i] = out[i] / len(ids[0])

        return out.T