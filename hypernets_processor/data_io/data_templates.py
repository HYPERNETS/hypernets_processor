"""
Data template class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.hypernets_ds_builder import HypernetsDSBuilder
from hypernets_processor.data_io.dataset_util import DatasetUtil

import numpy as np

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "04/11/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"


class DataTemplates:
    def __init__(self, context):
        self.context = context
        self.hdsb = HypernetsDSBuilder(context=context)

    def calibration_dataset(self, wavs, nonlinearcals, wavcoef, caldates, nonlineardates, wavdates):
        """
        Makes all L1 templates for the data, and propagates the appropriate keywords from the L0 datasets.

        :param datasetl0:
        :type datasetl0:
        :return:
        :rtype:
        """

        cal_dim_sizes_dict = {"wavelength": len(wavs),
                              "nonlinearcoef": len(nonlinearcals),
                              "wavcoef": len(wavcoef),
                              "calibrationdates": len(caldates),
                              "nonlineardates": len(nonlineardates),
                              "wavdates": len(wavdates)}
        dataset_cal = self.hdsb.create_ds_template(cal_dim_sizes_dict,
                                                   ds_format="CAL")

        dataset_cal = dataset_cal.assign_coords(wavelength=wavs)
        dataset_cal = dataset_cal.assign_coords(nonlinearcoef=range(len(nonlinearcals)))
        dataset_cal = dataset_cal.assign_coords(wavcoef=range(len(wavcoef)))
        dataset_cal = dataset_cal.assign_coords(calibrationdates=caldates)
        dataset_cal = dataset_cal.assign_coords(nonlineardates=nonlineardates)
        dataset_cal = dataset_cal.assign_coords(wavdates=wavdates)
        return dataset_cal

    def l0_template_dataset(self, wvl, scanDim, fileformat, swir=False):
        """
        Makes all L1 templates for the data, and propagates the appropriate keywords from the L0 datasets.

        :param datasetl0:
        :type datasetl0:
        :return:
        :rtype:
        """
        dim_sizes_dict = {"wavelength":len(wvl),"scan":scanDim}
        # use template from variables and metadata in format
        dataset_l0 = self.hdsb.create_ds_template(dim_sizes_dict=dim_sizes_dict,
                                          ds_format=fileformat,swir=swir)
        dataset_l0.assign_coords(wavelength=wvl)
        dataset_l0.assign_coords(scan=np.linspace(1,scanDim,scanDim))

        return dataset_l0

    def l1a_template_from_l0_dataset(self, measurandstring, dataset_l0, swir=False):
        """
        Makes all L1 templates for the data, and propagates the appropriate keywords from the L0 datasets.

        :param datasetl0:
        :type datasetl0:
        :return:
        :rtype:
        """
        l1a_dim_sizes_dict = {"wavelength": len(dataset_l0["wavelength"]),
                              "scan": len(dataset_l0["scan"])}

        if measurandstring == "radiance":
            dataset_l1a = self.hdsb.create_ds_template(l1a_dim_sizes_dict,
                                                       ds_format="L_L1A_RAD",
                                                       propagate_ds=dataset_l0,
                                                       ds=dataset_l0,
                                                       swir=swir)
        elif measurandstring == "irradiance":
            dataset_l1a = self.hdsb.create_ds_template(l1a_dim_sizes_dict,
                                                       "L_L1A_IRR",
                                                       propagate_ds=dataset_l0,
                                                       ds= dataset_l0,
                                                       swir=swir)

        dataset_l1a = dataset_l1a.assign_coords(wavelength=dataset_l0.wavelength)

        return dataset_l1a

    def l1c_int_template_from_l1a_dataset_water(self, dataset_l1a):
        """
        Makes all L1 templates for the data, and propagates the appropriate keywords from the L0 datasets.
        :param datasetl0:
        :type datasetl0:
        :return:
        :rtype:
        """
        upscan = [i for i, e in enumerate(dataset_l1a['viewing_zenith_angle'].values) if e <= 90]
        l1b_dim_sizes_dict = {"wavelength": len(dataset_l1a["wavelength"]),
                              "scan": len(upscan)}

        dataset_l1b = self.hdsb.create_ds_template(l1b_dim_sizes_dict, "W_L1C",
                                                   propagate_ds=dataset_l1a,ds=dataset_l1a)
        dataset_l1b = dataset_l1b.assign_coords(wavelength=dataset_l1a.wavelength)
        # todo check whether here some additional keywords need to propagated (see land version).
        return dataset_l1b

    def l1b_template_from_l1a_dataset_water(self, measurandstring, dataset_l1a):
        """
        Makes all L1 templates for the data, and propagates the appropriate keywords from the L0 datasets.

        :param datasetl0:
        :type datasetl0:
        :return:
        :rtype:
        """
        l1b_dim_sizes_dict = {"wavelength": len(dataset_l1a["wavelength"]),
                              "series": len(np.unique(dataset_l1a['series_id']))}

        if measurandstring == "radiance":
            dataset_l1b = self.hdsb.create_ds_template(l1b_dim_sizes_dict, "W_L1B_RAD", propagate_ds=dataset_l1a,ds=dataset_l1a)
        elif measurandstring == "irradiance":
            dataset_l1b = self.hdsb.create_ds_template(l1b_dim_sizes_dict, "W_L1B_IRR", propagate_ds=dataset_l1a,ds=dataset_l1a)

        dataset_l1b = dataset_l1b.assign_coords(wavelength=dataset_l1a.wavelength)

        series_id = np.unique(dataset_l1a['series_id'])
        dataset_l1b["series_id"].values = series_id

        for variablestring in ["acquisition_time", "viewing_azimuth_angle", "viewing_zenith_angle",
                               "solar_azimuth_angle", "solar_zenith_angle"]:
            temp_arr = np.empty(len(series_id))
            for i in range(len(series_id)):
                ids = np.where((dataset_l1a['series_id'] == series_id[i]) & np.invert(
                    DatasetUtil.unpack_flags(dataset_l1a["quality_flag"])["outliers"]))
                temp_arr[i] = np.mean(dataset_l1a[variablestring].values[ids])
            dataset_l1b[variablestring].values = temp_arr

        return dataset_l1b

    def l1b_template_from_l1a_dataset_land(self, measurandstring, dataset_l1a):
        """
        Makes all L1 templates for the data, and propagates the appropriate keywords from the L0 datasets.

        :param datasetl0:
        :type datasetl0:
        :return:
        :rtype:
        """
        l1b_dim_sizes_dict = {"wavelength": len(dataset_l1a["wavelength"]),
                              "series": len(np.unique(dataset_l1a['series_id']))}

        if measurandstring == "radiance":
            dataset_l1b = self.hdsb.create_ds_template(l1b_dim_sizes_dict, "L_L1B_RAD", propagate_ds=dataset_l1a,ds=dataset_l1a)
        elif measurandstring == "irradiance":
            dataset_l1b = self.hdsb.create_ds_template(l1b_dim_sizes_dict, "L_L1B_IRR", propagate_ds=dataset_l1a,ds=dataset_l1a)

        dataset_l1b = dataset_l1b.assign_coords(wavelength=dataset_l1a.wavelength)

        series_id = np.unique(dataset_l1a['series_id'])
        dataset_l1b["series_id"].values = series_id

        for variablestring in ["acquisition_time", "viewing_azimuth_angle", "viewing_zenith_angle",
                               "solar_azimuth_angle", "solar_zenith_angle"]:
            temp_arr = np.empty(len(series_id))
            for i in range(len(series_id)):
                ids = np.where((dataset_l1a['series_id'] == series_id[i]) & np.invert(
                    DatasetUtil.unpack_flags(dataset_l1a["quality_flag"])["outliers"]))
                temp_arr[i] = np.mean(dataset_l1a[variablestring].values[ids])
            dataset_l1b[variablestring].values = temp_arr

        return dataset_l1b

    def l1b_template_from_combine(self, measurementstring, dataset, dataset_SWIR):
        wavs_vis = dataset["wavelength"].values
        wavs_swir = dataset_SWIR["wavelength"].values
        wavs = np.append(wavs_vis[np.where(wavs_vis <= self.context.get_config_value("combine_lim_wav"))],
                         wavs_swir[np.where(wavs_swir > self.context.get_config_value("combine_lim_wav"))])
        l1b_dim_sizes_dict = {"wavelength": len(wavs),
                              "series": len(dataset['series'])}
        if measurementstring == "radiance":
            dataset_l1b = self.hdsb.create_ds_template(l1b_dim_sizes_dict, "L_L1B_RAD",
                                                       propagate_ds=dataset, ds=dataset)
        if measurementstring == "irradiance":
            dataset_l1b = self.hdsb.create_ds_template(l1b_dim_sizes_dict, "L_L1B_IRR",
                                                       propagate_ds=dataset, ds=dataset)
        dataset_l1b = dataset_l1b.assign_coords(wavelength=wavs)
        return dataset_l1b

    def l1c_from_l1b_dataset(self, dataset_l1b):
        """
        Makes a L2 template of the data, and propagates the appropriate keywords from L1.

        :param datasetl0:
        :type datasetl0:
        :return:
        :rtype:
        """
        if self.context.get_config_value("network").lower() == "l":
            l1c_dim_sizes_dict = {"wavelength": len(dataset_l1b["wavelength"]),
                                  "series": len(dataset_l1b['series'])}

            dataset_l1c = self.hdsb.create_ds_template(l1c_dim_sizes_dict, "L_L1C",
                                                       propagate_ds=dataset_l1b, ds=dataset_l1b)
            dataset_l1c = dataset_l1c.assign_coords(wavelength=dataset_l1b.wavelength)

        elif self.context.get_config_value("network").lower() == "w":
            l1c_dim_sizes_dict = {"wavelength": len(dataset_l1b["wavelength"]),
                                  "scan": len(np.unique(dataset_l1b['scan']))}

            dataset_l1c = self.hdsb.create_ds_template(l1c_dim_sizes_dict, "W_L1C",
                                                       propagate_ds=dataset_l1b, ds=dataset_l1b)
            dataset_l1c = dataset_l1c.assign_coords(wavelength=dataset_l1b.wavelength)

        return dataset_l1c

    def l1ctemp_dataset(self, dataset_l1b, dataset_l1b_irr):
        """
        Makes a L2 template of the data, and propagates the appropriate keywords from L1.

        :param datasetl0:
        :type datasetl0:
        :return:
        :rtype:
        """
        if self.context.get_config_value("network").lower() == "l":
            l1c_dim_sizes_dict = {"wavelength": len(dataset_l1b["wavelength"]),
                                  "series": len(dataset_l1b_irr['series'])}

            dataset_l1c = self.hdsb.create_ds_template(l1c_dim_sizes_dict, "L_L1C",
                                                       propagate_ds=dataset_l1b, ds=dataset_l1b)
            dataset_l1c = dataset_l1c.assign_coords(wavelength=dataset_l1b.wavelength)

        elif self.context.get_config_value("network").lower() == "w":
            l1c_dim_sizes_dict = {"wavelength": len(dataset_l1b["wavelength"]),
                                  "scan": len(np.unique(dataset_l1b_irr['series']))}

            dataset_l1c = self.hdsb.create_ds_template(l1c_dim_sizes_dict, "W_L1C",
                                                       propagate_ds=dataset_l1b, ds=dataset_l1b)
            dataset_l1c = dataset_l1c.assign_coords(wavelength=dataset_l1b.wavelength)

        return dataset_l1c

    def l1d_from_l1c_dataset(self, datasetl1c):
        """
        Makes a L2 template of the data, and propagates the appropriate keywords from L1.

        :param datasetl0:
        :type datasetl0:
        :return:
        :rtype:
        """
        if self.context.get_config_value("network").lower() == "l":
            print("No L1D level for land")

        elif self.context.get_config_value("network").lower() == "w":
            l1d_dim_sizes_dict = {"wavelength": len(datasetl1c["wavelength"]),
                                  "scan": len(datasetl1c["scan"])}
            dataset_l1d = self.hdsb.create_ds_template(l1d_dim_sizes_dict, "W_L1D", propagate_ds=datasetl1c, ds=datasetl1c)
            dataset_l1d = dataset_l1d.assign_coords(wavelength=datasetl1c.wavelength)

        return dataset_l1d


    def l2_from_l1c_dataset(self, datasetl1c, flags):
        """
        Makes a L2 template of the data, and propagates the appropriate keywords from L1.
        :param datasetl0:
        :type datasetl0:
        :return:
        :rtype:
        """
        if self.context.get_config_value("network").lower() == "w":
            l2a_dim_sizes_dict = {"wavelength": len(datasetl1c["wavelength"]),
                                  "series": len(np.unique(datasetl1c['series_id']))}
            dataset_l2a = self.hdsb.create_ds_template(l2a_dim_sizes_dict, "W_L2A", propagate_ds=datasetl1c, ds=datasetl1c)
            dataset_l2a = dataset_l2a.assign_coords(wavelength=datasetl1c.wavelength)

            series_id = np.unique(datasetl1c['series_id'])
            dataset_l2a["series_id"].values = series_id
            for variablestring in ["acquisition_time", "viewing_azimuth_angle",
                                   "viewing_zenith_angle", "solar_azimuth_angle",
                                   "solar_zenith_angle", "epsilon", "rhof", "fresnel_wind", "vaa_ref","vaa_abs","vaa_ask"]:
                temp_arr = np.empty(len(series_id))
                for i in range(len(series_id)):
                    flagged = np.any(
                        [DatasetUtil.unpack_flags(datasetl1c['quality_flag'])[x] for x in
                         flags], axis=0)
                    ids = np.where(
                        (datasetl1c['series_id'] == series_id[i]) & (flagged == False))
                    # ids = np.where((datasetl1c['series_id'] == series_id[i]) & (
                    #         datasetl1c['quality_flag'] == 0))
                    temp_arr[i] = np.mean(datasetl1c[variablestring].values[ids])
                dataset_l2a[variablestring].values = temp_arr


        if self.context.get_config_value("network").lower() == "l":
            l2a_dim_sizes_dict = {"wavelength": len(datasetl1c["wavelength"]),
                                  "series": len(datasetl1c['series_id'])}
            dataset_l2a = self.hdsb.create_ds_template(l2a_dim_sizes_dict, "L_L2A", propagate_ds=datasetl1c, ds=datasetl1c)
            dataset_l2a = dataset_l2a.assign_coords(wavelength=datasetl1c.wavelength)

        return dataset_l2a
