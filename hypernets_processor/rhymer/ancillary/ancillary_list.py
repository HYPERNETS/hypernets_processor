## ancillary_list
## lists ancillary data from a given date from the ocean data server
##
## written by Quinten Vanhellemont, RBINS for the PONDER project
## 2017-10-17
## modifications:

def ancillary_list(date):
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
