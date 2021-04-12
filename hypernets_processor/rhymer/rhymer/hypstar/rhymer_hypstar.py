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
from hypernets_processor.data_io.dataset_util import DatasetUtil as du

import numpy as np
import math


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

    def qc_scan(self, dataset, measurandstring, dataset_l1b):
        ## no inclination
        ## difference at 550 nm < 25% with neighbours
        ##
        ## QV July 2018
        ## Last modifications: 2019-07-10 (QV) renamed from PANTR, integrated in rhymer
        # Modified 10/09/2020 by CG for the PANTHYR
        verbosity = self.context.get_config_value("verbosity")
        series_id = np.unique(dataset['series_id'])
        wave = dataset['wavelength'].values
        flags = np.zeros(shape=len(dataset['scan']))
        id = 0
        for s in series_id:

            scans = dataset['scan'][dataset['series_id'] == s]

            ##
            n = len(scans)
            ## get pixel index for wavelength
            iref, wref = self.rhymershared.closest_idx(wave, self.context.get_config_value("diff_wave"))

            cos_sza = []
            for i in dataset['solar_zenith_angle'].sel(scan=scans).values:
                cos_sza.append(math.cos(math.radians(i)))

            ## go through the current set of scans
            for i in range(n):
                ## test inclination
                ## not done

                if measurandstring == 'irradiance':
                    data = dataset['irradiance'].sel(scan=scans).T.values

                    ## test variability at 550 nm
                    if i == 0:
                        v = abs(1 - ((data[i][iref] / cos_sza[i]) / (data[i + 1][iref] / cos_sza[i + 1])))
                    elif i < n - 1:
                        v = max(abs(1 - ((data[i][iref] / cos_sza[i]) / (data[i + 1][iref] / cos_sza[i + 1]))),
                                abs(1 - ((data[i][iref] / cos_sza[i]) / (data[i - 1][iref] / cos_sza[i - 1]))))
                    else:
                        v = abs(1 - ((data[i][iref] / cos_sza[i]) / (data[i - 1][iref] / cos_sza[i - 1])))
                else:
                    data = dataset['radiance'].sel(scan=scans).T.values
                    ## test variability at 550 nm
                    if i == 0:
                        v = abs(1 - (data[i][iref] / data[i + 1][iref]))
                    elif i < n - 1:
                        v = max(abs(1 - (data[i][iref] / data[i + 1][iref])),
                                abs(1 - (data[i][iref] / data[i - 1][iref])))
                    else:
                        v = abs(1 - (data[i][iref] / data[i - 1][iref]))

                ## continue if value exceeds the cv threshold
                if v > self.context.get_config_value("diff_threshold"):
                    # get flag value for the temporal variability
                    if measurandstring == 'irradiance':
                        flags[id] = 1
                        dataset_l1b['quality_flag'][range(len(dataset_l1b['scan']))] = du.set_flag(
                            dataset_l1b["quality_flag"][range(len(dataset_l1b['scan']))],
                            "temp_variability_ed")
                    else:
                        flags[id] = 1
                        dataset_l1b['quality_flag'][range(len(dataset_l1b['scan']))] = du.set_flag(
                            dataset_l1b["quality_flag"][range(len(dataset_l1b['scan']))],
                            "temp_variability_lu")

                    seq = dataset.attrs["sequence_id"]
                    ts = datetime.utcfromtimestamp(dataset['acquisition_time'][i])

                    if verbosity > 2: self.context.logger.info(
                        'Temporal jump: in {}:  Aquisition time {}, {}'.format(seq, ts, ', '.join(
                            ['{}:{}'.format(k, dataset[k][scans[i]].values) for k in ['scan', 'quality_flag']])))
                id += 1

            return dataset_l1b, flags

    def cycleparse(self, rad, irr, dataset_l1b):

        protocol = self.context.get_config_value("measurement_function_surface_reflectance")
        self.context.logger.debug(protocol)
        nbrlu = self.context.get_config_value("n_upwelling_rad")
        nbred = self.context.get_config_value("n_upwelling_irr")
        nbrlsky = self.context.get_config_value("n_downwelling_rad")

        if protocol != 'WaterNetworkProtocol':
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

            for i in lu['scan']:
                scani = lu.sel(scan=i)
                sena = scani["viewing_azimuth_angle"].values
                senz = scani["viewing_zenith_angle"].values
                self.context.logger.debug(scani['acquisition_time'].values)
                ts = datetime.utcfromtimestamp(int(scani['acquisition_time'].values))
                # not fromtimestamp?

                if (senz != 'NULL') & (sena != 'NULL'):
                    senz = float(senz)
                    sena = abs(float(sena))
                else:
                    dataset_l1b['quality_flag'] = du.set_flag(dataset_l1b.sel(scan=i)['quality_flag'], "angles_missing")
                    self.context.logger.info('NULL angles: Aquisition time {}, {}'.format(ts, ', '.join(
                        ['{}:{}'.format(k, scani[k].values) for k in ['scan', 'quality_flag']])))
                    continue

            # check if we have the same azimuth for lu and lsky
            sena_lu = np.unique(lu["viewing_azimuth_angle"].values)
            sena_lsky = np.unique(lsky["viewing_azimuth_angle"].values)
            for i in sena_lu:
                if np.round(i) not in np.round(sena_lsky):
                    dataset_l1b["quality_flag"][dataset_l1b["viewing_azimuth_angle"] == i] = du.set_flag(
                        dataset_l1b["quality_flag"][dataset_l1b["viewing_azimuth_angle"] == i], "lu_eq_missing")
                    if self.context.get_config_value("verbosity") > 2:
                        ts = [datetime.utcfromtimestamp(x) for x in
                              lu['acquisition_time'][lu["viewing_azimuth_angle"] == i].values]
                        self.context.logger.info(
                            'No azimuthal equivalent downwelling radiance measurement: Aquisition time {}, {}'.format(
                                ts, ', '.join(
                                    ['{}:{}'.format(k, lu[k][lu["viewing_azimuth_angle"] == i].values) for k in
                                     ['scan', 'quality_flag']])))

            # check if we have the required fresnel angle for lsky
            senz_lu = np.unique(lu["viewing_zenith_angle"].values)
            senz_lsky = 180 - np.unique(lsky["viewing_zenith_angle"].values)
            for i in senz_lu:
                if i not in senz_lsky:
                    dataset_l1b["quality_flag"][dataset_l1b["viewing_azimuth_angle"] == i] = du.set_flag(
                        dataset_l1b["quality_flag"][dataset_l1b["viewing_azimuth_angle"] == i], "fresnel_angle_missing")
                    ts = [datetime.utcfromtimestamp(x) for x in
                          lu['acquisition_time'][lu["viewing_zenith_angle"] == i].values]
                    self.context.logger.info(
                        'No downwelling radiance measurement at appropriate fresnel angle: Aquisition time {}, {}'.format(
                            ts, ', '.join(
                                ['{}:{}'.format(k, lu[k][lu["viewing_azimuth_angle"] == i].values) for k
                                 in ['scan', 'quality_flag']])))

            # check if correct number of radiance and irradiance data

            if lu.scan[lu['quality_flag'] <= 0].count() < nbrlu:
                for i in range(len(dataset_l1b["scan"])):
                    dataset_l1b["quality_flag"][dataset_l1b["scan"] == i] = du.set_flag(
                        dataset_l1b["quality_flag"][dataset_l1b["scan"] == i], "min_nbrlu")
                self.context.logger.info(
                    "Not enough upwelling radiance data for sequence {}".format(lu.attrs['sequence_id']))
            if lsky.scan[lsky['quality_flag'] <= 1].count() < nbrlsky:
                for i in range(len(dataset_l1b["scan"])):
                    dataset_l1b["quality_flag"][dataset_l1b["scan"] == i] = du.set_flag(
                        dataset_l1b["quality_flag"][dataset_l1b["scan"] == i], "min_nbrlsky")
                self.context.logger.info(
                    "Not enough downwelling radiance data for sequence {}".format(lsky.attrs['sequence_id']))
            if irr.scan[irr['quality_flag'] <= 1].count() < nbred:
                for i in range(len(dataset_l1b["scan"])):
                    dataset_l1b["quality_flag"][dataset_l1b["scan"] == i] = du.set_flag(
                        dataset_l1b["quality_flag"][dataset_l1b["scan"] == i], "min_nbred")
                self.context.logger.info(
                    "Not enough downwelling irradiance data for sequence {}".format(irr.attrs['sequence_id']))

            return lu, lsky, irr, dataset_l1b

    def get_wind(self, l1b):

        lat = l1b.attrs['site_latitude']
        lon = l1b.attrs['site_latitude']
        wind = []

        wa = self.context.get_config_value("wind_ancillary")
        if not wa:
            self.context.logger.info("Default wind speed {}".format(self.context.get_config_value("wind_default")))

        for i in range(len(l1b.scan)):
            wa = self.context.get_config_value("wind_ancillary")
            if not wa:
                l1b["quality_flag"][l1b["scan"] == i] = du.set_flag(l1b["quality_flag"][l1b["scan"] == i],
                                                                    "def_wind_flag")
                wind.append(self.context.get_config_value("wind_default"))
            else:
                isodate = datetime.utcfromtimestamp(l1b['acquisition_time'].values[i]).strftime('%Y-%m-%d')
                isotime = datetime.utcfromtimestamp(l1b['acquisition_time'].values[i]).strftime('%H:%M:%S')
                anc_wind = self.rhymeranc.get_wind(isodate, lon, lat, isotime=isotime)
                if anc_wind is not None:
                    wind.append(anc_wind)
        l1b['fresnel_wind'].values = wind
        return l1b

    def get_fresnelrefl(self, l1b):

        ## read mobley rho lut
        fresnel_coeff = np.zeros(len(l1b.scan))
        fresnel_vza = np.zeros(len(l1b.scan))
        fresnel_raa = np.zeros(len(l1b.scan))
        fresnel_sza = np.zeros(len(l1b.scan))

        ## inform
        if self.context.get_config_value("fresnel_option") == 'Ruddick2006':
            self.context.logger.info("Apply Ruddick et al., 2006")
        if self.context.get_config_value("fresnel_option") == 'Mobley':
            self.context.logger.info("Apply Mobley 1999")

        wind = l1b["fresnel_wind"].values
        for i in range(len(l1b.scan)):
            fresnel_vza[i] = l1b['viewing_zenith_angle'][i].values
            fresnel_sza[i] = l1b['solar_zenith_angle'][i].values

            diffa = l1b['viewing_azimuth_angle'][i].values - l1b['solar_azimuth_angle'][i].values

            if diffa >= 360:
                diffa = diffa - 360
            elif 0 <= diffa < 360:
                diffa = diffa
            else:
                diffa = diffa + 360
            fresnel_raa[i] = abs((diffa - 180))

            ## get fresnel reflectance
            if self.context.get_config_value("fresnel_option") == 'Mobley':
                if (fresnel_sza[i] is not None) & (fresnel_raa[i] is not None):
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


    def qc_similarity(self, L1c):

        wave=L1c["wavelength"]
        wr=L1c.attrs["similarity_waveref"]
        wp=L1c.attrs["similarity_wavethres"]

        epsilon=L1c["epsilon"]
        ## get pixel index for wavelength
        irefr, wrefr = self.rhymershared.closest_idx(wave, wr)

        failSimil = []
        scans = L1c['scan']
        for i in range(len(scans)):
            data=L1c['reflectance_nosc'].sel(scan=i).values
            if abs(epsilon[i]) > wp * data[irefr]:
                failSimil.append(1)
            else:
                failSimil.append(0)
        return failSimil

    def process_l1c_int(self, l1a_rad, l1a_irr):

        # because we average to Lu scan we propagate values from radiance!
        dataset_l1b = self.templ.l1c_int_template_from_l1a_dataset_water(l1a_rad)
        # QUALITY CHECK: TEMPORAL VARIABILITY IN ED AND LSKY -> ASSIGN FLAG
        dataset_l1b, flags_rad = self.qc_scan(l1a_rad, "radiance", dataset_l1b)
        dataset_l1b, flags_irr = self.qc_scan(l1a_irr, "irradiance", dataset_l1b)
        # QUALITY CHECK: MIN NBR OF SCANS -> ASSIGN FLAG
        # remove temporal variability scans before average
        l1a_rad = l1a_rad.sel(scan=np.where(np.array(flags_rad) != 1)[0])
        l1a_irr = l1a_irr.sel(scan=np.where(np.array(flags_irr) != 1)[0])

        # check number of scans per cycle for up, down radiance and irradiance
        L1a_uprad, L1a_downrad, L1a_irr, dataset_l1b = self.cycleparse(l1a_rad, l1a_irr, dataset_l1b)

        L1b_downrad = self.avg.average_l1b("radiance", L1a_downrad)
        L1b_irr = self.avg.average_l1b("irradiance", L1a_irr)
        # INTERPOLATE Lsky and Ed FOR EACH Lu SCAN! Threshold in time -> ASSIGN FLAG
        # interpolate_l1b_w calls interpolate_irradiance which includes interpolation of the
        # irradiance wavelength to the radiance wavelength
        L1c_int = self.intp.interpolate_l1b_w(dataset_l1b,L1a_uprad, L1b_downrad, L1b_irr)
        return L1c_int
