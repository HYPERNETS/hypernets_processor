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
from hypernets_processor.data_io.hypernets_ds_builder import HypernetsDSBuilder
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
import numpy as np
import math
from hypernets_processor.data_io.hypernets_reader import read_hypernets_data


class RhymerHypstar:

    def __init__(self, context):
        self.hdsb = HypernetsDSBuilder(context=context)
        self.writer = HypernetsWriter(context)
        self.context = context
        self.wind_ancillary = None
        self.wind_default = 2
        self.fresnel_option = 'Mobley'
        self.rhymer_data_dir="/home/cgoyens/OneDrive/BackUpThinkpadClem/Projects/HYPERNETS/NetworkDesign_D52" \
                             "/DataProcChain/hypernets_processor/hypernets_processor/rhymer/data"
        ## compute similarity epsilon
        self.similarity_test = False
        self.similarity_correct = True
        self.similarity_wr = 670
        self.similarity_wp = 0.05
        self.similarity_w1 = 720
        self.similarity_w2 = 780
        self.similarity_alpha = 2.35

    def qc_scan(self, dataset, measurandstring, diff_wave=550, diff_threshold=0.25, verbosity=0):
        ## no inclination
        ## difference at 550 nm < 25% with neighbours
        ##
        ## QV July 2018
        ## Last modifications: 2019-07-10 (QV) renamed from PANTR, integrated in rhymer
        # Modified 10/09/2020 by CG for the PANTHYR

        series_id = np.unique(dataset['series_id'])
        wave = dataset['wavelength'].values
        rs = RhymerShared()

        for i in series_id:

            scans = dataset['scan'][dataset['series_id'] == i]

            ##
            n = len(scans)
            ## get pixel index for wavelength
            iref, wref = rs.closest_idx(wave, diff_wave)

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
                if v > diff_threshold:
                    # set quality flag to 10
                    dataset['quality_flag'][scans[i]] = 10
                    seq = dataset.attrs["sequence_id"]
                    ts = datetime.utcfromtimestamp(dataset['quality_flag'][scans[i]])

                    if verbosity > 2: print('Temporal jump: in {}:  Aquisition time {}, {}'.format(seq, ts, ', '.join(
                        ['{}:{}'.format(k, dataset[k][scans[i]].values) for k in ['scan', 'quality_flag']])))

                ## check for complete spectra
                ## assumed here they are masked by inf or nan by calibration step
                if any([not np.isfinite(j) for j in data[i]]):
                    # set quality flag to 10
                    dataset['quality_flag'][scans[i]] = 10
                    ts = datetime.utcfromtimestamp(dataset['acquisition_time'].values)
                    if verbosity > 2: print('inf or Nan data in: Aquisition time {}, {}'.format(ts, ', '.join(
                        ['{}:{}'.format(k, dataset[k][scans[i]].values) for k in ['scan', 'quality_flag']])))

            return dataset

    def read_protocol(self, settings_file):
        defset = ConfigParser()
        defset.read(settings_file)
        protocol = dict(defset['MEASPROTOCOL'])['protocol']
        valheader = dict(defset['MEASPROTOCOL'])['valheader']
        valheader = valheader.split(',')
        nbrlu = dict(defset['MEASPROTOCOL'])['nbrlu']
        nbrlsky = dict(defset['MEASPROTOCOL'])['nbrlsky']
        nbred = dict(defset['MEASPROTOCOL'])['nbred']
        return protocol, valheader, nbrlu, nbrlsky, nbred

    def cycleparse(self, rad, irr, settings_file=None, verbosity=0):

        # # check which cycle we have and see if we have the required cycle
        # if settings_file is None:
        #     settings_file = "~/OneDrive/BackUpThinkpadClem/Projects/HYPERNETS/NetworkDesign_D52/DataProcChain/hypernets_processor/data/default.txt"
        # print(settings_file)        #
        # protocol, valheader, nbrlu, nbrlsky, nbred = self.read_protocol(settings_file)
        nbrlu, nbrlsky, nbred = 6, 6, 6
        protocol = 'water_std'

        if protocol != 'water_std':
            # here we should simply provide surface reflectance?
            # what about a non-standard protocol but that includes the required standard series?
            print('Unknown measurement protocol: {}'.format(protocol))
        else:
            uprad = []
            downrad = []
            for i in rad['scan']:
                scani = rad.sel(scan=i)
                sena = scani["viewing_azimuth_angle"].values
                senz = scani["viewing_zenith_angle"].values
                ts = datetime.utcfromtimestamp(scani['acquisition_time'].values)
                # not fromtimestamp?

                if (senz != 'NULL') & (sena != 'NULL'):
                    senz = float(senz)
                    sena = abs(float(sena))
                else:
                    if verbosity > 2: print('NULL angles: Aquisition time {}, {}'.format(ts, ', '.join(
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
                    lu["quality_flag"][lu["viewing_azimuth_angle"] == i] = 10
                    if verbosity > 2:
                        ts = [datetime.utcfromtimestamp(x) for x in
                              lu['acquisition_time'][lu["viewing_azimuth_angle"] == i].values]
                        print('No azimuthal equivalent downwelling radiance measurement: Aquisition time {}, {}'.format(
                            ts, ', '.join(
                                ['{}:{}'.format(k, lu[k][lu["viewing_azimuth_angle"] == i].values) for k in
                                 ['scan', 'quality_flag']])))

            # check if we have the required fresnel angle for lsky
            senz_lu = np.unique(lu["viewing_zenith_angle"].values)
            senz_lsky = 180 - np.unique(lsky["viewing_zenith_angle"].values)
            for i in senz_lu:
                if i not in senz_lsky:
                    lu["quality_flag"][lu["viewing_zenith_angle"] == i] = 10
                    if verbosity > 2:
                        ts = [datetime.utcfromtimestamp(x) for x in
                              lu['acquisition_time'][lu["viewing_zenith_angle"] == i].values]
                        print(
                            'No downwelling radiance measurement at appropriate fresnel angle: Aquisition time {}, {}'.format(
                                ts, ', '.join(
                                    ['{}:{}'.format(k, lu[k][lu["viewing_azimuth_angle"] == i].values) for k
                                     in ['scan', 'quality_flag']])))

            # check if correct number of radiance and irradiance data
            if lu.scan[lu['quality_flag'] <= 1].count() < nbrlu:
                if verbosity > 2:
                    print("No enough upwelling radiance data for sequence {}".format(lu.attrs['sequence_id']))
            if lsky.scan[lsky['quality_flag'] <= 1].count() < nbrlsky:
                if verbosity > 2:
                    print("No enough downwelling radiance data for sequence {}".format(lsky.attrs['sequence_id']))

            if irr.scan[irr['quality_flag'] <= 1].count() < nbred:
                if verbosity > 2:
                    print("No enough irradiance data for sequence {}".format(irr.attrs['sequence_id']))

        return lu, lsky, irr

    def retrieve_wind(self, l1c):

        lat = l1c.attrs['site_latitude']
        lon = l1c.attrs['site_latitude']
        wind = []
        for i in range(len(l1c.scan)):
            if self.wind_ancillary is not None:
                isodate = datetime.utcfromtimestamp(l1c['acquisition_time'][i].values).strftime('%Y-%m-%d')
                isotime = datetime.utcfromtimestamp(l1c['acquisition_time'][i].values).strftime('%H:%M:%S')
                anc_wind = ry.ancillary.get_wind(isodate, lon, lat, isotime=isotime)
                if anc_wind is not None:
                    wind.append(anc_wind)
            else:
                wind.append(self.wind_default)
        return wind


    def fresnelrefl_qc_simil(self, l1c, wind):

        ## read mobley rho lut
        rholut = RhymerProcessing.mobley_lut_read(self)

        wavelength=l1c['wavelength'].values

        fresnel_coeff = np.zeros(len(l1c.scan))
        rhow_nosc_all= np.zeros((len(l1c.scan), len(wavelength)))
        lw_all= np.zeros((len(l1c.scan), len(wavelength)))
        rhow_all=np.zeros((len(l1c.scan), len(wavelength)))
        epsilon= np.zeros(len(l1c.scan))

        for i in range(len(l1c.scan)):
            vza=l1c['viewing_zenith_angle'][i].values
            sza = l1c['solar_zenith_angle'][i].values

            diffa=l1c['viewing_azimuth_angle'][i].values-l1c['viewing_azimuth_angle'][i].values

            if diffa >= 360:
                diffa = diffa - 360
            elif 0 <= diffa < 360:
                diffa = diffa
            else:
                diffa = diffa + 360
            raa = abs((diffa - 180))
            sza=l1c['solar_zenith_angle'][i].values
            ## get fresnel reflectance
            if self.fresnel_option == 'Mobley':
                if (sza is not None) & (raa is not None):
                    sza_ = min(sza, 79.999)
                    rhof = RhymerProcessing().mobley_lut_interp(sza, vza, raa,
                                                           wind=wind[i],
                                                           rholut=rholut)
                else:
                    # add a quality flag!
                    fresnel = 'fixed'

            if self.fresnel_option == 'Ruddick2006':
                rhof = self.rhof_default
                ## R2006
                if wind is not None:
                    rhof = rhof + 0.00039 * wind + 0.000034 * wind ** 2
            ## compute rhow
            lu=l1c['upwelling_radiance'][:,i].values
            # should I average here or take the downwelling radiance per scan???
            # mls stands for mean sky/downwelling radiance, so need to check if mean is better than interpolated?
            mls=l1c['downwelling_radiance'][:,i].values
            # same for ed? Better interpolated or mean Ed???
            med=l1c['irradiance'][:,i].values

            lw_all[i]=[(lu[w] - (rhof * mls[w])) for w in range(len(wavelength))]
            rhow_nosc_all[i]=[np.pi * (lu[w] - (rhof * mls[w])) / med[w] for w in range(len(wavelength))]
            fresnel_coeff[i]=rhof

            ## compute similarity epsilon
            print(self.similarity_alpha)
            fail_simil, eps = self.qc_similarity(wavelength, rhow_nosc_all[i],
                                                                   self.similarity_wr,
                                                                   self.similarity_wp,
                                                                   self.similarity_w1,
                                                                   self.similarity_w2,
                                                                   self.similarity_alpha)

            ## R2005 quality control
            ## skip spectra not following similarity
            if self.similarity_test:
                if fail_simil:
                    if verbosity > 2: print('Failed simil test.')
                    continue
                else:
                    if verbosity > 2: print('Passed simil test.')

            ## R2005 correction
            if self.similarity_correct:
                # print(epsilon)
                rhow_all[i] = [r - eps for r in rhow_nosc_all[i]]
            else:
                rhow_all[i] = rhow_nosc_all[i]

            epsilon[i]=eps


        return lw_all, rhow_all, rhow_nosc_all, epsilon, fresnel_coeff

    ## QC a single rhow scan from PANTHYR
    ## according to R2005
    ##
    ## QV July 2018
    ## Last modifications: 2019-07-10 (QV) renamed from PANTR, integrated in rhymer

    def qc_similarity(self, wave, data, wr=670, wp=0.05, w1=720, w2=780, alpha=2.35, ssd=None):

        n = len(data)
        data_retained = []

        ## get pixel index for wavelength
        irefr, wrefr = RhymerShared().closest_idx(wave, wr)
        iref1, wref1 = RhymerShared().closest_idx(wave, w1)
        iref2, wref2 = RhymerShared().closest_idx(wave, w2)

        ## get pixel index for similarity
        if alpha is None:
            if ssd is None: ssd = RhymerProcessing.similarity_read()
            id1, w1 = RhymerShared().closest_idx(ssd['wave'], w1 / 1000.)
            id2, w2 = RhymerShared().closest_idx(ssd['wave'], w2 / 1000.)
            alpha = ssd['ave'][id1] / ssd['ave'][id2]

        ## compute epsilon
        epsilon = (alpha * data[iref2] - data[iref1]) / (alpha - 1.0)

        if abs(epsilon) > wp * data[irefr]:
            return (True, epsilon)
        else:
            return (False, epsilon)