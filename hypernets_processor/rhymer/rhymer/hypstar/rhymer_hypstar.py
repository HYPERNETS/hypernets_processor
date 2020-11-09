## parse PANTHYR measurement cycle
## i.e. count e and l measurements for each azimuth in the cycle
## zenith angle is used to differentiate Lsky and Lu
## QV July 2018
## Last modifications: 2019-07-10 (QV) renamed from PANTR, added .lower() to sensor ID as it is in some cases uppercase in the current deployment (RBINS ROOF)
from configparser import ConfigParser
from datetime import datetime
from hypernets_processor.rhymer.rhymer.shared.rhymer_shared import RhymerShared
from hypernets_processor.rhymer.rhymer.ancillary.rhymer_ancillary import RhymerAncillary
from hypernets_processor.rhymer.rhymer.processing.rhymer_processing import RhymerProcessing
from hypernets_processor.version import __version__
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.interpolation.interpolate import Interpolate
from hypernets_processor.plotting.plotting import Plotting
from hypernets_processor.data_io.format.metadata import METADATA_DEFS
from hypernets_processor.data_io.format.variables import VARIABLES_DICT_DEFS
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
        self.intp = Interpolate(context, MCsteps=1000)
        self.plot = Plotting(context)
        self.rhymeranc = RhymerAncillary(context)
        self.rhymerproc = RhymerProcessing(context)
        self.rhymershared = RhymerShared(context)

    def qc_scan(self, dataset, measurandstring):
        ## no inclination
        ## difference at 550 nm < 25% with neighbours
        ##
        ## QV July 2018
        ## Last modifications: 2019-07-10 (QV) renamed from PANTR, integrated in rhymer
        # Modified 10/09/2020 by CG for the PANTHYR
        verbosity = self.context.get_config_value("verbosity")
        series_id = np.unique(dataset['series_id'])
        wave = dataset['wavelength'].values

        for i in series_id:

            scans = dataset['scan'][dataset['series_id'] == i]

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
                        dataset['quality_flag'][dataset['scan'] == i] = du.set_flag(
                            dataset["quality_flag"][dataset['scan'] == i],
                            "temp_variability_ed")
                    else:
                        dataset['quality_flag'][dataset['scan'] == i] = du.set_flag(
                            dataset["quality_flag"][dataset['scan'] == i],
                            "temp_variability_lu")

                    seq = dataset.attrs["sequence_id"]
                    ts = datetime.utcfromtimestamp(dataset['acquisition_time'][i])

                    if verbosity > 2: self.context.logger.info(
                        'Temporal jump: in {}:  Aquisition time {}, {}'.format(seq, ts, ', '.join(
                            ['{}:{}'.format(k, dataset[k][scans[i]].values) for k in ['scan', 'quality_flag']])))

            return dataset

    def cycleparse(self, rad, irr):

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
                sena = scani["viewing_azimuth_angle"].values
                senz = scani["viewing_zenith_angle"].values
                self.context.logger.debug(scani['acquisition_time'].values)
                ts = datetime.utcfromtimestamp(int(scani['acquisition_time'].values))
                # not fromtimestamp?

                if (senz != 'NULL') & (sena != 'NULL'):
                    senz = float(senz)
                    sena = abs(float(sena))
                else:
                    scani['quality_flag'] = du.set_flag(scani['quality_flag'], "angles_missing")
                    self.context.logger.info('NULL angles: Aquisition time {}, {}'.format(ts, ', '.join(
                        ['{}:{}'.format(k, scani[k].values) for k in ['scan', 'quality_flag']])))
                    continue

                # ## identify measurement
                measurement = None
                ## radiance
                if senz < 90:
                    measurement = 'upwelling_radiance'
                    uprad.append(int(i))
                if senz >= 90:
                    measurement = 'downwelling_radiance'
                    downrad.append(int(i))
                if measurement is None: continue

            lu = rad.sel(scan=uprad)
            lsky = rad.sel(scan=downrad)

            # check if we have the same azimuth for lu and lsky
            sena_lu = np.unique(lu["viewing_azimuth_angle"].values)
            sena_lsky = np.unique(lsky["viewing_azimuth_angle"].values)
            for i in sena_lu:
                if i not in sena_lsky:
                    lu["quality_flag"][lu["viewing_azimuth_angle"] == i] = du.set_flag(
                        lu["quality_flag"][lu["viewing_azimuth_angle"] == i], "lu_eq_missing")
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
                    lu["quality_flag"][lu["viewing_azimuth_angle"] == i] = du.set_flag(
                        lu["quality_flag"][lu["viewing_azimuth_angle"] == i], "fresnel_angle_missing")
                    ts = [datetime.utcfromtimestamp(x) for x in
                          lu['acquisition_time'][lu["viewing_zenith_angle"] == i].values]
                    self.context.logger.info(
                        'No downwelling radiance measurement at appropriate fresnel angle: Aquisition time {}, {}'.format(
                            ts, ', '.join(
                                ['{}:{}'.format(k, lu[k][lu["viewing_azimuth_angle"] == i].values) for k
                                 in ['scan', 'quality_flag']])))

            # check if correct number of radiance and irradiance data

            if lu.scan[lu['quality_flag'] <= 0].count() < nbrlu:

                for i in range(len(lu["scan"])):
                    lu["quality_flag"][lu["scan"]==i] = du.set_flag(lu["quality_flag"][lu["scan"] == i], "outliers")
                self.context.logger.info(
                    "No enough upwelling radiance data for sequence {}".format(lu.attrs['sequence_id']))
            if lsky.scan[lsky['quality_flag'] <= 1].count() < nbrlsky:
                for i in range(len(lsky["scan"])):
                    lsky["quality_flag"][lsky["scan"] == i] = du.set_flag(lsky["quality_flag"][lsky["scan"] == i], "outliers")
                self.context.logger.info(
                    "No enough downwelling radiance data for sequence {}".format(lsky.attrs['sequence_id']))
            if irr.scan[irr['quality_flag'] <= 1].count() < nbred:
                for i in range(len(irr["scan"])):
                    irr["quality_flag"][irr["scan"] == i] = du.set_flag(irr["quality_flag"][irr["scan"] == i],
                                                                          "outliers")
                self.context.logger.info(
                    "No enough downwelling irradiance data for sequence {}".format(irr.attrs['sequence_id']))

            return lu, lsky, irr

    def get_wind(self, l1b):

        lat = l1b.attrs['site_latitude']
        lon = l1b.attrs['site_latitude']
        wind = []
        for i in range(len(l1b.scan)):
            wa = self.context.get_config_value("wind_ancillary")
            if not wa:
                l1b["quality_flag"][l1b["scan"] == i] = du.set_flag(l1b["quality_flag"][l1b["scan"] == i],
                                                                    "def_wind_flag")
                self.context.logger.info("Default wind speed {}".format(self.context.get_config_value("wind_default")))
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
                self.context.logger.info("Apply Ruddick et al., 2006")
                if wind[i] is not None:
                    rhof = rhof + 0.00039 * wind[i] + 0.000034 * wind[i] ** 2

            fresnel_coeff[i] = rhof

        l1b["rhof"].values = fresnel_coeff
        l1b["fresnel_vza"].values = fresnel_vza
        l1b["fresnel_raa"].values = fresnel_raa
        l1b["fresnel_sza"].values = fresnel_sza

        return l1b

    def get_epsilon(self, rhow_nosc, wavelength):

        # wavelength = l1b['wavelength'].values
        # get length of transposed rhow_nosc (1 epsilon per scan!)
        epsilon = np.zeros(len(rhow_nosc.T))
        failSimil = np.zeros(len(rhow_nosc.T))

        ## compute similarity epsilon
        for i in range(len(rhow_nosc.T)):
            ## compute similarity epsilon
            fail_simil, eps = self.qc_similarity(wavelength, rhow_nosc.T[i],
                                                 self.context.get_config_value("similarity_wr"),
                                                 self.context.get_config_value("similarity_wp"),
                                                 self.context.get_config_value("similarity_w1"),
                                                 self.context.get_config_value("similarity_w2"),
                                                 self.context.get_config_value("similarity_alpha"))

            ## R2005 quality control
            ## skip spectra not following similarity
            if self.context.get_config_value("similarity_test") == True:
                if fail_simil:
                    if self.context.get_config_value("verbosity") > 2: self.context.logger.info('Failed simil test.')
                    continue
                else:
                    if self.context.get_config_value("verbosity") > 2: self.context.logger.info('Passed simil test.')
            epsilon[i] = eps
            failSimil[i] = fail_simil
        return epsilon, failSimil

    def get_rhow_nosc(self, l1b):

        ## read mobley rho lut

        wavelength = l1b['wavelength'].values
        fresnel_coeff = l1b['rhof'].values
        rhow_nosc_all = np.zeros((len(l1b.scan), len(wavelength)))
        lw_all = np.zeros((len(l1b.scan), len(wavelength)))
        # rhow_all = np.zeros((len(l1b.scan), len(wavelength)))
        # epsilon = np.zeros(len(l1b.scan))
        simil_flag = np.zeros(len(l1b.scan))

        for i in range(len(l1b.scan)):
            ## compute rhow
            lu = l1b['upwelling_radiance'][:, i].values
            # should I average here or take the downwelling radiance per scan???
            # mls stands for mean sky/downwelling radiance, so need to check if mean is better than interpolated?
            mls = l1b['downwelling_radiance'][:, i].values
            # same for ed? Better interpolated or mean Ed???
            med = l1b['irradiance'][:, i].values

            lw_all[i] = [(lu[w] - (fresnel_coeff[i] * mls[w])) for w in range(len(wavelength))]
            rhow_nosc_all[i] = [np.pi * (lu[w] - (fresnel_coeff[i] * mls[w])) / med[w] for w in range(len(wavelength))]

        return rhow_nosc_all, lw_all

    ## QC a single rhow scan from PANTHYR
    ## according to R2005
    ##
    ## QV July 2018
    ## Last modifications: 2019-07-10 (QV) renamed from PANTR, integrated in rhymer

    def qc_similarity(self, wave, data, wr=670, wp=0.05, w1=720, w2=780, alpha=2.35, ssd=None):

        n = len(data)
        data_retained = []

        ## get pixel index for wavelength
        irefr, wrefr = self.rhymershared.closest_idx(wave, wr)
        iref1, wref1 = self.rhymershared.closest_idx(wave, w1)
        iref2, wref2 = self.rhymershared.closest_idx(wave, w2)

        ## get pixel index for similarity
        if alpha is None:
            if ssd is None: ssd = self.rhymerproc.similarity_read()
            id1, w1 = self.rhymershared.closest_idx(ssd['wave'], w1 / 1000.)
            id2, w2 = self.rhymershared.closest_idx(ssd['wave'], w2 / 1000.)
            alpha = ssd['ave'][id1] / ssd['ave'][id2]

        ## compute epsilon
        epsilon = (alpha * data[iref2] - data[iref1]) / (alpha - 1.0)

        if abs(epsilon) > wp * data[irefr]:
            return (1, epsilon)
        else:
            return (0, epsilon)

    def process_l1b(self, L1a_rad, L1a_irr):

        # QUALITY CHECK: TEMPORAL VARIABILITY IN ED AND LSKY -> ASSIGN FLAG
        L1a_rad = self.qc_scan(L1a_rad, measurandstring="radiance")
        L1a_irr = self.qc_scan(L1a_irr, measurandstring="irradiance")
        # QUALITY CHECK: MIN NBR OF SCANS -> ASSIGN FLAG
        L1a_uprad, L1a_downrad, L1a_irr = self.cycleparse(L1a_rad, L1a_irr)
        L1b_downrad = self.avg.average_l1b("radiance", L1a_downrad)
        L1b_irr = self.avg.average_l1b("irradiance", L1a_irr)
        # INTERPOLATE Lsky and Ed FOR EACH Lu SCAN! Threshold in time -> ASSIGN FLAG
        L1b = self.intp.interpolate_l1b_w(L1a_uprad, L1b_downrad, L1b_irr)
        if self.context.get_config_value("write_l1b") == True:
            self.writer.write(L1b, overwrite=True)
        return L1b

    def process_l1c(self, l1b):
        dataset_l1c = self.templ.l1c_from_l1b_dataset(l1b)

        dataset_l1c = self.get_wind(dataset_l1c)
        dataset_l1c = self.get_fresnelrefl(dataset_l1c)

        rhow_nosc_all, lw_all = self.get_rhow_nosc(dataset_l1c)

        # dataset_l1c['reflectance'].values = rhow_all.T

        dataset_l1c['reflectance_nosc'].values = rhow_nosc_all.T
        # dataset_l1c['epsilon'].values = epsilon
        dataset_l1c['water_leaving_radiance'].values = lw_all.T

        if self.context.get_config_value("write_l1c"):
            self.writer.write(dataset_l1c, overwrite=True)

        if self.context.get_config_value("plot_l1c"):
            self.plot.plot_scans_in_series("irradiance", dataset_l1c)

        return dataset_l1c


