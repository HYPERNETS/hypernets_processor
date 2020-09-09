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

def ancillary_get(date, lon, lat, ftime=12.0, local_dir=None, quiet=True, kind='linear', verbosity=0):
    import rhymer as ry
    if local_dir == None: local_dir = ry.config['met_dir']

    ## list and download files
    anc_files = ry.ancillary.ancillary_list(date)
    anc_local = ry.ancillary.ancillary_download(ancillary_files=anc_files, local_dir=local_dir, verbosity=verbosity)

    ## get ncep MET files
    ncep_files = [anc_local[i] for i, j in enumerate(anc_local) if "NCEPR2" in j]
    anc = {'date': date, 'lon': lon, 'lat': lat, 'ftime': ftime}

    ## interpolate MET
    if len(ncep_files) == 0:
        print('No NCEP files found for {}'.format(date))
    else:
        anc_met = ry.ancillary.ancillary_interp_met(ncep_files, lon, lat, ftime, kind=kind)
        for k in anc_met.keys(): anc[k] = anc_met[k]

    return (anc)
