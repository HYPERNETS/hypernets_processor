## def isodate_to_yday
## converts isodate (YYYY-MM-DDTHH:mm:ss) to day of year (fractional)
## written by Quinten Vanhellemont
## 2018-05-15
## modifications:

def isodate_to_yday(isodate):
    import dateutil.parser
    from datetime import datetime
    tm = dateutil.parser.parse(isodate)

    y = tm.year

    ## get day fraction
    hour = tm.hour + tm.minute / 60 + tm.second / 3600
    df = hour / 24.

    ## get year fraction
    ylen = ((datetime(y + 1, 1, 1) - datetime(y, 1, 1)).days)
    doy = float(tm.strftime('%j'))
    doy += df

    yf = doy / ylen

    return (tm, y, yf)
