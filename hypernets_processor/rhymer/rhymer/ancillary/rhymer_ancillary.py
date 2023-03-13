import os
from hypernets_processor.rhymer.rhymer.shared.rhymer_shared import RhymerShared


class RhymerAncillary:

    ### get wind speed data for isodate, lon and lat location
    ## ftime is the fractional UTC time - assumed to be midday 12 UTC if not given
    ## 18:14:33 would be ftime = 0.7601 = (18 + 14/60 + 33/3600)/24
    ## QV 2019-07-03
    ## Last modifications:    QV 2019-07-10 changed isotime parsing to be more flexible
    def __init__(self, context):
        self.context = context


    def get_wind(self, isodate, lon, lat, isotime=None, ftime=12):

        if isotime is not None:
            # h,m,s = (float(v) for v in isotime.split(':'))
            # ftime = (h + m/60 + s/3600)/24
            ts = (float(v) for v in isotime.split(':'))
            ftime = 0
            for i, t in enumerate(ts):
                ftime += t / (60 ** i)
        print('isodate:{}, lat:{}, lon:{}'.format(isodate, lat, lon))
        anc = self.ancillary_get(isodate, lon, lat, ftime=ftime)

        if ('z_wind' in anc) and ('m_wind' in anc):
            u = anc['z_wind']['interp']
            v = anc['m_wind']['interp']
            wind = (u ** 2 + v ** 2) ** 0.5
            return (wind)
        else:
            return (None)


    ## ancillary_get
    ## downloads and interpolates ancillary data from the ocean data server
    ##
    ## written by Quinten Vanhellemont, RBINS for the PONDER project
    ## 2017-10-18
    ## modifications: 2017-10-24 (QV) added kind keyword
    ##                2017-12-05 (QV) added test if data is missing
    ##                2018-07-18 (QV) changed acolite import name
    ##                2018-11-19 (QV) added verbosity option
    ##                2019-07-03 (QV) modified for rhymer, ozone data removed

    def ancillary_get(self, date, lon, lat, ftime=12.0, local_dir=None, quiet=True, kind='linear', verbosity=0):
        if local_dir == None: local_dir = self.context.get_config_value('met_dir')

        ## list and download files
        anc_files = self.ancillary_list(date)
        anc_local = self.ancillary_download(ancillary_files=anc_files, local_dir=local_dir, verbosity=verbosity)

        ## get ncep MET files
        ncep_files = [anc_local[i] for i, j in enumerate(anc_local) if "NCEPR2" in j]
        anc = {'date': date, 'lon': lon, 'lat': lat, 'ftime': ftime}

        ## interpolate MET
        if len(ncep_files) == 0:
            print('No NCEP files found for {}'.format(date))
        else:
            anc_met = self.ancillary_interp_met(ncep_files, lon, lat, ftime, kind=kind)
            for k in anc_met.keys(): anc[k] = anc_met[k]

        return (anc)


    ## ancillary_list
    ## lists ancillary data from a given date from the ocean data server
    ##
    ## written by Quinten Vanhellemont, RBINS for the PONDER project
    ## 2017-10-17
    ## modifications:

    def ancillary_list(self, date):
        from datetime import datetime, timedelta

        year, month, day = [int(i) for i in date.split('-')]
        dtime = datetime(year, month, day)

        isodate = dtime.strftime("%Y-%m-%d")
        year = dtime.strftime("%Y")
        jday = dtime.strftime("%j").zfill(3)
        yjd = "{}{}".format(dtime.strftime("%Y"), jday)

        dtime_next = dtime + timedelta(days=1)
        year_next = dtime_next.strftime("%Y")
        jday_next = dtime_next.strftime("%j").zfill(3)
        yjd_next = "{}{}".format(year_next, jday_next)

        file_types = ['MET_NCEPR2_6h', 'MET_NCEPR2_6h_NEXT']

        basefiles = []
        for file_type in file_types:
            if file_type == "MET_NCEPR2_6h":
                cfile = ["N{}{}_MET_NCEPR2_6h.hdf.bz2".format(yjd, h) for h in ['00', '06', '12', '18']]
                for f in cfile: basefiles.append(f)
            elif file_type == "MET_NCEPR2_6h_NEXT":
                cfile = "N{}00_MET_NCEPR2_6h.hdf.bz2".format(yjd_next)
                basefiles.append(cfile)
            else:
                continue
        return (basefiles)

    ## ancillary_download
    ## gets ancillary data from the ocean data server
    ##
    ## written by Quinten Vanhellemont, RBINS for the PONDER project
    ## 2017-10-17
    ## modifications:
    ##                2018-07-18 (QV) changed acolite import name
    ##                2018-11-19 (QV) added verbosity option, fixed the download_file script for the GUI
    ##                2019-07-03 (QV) adapted for rhymer

    def ancillary_download(self, date=None, ancillary_files=None, time=None,
                           file_types=['TOAST', 'O3_AURAOMI_24h', 'MET_NCEP_6h', 'MET_NCEP_NEXT'],
                           local_dir="/storage/Data/MET", download=True, override=False, verbosity=0,
                           get_url="https://oceandata.sci.gsfc.nasa.gov/cgi/getfile"):


        local_files = []
        for basefile in ancillary_files:
            yjd = basefile[1:8]
            year = yjd[0:4]
            jday = yjd[4:7]

            url_file = '{}/{}'.format(get_url, basefile)
            local_file = '{}/{}/{}/{}'.format(local_dir, year, jday, basefile)

            if download:
                ## download file
                if os.path.exists(local_file) & (not override):
                    if verbosity > 1: print('File {} exists'.format(basefile))
                    local_files.append(local_file)
                else:
                    if os.path.exists(os.path.dirname(local_file)) is False:
                        os.makedirs(os.path.dirname(local_file))

                    if verbosity > 0: print('Downloading file {}'.format(basefile))

                    try:
                        # urllib.request.urlretrieve(url_file, local_file)
                        RhymerShared(self).download_file(url_file, local_file)
                        if verbosity > 0: print('Finished downloading file {}'.format(basefile))
                        local_files.append(local_file)
                    except:
                        print('Downloading file {} failed'.format(basefile))
        return (local_files)

    ## ancillary_interp_met
    ## interpolates NCEP MET data from 6 hourly files to given lon, lat and time (float)
    ##
    ## written by Quinten Vanhellemont, RBINS for the PONDER project
    ## 2017-10-17
    ## modifications: 2017-10-18 (QV) fixed latitude indexing
    ##                           (QV) added bz2 support
    ##                2017-10-24 (QV) added option to use nearest neighbour (kind from scipy= ‘linear’, ‘cubic’, ‘quintic’)
    ##                2018-03-05 (QV) fixed end of year rollover
    ##                2018-03-12 (QV) added file closing to enable file deletion for Windows

    def ancillary_interp_met(self, files, lon, lat, time, datasets=['z_wind', 'm_wind', 'press', 'rel_hum', 'p_water'],
                             kind='linear'):
        print("pyhdf")
        import os, bz2
        from pyhdf.SD import SD, SDC
        from numpy import linspace
        from scipy import interpolate

        interp_data = {ds: [] for ds in datasets}
        ftimes = []
        jdates = []
        for file in files:
            zipped = False
            # uncompress bz2 files
            if file[-4:len(file)] == '.bz2':
                try:
                    zipped = True
                    file = file.strip('.bz2')
                    file_zipped = file + '.bz2'
                    with bz2.open(file_zipped, 'rb') as f:
                        data = f.read()
                    with open(file, 'wb') as f:
                        f.write(data)
                except:
                    print("Error extracting file {}, probably incomplete download".format(file_zipped))

            f = SD(file, SDC.READ)
            datasets_dic = f.datasets()
            meta = f.attributes()

            if zipped is False:
                print(meta)
                for idx, sds in enumerate(datasets_dic.keys()): print(idx, sds)

            ftime = meta['Start Millisec'] / 3600000.
            ftimes.append(ftime)
            jdates.append(meta['Start Day'])

            ## make lons and lats for this file
            lons = linspace(meta["Westernmost Longitude"], meta["Easternmost Longitude"],
                            num=meta['Number of Columns'])
            lats = linspace(meta["Northernmost Latitude"], meta["Southernmost Latitude"],
                            num=meta['Number of Rows'])

            for dataset in datasets:
                sds_obj = f.select(dataset)
                data = sds_obj.get()
                ## do interpolation in space
                if kind == 'nearest':
                    xi, xret = min(enumerate(lons), key=lambda x: abs(x[1] - float(lon)))
                    yi, yret = min(enumerate(lats), key=lambda x: abs(x[1] - float(lat)))
                    interp_data[dataset].append(data[yi, xi])
                else:
                    interp = interpolate.interp2d(lons, lats, data, kind=kind)
                    idata = interp(lon, lat)
                    interp_data[dataset].append(idata[0])
                ## add QC?

            f.end()
            f = None

            ### delete unzipped file
            # if (zipped) & (sys.platform[0:3].lower() != 'win'): os.remove(file)
            if (zipped): os.remove(file)
        # f = None

        ## add check for year for files[-1]?
        if (ftimes[-1] == 0.) & \
                ((jdates[-1] == jdates[0] + 1) | (jdates[0] >= 365 & jdates[-1] == 1)): ftimes[-1] = 24.0

        ## do interpolation in time
        anc_data = {}
        for dataset in datasets:
            tinp = interpolate.interp1d(ftimes, interp_data[dataset])
            ti = tinp(time)
            anc_data[dataset] = {"interp": ti, "series": interp_data[dataset]}

        return (anc_data)
