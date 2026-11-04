import datetime
import numpy as np
from typing import Optional, Union, List, Any
from dateutil.parser import parse


def convert_datetime(
    date_time: Union[datetime.datetime, datetime.date, str, float, int, np.ndarray],
) -> datetime.datetime:
    """
    Convert input datetimes to a datetime object

    :param date_time: date time to convert to a datetime object
    :return: datetime object corresponding to input date_time
    """
    if isinstance(date_time, np.ndarray):
        return np.array([convert_datetime(date_time_i) for date_time_i in date_time])
    elif isinstance(date_time, datetime.datetime):
        return date_time
    elif isinstance(date_time, datetime.date):
        return datetime.datetime.combine(
            date_time, datetime.time(), tzinfo=datetime.timezone.utc
        )
    elif isinstance(date_time, np.datetime64):
        unix_epoch = np.datetime64(0, "s")
        one_second = np.timedelta64(1, "s")
        seconds_since_epoch = (date_time - unix_epoch) / one_second
        return datetime.datetime.fromtimestamp(
            seconds_since_epoch, datetime.timezone.utc
        )
    elif isinstance(date_time, (float, int, np.integer)):
        return datetime.datetime.fromtimestamp(date_time, datetime.timezone.utc)
    elif isinstance(date_time, str) and date_time.lower() == "present":
        return datetime.datetime.now(datetime.timezone.utc)
    else:
        if isinstance(date_time, str) and date_time[-1] == "Z":
            date_time = date_time[:-1]
        try:
            dt = parse(date_time, fuzzy=False)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return dt
        except ValueError:
            raise ValueError(
                "Unable to discern datetime requested: '{}' ({})".format(
                    date_time, type(date_time)
                )
            )
