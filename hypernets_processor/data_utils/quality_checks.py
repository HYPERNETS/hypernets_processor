"""
Averaging class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.plotting.plotting import Plotting

import punpy
import numpy as np
import warnings
import os
import xarray as xr
import matplotlib.pyplot as plt
import pysolar
import datetime
from obsarray.templater.dataset_util import DatasetUtil

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "04/11/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"

dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
refdat_path = os.path.join(dir_path,"data","quality_comparison_data")

class QualityChecks:
    def __init__(self,context):
        self.context=context
        self.plot=Plotting(context)


    def perform_quality_check_L0(self, datasetl0, series_ids):
        mask = []
        mask_threshold = []
        mask_outliers = []
        mask_discontinuity = []
        for i in range(len(series_ids)):
            ids = np.where(datasetl0["series_id"] == series_ids[i])[0]

            data_subset = datasetl0["digital_number"].values[:, ids]
            intsig = np.nanmean(data_subset, axis=0)
            mask_all_i = np.zeros_like(intsig)  # mask the columns that have NaN
            mask_threshold_i = self.threshold_checks(data_subset)
            mask_outliers_i = self.outlier_checks(data_subset)
            mask_discontinuity_i = self.discontinuity_checks(data_subset)
            mask_all_i[np.where(mask_threshold_i==1)] = 1
            mask_all_i[np.where(mask_outliers_i == 1)] = 1
            # mask_all_i[np.where(mask_discontinuity_i==1)] = 1

            if all(mask_all_i == 1):
                self.context.logger.error(
                    "None of the scans for series passed the quality control criteria"
                )
                self.context.anomaly_handler.add_anomaly("q")

            mask = np.append(mask, mask_all_i)
            mask_threshold = np.append(mask_threshold, mask_threshold_i)
            mask_outliers = np.append(mask_outliers, mask_outliers_i)
            mask_discontinuity = np.append(mask_discontinuity, mask_discontinuity_i)
        datasetl0["quality_flag"][np.where(mask_outliers == 1)] = DatasetUtil.set_flag(
            datasetl0["quality_flag"][np.where(mask_outliers == 1)], "outliers"
        )  # for i in range(len(mask))]
        datasetl0["quality_flag"][np.where(mask_threshold == 1)] = DatasetUtil.set_flag(
            datasetl0["quality_flag"][np.where(mask_threshold == 1)], "L0_thresholds"
        )  # for i in range(len(mask))]
        datasetl0["quality_flag"][
            np.where(mask_discontinuity == 1)
        ] = DatasetUtil.set_flag(
            datasetl0["quality_flag"][np.where(mask_discontinuity == 1)],
            "L0_discontinuity",
        )  # for i in range(len(mask))]
        return datasetl0, mask

    def perform_quality_check_black(self, datasetl0, series_ids):
        mask = []
        mask_outliers = []
        mask_threshold = []
        mask_discontinuity = []
        for i in range(len(series_ids)):
            ids = np.where(datasetl0["series_id"] == series_ids[i])[0]

            data_subset = datasetl0["digital_number"].values[:, ids]
            intsig = np.nanmean(data_subset, axis=0)
            mask_all_i = np.zeros_like(intsig)  # mask the columns that have NaN
            mask_threshold_i = self.threshold_checks(data_subset)
            mask_outliers_i = self.outlier_checks(data_subset)
            mask_discontinuity_i = self.discontinuity_checks(data_subset)
            mask_all_i[np.where(mask_threshold_i==1)] = 1
            mask_all_i[np.where(mask_outliers_i == 1)] = 1
            #mask_all_i[np.where(mask_discontinuity_i==1)] = 1

            if all(mask_all_i == 1):
                self.context.logger.error(
                    "None of the dark scans for series passed the quality control criteria"
                )
                self.context.anomaly_handler.add_anomaly("q")

            mask = np.append(mask, mask_all_i)
            mask_threshold = np.append(mask_threshold, mask_threshold_i)
            mask_outliers = np.append(mask_outliers, mask_outliers_i)
        datasetl0["quality_flag"][np.where(mask == 1)] = DatasetUtil.set_flag(
            datasetl0["quality_flag"][np.where(mask == 1)], "dark_masked"
        )
        # datasetl0["quality_flag"][np.where(mask_threshold == 1)] = DatasetUtil.set_flag(
        #     datasetl0["quality_flag"][np.where(mask_threshold == 1)], "L0_thresholds"
        # )  # for i in range(len(mask))]

        return datasetl0, mask

    def perform_quality_check_comb(self, dataset_l1b, dataset_l1b_swir):
        # todo add these checks
        return dataset_l1b, dataset_l1b_swir

    def perform_quality_irradiance(self, dataset_l1b_irr):
        # todo add further checks
        vzas = dataset_l1b_irr["viewing_zenith_angle"].values
        szas = dataset_l1b_irr["solar_zenith_angle"].values

        for i, vza in enumerate(vzas):
            if np.abs(vza - 180) > 2:
                dataset_l1b_irr["irradiance"].values[:, i] = np.mean(
                    dataset_l1b_irr["irradiance"].values[
                    :, np.where(np.abs(vzas - 180) < 2.0)[0]
                    ],
                    axis=1,
                )
                self.context.logger.warning(
                    "One of the irradiance measurements did not have vza=180, so has been masked"
                )
                dataset_l1b_irr["quality_flag"][i] = DatasetUtil.set_flag(
                    dataset_l1b_irr["quality_flag"][i], "vza_irradiance"
                )  # for i in range(len(mask))]

        if self.context.get_config_value("clear_sky_check"):
            # could also be done by: https://pvlib-python.readthedocs.io/en/stable/auto_examples/plot_spectrl2_fig51A.html
            ref_szas = [0, 20, 40, 60, 70, 80]
            ref_sza = ref_szas[np.argmin(np.abs(ref_szas - np.mean(szas)))]
            system_id = dataset_l1b_irr.attrs["system_id"]
            ref_data = xr.open_dataset(
                os.path.join(
                    refdat_path,
                    "solar_irradiance_hypernets_sza%s_%s.nc" % (ref_sza, system_id),
                    )
            )
            # ref_irrtot = pysolar.radiation.get_radiation_direct(
            #     np.mean(dataset_l1b_irr["acquisition_time"]),90-ref_sza)
            irr_scaled = np.zeros_like(dataset_l1b_irr["irradiance"].values)
            for i, vza in enumerate(vzas):

                # irrtot=pysolar.radiation.get_radiation_direct(datetime.datetime.fromtimestamp(dataset_l1b_irr["acquisition_time"][i]),90-dataset_l1b_irr["solar_zenith_angle"].values[i])
                irr_scaled[:, i] = (
                        dataset_l1b_irr["irradiance"].values[:, i]
                        / np.cos(
                    np.pi / 180.0 * dataset_l1b_irr["solar_zenith_angle"].values[i]
                )
                        * np.cos(np.pi / 180.0 * ref_sza)
                )
                if (
                        np.count_nonzero(
                            irr_scaled[:, i] < 0.5 * ref_data["solar_irradiance_BOA"]
                        )
                        > 20
                ):
                    dataset_l1b_irr["quality_flag"][i] = DatasetUtil.set_flag(
                        dataset_l1b_irr["quality_flag"][i], "clear_sky_irradiance"
                    )

            if self.context.get_config_value("plot_clear_sky_check"):
                self.plot.plot_quality_irradiance(
                    dataset_l1b_irr, irr_scaled, ref_data["solar_irradiance_BOA"], ref_sza
                )

        return dataset_l1b_irr

    def perform_quality_check_L2a(self,dataset):
        #todo add these checks
        return dataset

    def outlier_checks(self,data_subset,k_unc=3):
        intsig = np.nanmean(data_subset,axis=0)
        mask = np.zeros_like(intsig)  # mask the columns that have NaN
        if len(intsig)>1:
            noisestd,noiseavg = self.sigma_clip(intsig)
            mask[np.where(np.abs(intsig-noiseavg) >= k_unc*noisestd)] = 1
            mask[np.where(np.abs(intsig-noiseavg) >= 0.25*intsig)] = 1
        return mask

    def threshold_checks(self,data_subset):
        intsig = np.nanmean(data_subset,axis=0)
        mask = np.zeros_like(intsig)  # mask the columns that have NaN
        mask[np.where(intsig >= 1e7)] = 1
        mask[np.where(intsig < 0)] = 1
        return mask

    def discontinuity_checks(self,data_subset):
        intsig = np.nanmean(data_subset,axis=0)
        mask = np.zeros_like(intsig)  # mask the columns that have NaN
        #todo add these checks
        return mask

    def sigma_clip(self,values,tolerance=0.01,median=True,sigma_thresh=3.0):
        # Remove NaNs from input values
        values = np.array(values)
        values = values[np.where(np.isnan(values) == False)]
        values_original = np.copy(values)

        # Continue loop until result converges
        diff = 10E10
        while diff > tolerance:
            # Assess current input iteration
            if median == False:
                average = np.mean(values)
            elif median == True:
                average = np.median(values)
            sigma_old = np.std(values)

            # Mask those pixels that lie more than 3 stdev away from mean
            check = np.zeros([len(values)])
            check[np.where(values > (average+(sigma_thresh*sigma_old)))] = 1
            # check[ np.where( values<(average-(sigma_thresh*sigma_old)) ) ] = 1
            values = values[np.where(check < 1)]

            # Re-measure sigma and test for convergence
            sigma_new = np.std(values)
            diff = abs(sigma_old-sigma_new)/sigma_old

        # Perform final mask
        check = np.zeros([len(values)])
        check[np.where(values > (average+(sigma_thresh*sigma_old)))] = 1
        check[np.where(values < (average-(sigma_thresh*sigma_old)))] = 1
        values = values[np.where(check < 1)]

        # Return results
        return sigma_new,average

