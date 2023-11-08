## parse PANTHYR measurement cycle
## i.e. count e and l measurements for each azimuth in the cycle
## zenith angle is used to differentiate Lsky and Lu
## QV July 2018
## Last modifications: 2019-07-10 (QV) renamed from PANTR, added .lower() to sensor ID as it is in some cases uppercase in the current deployment (RBINS ROOF)
from datetime import datetime
from hypernets_processor.rhymer.rhymer.shared.rhymer_shared import RhymerShared
from hypernets_processor.rhymer.rhymer.ancillary.rhymer_ancillary import RhymerAncillary
from hypernets_processor.rhymer.rhymer.processing.rhymer_processing import RhymerProcessing
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.interpolation.interpolate import Interpolate
from hypernets_processor.plotting.plotting import Plotting
from hypernets_processor.data_utils.average import Average
from obsarray.templater.dataset_util import DatasetUtil as du
from hypernets_processor.data_io.normalize_360 import normalizedeg
from hypernets_processor.data_utils.quality_checks import QualityChecks

import numpy as np
import math
import sys
from scipy.optimize import curve_fit
import configparser


class RhymerHypstar:

    def __init__(self, context):
        self.context = context
        self.templ = DataTemplates(context=context)
        self.writer = HypernetsWriter(context)
        self.avg = Average(context)
        self.intp = Interpolate(context)
        self.plot = Plotting(context)
        self.rhymeranc = RhymerAncillary(context)
        self.rhymerproc = RhymerProcessing(context)
        self.rhymershared = RhymerShared(context)
        self.qual = QualityChecks(context)

    def checkazimuths(self, rad):
        uprad = []
        for i in rad['scan']:
            scani = rad.sel(scan=i)
            senz = scani["viewing_zenith_angle"].values
            if senz < 90:
                measurement = 'upwelling_radiance'
                uprad.append(int(i))
        azis = np.unique(
            [round(normalizedeg(float(rad["viewing_azimuth_angle"].sel(scan=i).values), 0, 360)) for i in uprad])
        return (azis)

    def selectazimuths(self, rad, irr, a):
        scanaz_rad = []
        scanaz_irr = []
        for i in rad['scan']:
            scani_ = rad.sel(scan=i)
            sena_rad = round(normalizedeg(float(scani_["viewing_azimuth_angle"].values)))
            # change to less or equal to one to avoid missing scans due to rounding to lower values
            if abs(sena_rad - a) <= 1:
                scanaz_rad.append(int(i))
        for i in irr['scan']:
            scani_ = irr.sel(scan=i)
            sena_irr = round(normalizedeg(float(scani_["viewing_azimuth_angle"].values)))
            # change to less or equal to one to avoid missing scans due to rounding to lower values
            if abs(sena_irr - a) <= 1:
                scanaz_irr.append(int(i))

        ra = ((np.nanmean(rad["viewing_azimuth_angle"].sel(scan=scanaz_rad)) -
              np.nanmean(rad["solar_azimuth_angle"].sel(scan=scanaz_rad))) % 360)

        return rad.sel(scan=scanaz_rad), irr.sel(scan=scanaz_irr), ra

    def cycleparse(self, rad, irr, dataset_l1b):

        protocol = self.context.get_config_value("measurement_function_surface_reflectance")
        if self.context.logger is not None:
            self.context.logger.debug(protocol)
        nbrlu = self.context.get_config_value("n_upwelling_rad")
        nbred = self.context.get_config_value("n_upwelling_irr")
        nbrlsky = self.context.get_config_value("n_downwelling_rad")

        if (protocol != 'WaterNetworkProtocol') and (self.context.logger is not None):
            # here we should simply provide surface reflectance?
            # what about a non-standard protocol but that includes the required standard series?
            self.context.logger.error('Unknown measurement protocol: {}'.format(protocol))
        else:
            uprad = []
            downrad = []
            for i in rad['scan']:
                scani = rad.sel(scan=i)
                senz = scani["viewing_zenith_angle"].values
                if senz < 90:
                    measurement = 'upwelling_radiance'
                    uprad.append(int(i))
                if senz >= 90:
                    measurement = 'downwelling_radiance'
                    downrad.append(int(i))
                if measurement is None: continue

            lu = rad.sel(scan=uprad)
            lsky = rad.sel(scan=downrad)

            # print("this is coeff. of variation for downwelling radiance".format(self.qual.qc_illumination(lsky, 'radiance')))
            # if self.qual.qc_illumination(lsky, 'radiance') > 0.1:
            #     self.context.logger.info(
            #         "Non constant illumination for sequence {}".format(dataset_l1b.attrs['sequence_id']))
            #     self.context.anomaly_handler.add_anomaly("nu")
            #     for i in range(len(dataset_l1b["quality_flag"].values)):
            #         dataset_l1b["quality_flag"][i] = DatasetUtil.set_flag(
            #             dataset_l1b["quality_flag"][i], "variable_radiance"
            #         )

            for i in lu['scan']:
                scani = lu.sel(scan=i)
                sena = scani["viewing_azimuth_angle"].values
                senz = scani["viewing_zenith_angle"].values
                if self.context.logger is not None:
                    self.context.logger.debug(scani['acquisition_time'].values)
                ts = datetime.utcfromtimestamp(int(scani['acquisition_time'].values))
                # not fromtimestamp?

                if (senz != 'NULL') & (sena != 'NULL'):
                    senz = float(senz)
                    sena = abs(float(sena))
                else:
                    dataset_l1b['quality_flag'] = du.set_flag(dataset_l1b.sel(scan=i)['quality_flag'], "angles_missing")
                    if self.context.logger is not None:
                        self.context.logger.info('NULL angles: Aquisition time {}, {}'.format(ts, ', '.join(
                            ['{}:{}'.format(k, scani[k].values) for k in ['scan', 'quality_flag']])))
                    continue

            # check if we have the same azimuth for lu and lsky
            sena_lu = np.unique(lu["viewing_azimuth_angle"].values)
            sena_lsky = np.unique(lsky["viewing_azimuth_angle"].values)
            sena_lu = sena_lu % 360
            print(sena_lu)
            sena_lsky = sena_lsky % 360
            print(sena_lsky)

            for i in sena_lu:
                if (np.round(i)-1 not in np.round(sena_lsky) and np.round(i) not in np.round(sena_lsky) and
                        np.round(i) + 1 not in np.round(sena_lsky)) :
                    dataset_l1b["quality_flag"][dataset_l1b["viewing_azimuth_angle"] == i] = du.set_flag(
                        dataset_l1b["quality_flag"][dataset_l1b["viewing_azimuth_angle"] == i], "lu_eq_missing")
                    if self.context.get_config_value("verbosity") > 2:
                        ts = [datetime.utcfromtimestamp(x) for x in
                              lu['acquisition_time'][lu["viewing_azimuth_angle"] == i].values]
                        if self.context.logger is not None:
                            self.context.logger.info(
                                'No azimuthal equivalent downwelling radiance measurement: Aquisition time {}, {}'.format(
                                    ts, ', '.join(
                                        ['{}:{}'.format(k, lu[k][lu["viewing_azimuth_angle"] == i].values) for k in
                                         ['scan', 'quality_flag']])))
                            self.context.logger.error("Ld missing for fresnel correction")
                        self.context.anomaly_handler.add_anomaly("l")

            # check if we have the required fresnel angle for lsky
            senz_lu = np.unique(lu["viewing_zenith_angle"].values)
            senz_lsky = 180 - np.unique(lsky["viewing_zenith_angle"].values)

            for i in senz_lu:
                if (np.round(i)-1 not in np.round(senz_lsky) and np.round(i) not in np.round(senz_lsky) and
                        np.round(i) + 1 not in np.round(senz_lsky)) :
                    dataset_l1b["quality_flag"][dataset_l1b["viewing_azimuth_angle"] == i] = du.set_flag(
                        dataset_l1b["quality_flag"][dataset_l1b["viewing_azimuth_angle"] == i], "fresnel_angle_missing")
                    ts = [datetime.utcfromtimestamp(x) for x in
                          lu['acquisition_time'][lu["viewing_zenith_angle"] == i].values]
                    if self.context.logger is not None:
                        self.context.logger.info(
                            'No downwelling radiance measurement at appropriate fresnel angle: Aquisition time {}, {}'.format(
                                ts, ', '.join(
                                    ['{}:{}'.format(k, lu[k][lu["viewing_azimuth_angle"] == i].values) for k
                                     in ['scan', 'quality_flag']])))
                        self.context.logger.error("Ld missing for fresnel correction")
                    self.context.anomaly_handler.add_anomaly("l")

            # check if correct number of radiance and irradiance data
            flags = ["nonlinearity", "bad_pointing", "outliers"]
            # flags = ["nonlinearity", "bad_pointing", "outliers",
            #          "angles_missing", "lu_eq_missing", "fresnel_angle_missing", "ld_ed_clearsky_failing",
            #          "fresnel_default", "temp_variability_ed", "temp_variability_lu", "simil_fail"]
            flagged = np.any(
                [du.unpack_flags(lu['quality_flag'])[x] for x in
                 flags], axis=0)
            ids = np.where(flagged == False)[0]
            dataset_l1b.attrs["nlu"] = len(ids)
            print("Number of valid Lu: {}".format(len(ids)))
            if len(ids) < nbrlu:
                for i in range(len(dataset_l1b["scan"])):
                    dataset_l1b["quality_flag"][dataset_l1b["scan"] == i] = du.set_flag(
                        dataset_l1b["quality_flag"][dataset_l1b["scan"] == i], "min_nbrlu")
                if self.context.logger is not None:
                    self.context.logger.info(
                        "Not enough upwelling radiance data for sequence {}".format(lu.attrs['sequence_id']))
                self.context.anomaly_handler.add_anomaly("nlu")

            flagged = np.any(
                [du.unpack_flags(lsky['quality_flag'])[x] for x in
                 flags], axis=0)
            ids = np.where(flagged == False)[0]
            dataset_l1b.attrs["nld"] = len(ids)

            print("Number of valid Ld: {}".format(len(ids)))

            if len(ids) < nbrlsky:
                for i in range(len(dataset_l1b["scan"])):
                    dataset_l1b["quality_flag"][dataset_l1b["scan"] == i] = du.set_flag(
                        dataset_l1b["quality_flag"][dataset_l1b["scan"] == i], "min_nbrlsky")
                if self.context.logger is not None:
                    self.context.logger.info(
                        "Not enough downwelling radiance data for sequence {}".format(lsky.attrs['sequence_id']))
                self.context.anomaly_handler.add_anomaly("nls")

            flagged = np.any(
                [du.unpack_flags(irr['quality_flag'])[x] for x in
                 flags], axis=0)
            ids = np.where(flagged == False)[0]
            dataset_l1b.attrs["ned"] = len(ids)
            print("Number of valid Ed: {}".format(len(ids)))

            if len(ids) < nbred:
                for i in range(len(dataset_l1b["scan"])):
                    dataset_l1b["quality_flag"][dataset_l1b["scan"] == i] = du.set_flag(
                        dataset_l1b["quality_flag"][dataset_l1b["scan"] == i], "min_nbred")
                if self.context.logger is not None:
                    self.context.logger.info(
                        "Not enough downwelling irradiance data for sequence {}".format(irr.attrs['sequence_id']))
                self.context.anomaly_handler.add_anomaly("ned")

            return lu, lsky, irr, dataset_l1b

    def get_wind(self, l1b):

        lat = l1b.attrs['site_latitude']
        lon = l1b.attrs['site_longitude']
        wind = []

        ## inform
        if self.context.get_config_value("fresnel_option") == 'Ruddick2006':
            if self.context.logger is not None:
                self.context.logger.info("Apply Ruddick et al., 2006")
            else:
                print("Apply Ruddick et al., 2006")
        if self.context.get_config_value("fresnel_option") == 'Mobley1999':
            if self.context.logger is not None:
                self.context.logger.info("Apply Mobley 1999")
            else:
                print("Apply Mobley, 1999")

        wa = self.context.get_config_value("wind_ancillary")
        if not wa:
            if self.context.logger is not None:
                self.context.logger.info("Default wind speed {}".format(self.context.get_config_value("wind_default")))
            else:
                print("Default wind speed {}".format(self.context.get_config_value("wind_default")))

        for i in range(len(l1b.scan)):
            wa = self.context.get_config_value("wind_ancillary")
            if not wa:
                l1b["quality_flag"][l1b["scan"] == i] = du.set_flag(l1b["quality_flag"][l1b["scan"] == i],
                                                                    "def_wind_flag")
                wind.append(self.context.get_config_value("wind_default"))
                l1b.attrs["fresnel_wind_source"] = "Default - {}".format(self.context.get_config_value("wind_default"))

            elif self.context.get_config_value("wind_ancillary") == 'NCEP':
                isotime = datetime.utcfromtimestamp(l1b['acquisition_time'].values[i]).strftime('%Y-%m-%d %H:%M:%S')
                anc_wind = self.rhymeranc.ts_wind(isotime, l1b.attrs['site_id'])
                if anc_wind is not None:
                    wind.append(anc_wind)
                l1b.attrs["fresnel_wind_source"] = "NCEP"


            elif self.context.get_config_value("wind_ancillary") == 'GDAS':
                isotime = datetime.utcfromtimestamp(l1b['acquisition_time'].values[i]).strftime('%Y-%m-%d %H:%M:%S')
                anc_wind = self.rhymeranc.gdas_extract(isotime, lon, lat)
                if anc_wind is not None:
                    wind.append(anc_wind['w'])
                    now = datetime.now()
                    l1b.attrs["fresnel_wind_source"] = "NCEP/GDAS FNL 0.25 ds083.3 | DOI: 10.5065/D65Q4T4Z"

        l1b['fresnel_wind'].values = wind
        return l1b

    def get_fresnelrefl(self, l1b):

        ## read mobley rho lut
        fresnel_coeff = np.zeros(len(l1b.scan))
        fresnel_vza = np.zeros(len(l1b.scan))
        fresnel_raa = np.zeros(len(l1b.scan))
        fresnel_sza = np.zeros(len(l1b.scan))

        wind = l1b["fresnel_wind"].values
        for i in range(len(l1b.scan)):
            fresnel_vza[i] = l1b['viewing_zenith_angle'][i].values
            fresnel_sza[i] = l1b['solar_zenith_angle'][i].values
            ra = (l1b['viewing_azimuth_angle'][i].values -
                                  l1b['solar_azimuth_angle'][i].values) % 360

            fresnel_raa[i]=((ra - 180) % 360) - 180

            ## get fresnel reflectance
            if self.context.get_config_value("fresnel_option") == 'Mobley1999':
                if (fresnel_sza[i] is not None) & (fresnel_raa[i] is not None) & (abs(fresnel_raa[i]) > 180):
                    sza = min(fresnel_sza[i], 79.999)
                    rhof = self.rhymerproc.mobley_lut_interp(sza, fresnel_vza[i], fresnel_raa[i],
                                                             wind=wind[i])
                else:
                    l1b["quality_flag"][l1b["scan"] == i] = du.set_flag(l1b["quality_flag"][l1b["scan"] == i],
                                                                        "fresnel_default")
                    rhof = self.context.get_config_value("rhof_default")
            if self.context.get_config_value("fresnel_option") == 'Ruddick2006':
                rhof = self.context.get_config_value("rhof_default")
                if wind[i] is not None:
                    rhof = rhof + 0.00039 * wind[i] + 0.000034 * wind[i] ** 2

            fresnel_coeff[i] = rhof
        l1b["rhof"].values = fresnel_coeff
        l1b["fresnel_vza"].values = fresnel_vza
        l1b["fresnel_raa"].values = fresnel_raa
        l1b["fresnel_sza"].values = fresnel_sza

        return l1b



    def process_l1c_int(self, l1a_rad, l1a_irr):

        # because we average to Lu scan we propagate values from radiance!
        dataset_l1flags = self.templ.l1c_int_template_from_l1a_dataset_water(l1a_rad)

        # print(pd.DataFrame(du.unpack_flags(dataset_l1b['quality_flag']).to_dataframe()))
        # No temporal quality checks but check if downwelling radiance varies by less than 10%
        dataset_l1flags, flags_rad = self.qual.qc_scan(l1a_rad, "radiance", dataset_l1flags)
        dataset_l1flags, flags_irr = self.qual.qc_scan(l1a_irr, "irradiance", dataset_l1flags)
        l1a_rad = l1a_rad.sel(scan=np.where(np.array(flags_rad) != 1)[0])
        l1a_irr = l1a_irr.sel(scan=np.where(np.array(flags_irr) != 1)[0])

        # check number of scans per cycle for up, down radiance and irradiance
        L1a_uprad, L1a_downrad, L1a_irr, dataset_l1flags = self.cycleparse(l1a_rad, l1a_irr, dataset_l1flags)


        if self.qual.qc_illumination(L1a_downrad, 'radiance') > 0.1:
            self.context.logger.info(
                "Non constant illumination for sequence {}".format(L1a_downrad.attrs['sequence_id']))
            self.context.anomaly_handler.add_anomaly("nd")

        L1b_downrad = self.avg.average_l1a("radiance", L1a_downrad)
        L1b_irr = self.avg.average_l1a("irradiance", L1a_irr)

        # INTERPOLATE Lsky and Ed FOR EACH Lu SCAN! Threshold in time -> ASSIGN FLAG
        # interpolate_l1b_w calls interpolate_irradiance which includes interpolation of the
        # irradiance wavelength to the radiance wavelength
        L1c_int = self.intp.interpolate_l1b_w(dataset_l1flags, L1a_uprad, L1b_downrad, L1b_irr)

        flags = ([ "nonlinearity", "bad_pointing", "outliers",
                 "angles_missing", "lu_eq_missing", "fresnel_angle_missing", "ld_ed_clearsky_failing",
                  "outliers",
                  "L0_thresholds",
                  "L0_discontinuity"
                  ])
                  #"temp_variability_ed", "temp_variability_lu"])
#                 "fresnel_default",  "simil_fail"]

        for measurandstring in ["irradiance", "downwelling_radiance"]:
            L1c_int["std_{}".format(measurandstring)].values = self.avg.calc_std_masked(
                L1c_int, measurandstring, flags).ravel()

        # pd.set_option('display.max_columns', None)  # or 1000
        # pd.set_option('display.max_rows', None)  # or 1000
        # pd.set_option('display.max_colwidth', -1)  # or 199
        # print(pd.DataFrame(du.unpack_flags(L1c_int['quality_flag']).to_dataframe()))

        L1c_int.attrs['nld'] = dataset_l1flags.attrs['nld']
        L1c_int.attrs['nlu'] = dataset_l1flags.attrs['nlu']
        L1c_int.attrs['ned'] = dataset_l1flags.attrs['ned']

        return L1c_int
