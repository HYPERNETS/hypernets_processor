class RhymerAncillary:

    ### get wind speed data for isodate, lon and lat location
    ## ftime is the fractional UTC time - assumed to be midday 12 UTC if not given
    ## 18:14:33 would be ftime = 0.7601 = (18 + 14/60 + 33/3600)/24
    ## QV 2019-07-03
    ## Last modifications:    QV 2019-07-10 changed isotime parsing to be more flexible

    def get_wind(isodate, lon, lat, isotime=None, ftime=12):
        import rhymer as ry

        if isotime is not None:
            # h,m,s = (float(v) for v in isotime.split(':'))
            # ftime = (h + m/60 + s/3600)/24
            ts = (float(v) for v in isotime.split(':'))
            ftime = 0
            for i, t in enumerate(ts):
                ftime += t / (60 ** i)

        anc = ry.ancillary.ancillary_get(isodate, lon, lat, ftime=ftime)

        if ('z_wind' in anc) and ('m_wind' in anc):
            u = anc['z_wind']['interp']
            v = anc['m_wind']['interp']
            wind = (u ** 2 + v ** 2) ** 0.5
            return (wind)
        else:
            return (None)
