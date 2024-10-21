import os.path
import numpy as np
from datetime import datetime, timedelta
import pandas as pd

def read_db_radcalnet_BOA(data_folder, db_folder, file, start_date, end_date):
    dbpath = os.path.join(db_folder, file)
    db = np.genfromtxt(dbpath, dtype=str)
    data = parse_radcalnet_dates(db)
    valid_ids = np.where(
        (data[:, 1] > start_date)
        & (data[:, 1] < end_date)
        & ([".input" in dat for dat in data[:, 0]])
    )[0]
    data = data[valid_ids, :]
    if len(data) == 0:
        raise ValueError(
            "no data found between the specified dates in the radcalnet database"
        )
    data_expanded = np.empty((len(data[:, 0]) * 13, 20), dtype=object)
    for i in range(len(data[:, 0])):
        data_expanded[i * 13 : (i + 1) * 13, 0] = data[i, 0]
        data_expanded[i * 13 : (i + 1) * 13, 1] = data[i, 1]
        (
            wav,
            times,
            refl,
            refl_uncs,
            doy_l,
            local_time,
            P,
            T,
            H2O,
            O3,
            AOD,
            ang,
            type,
            u_P,
            u_T,
            u_H2O,
            u_O3,
            u_AOD,
            u_ang,
        ) = read_file_radcalnet_BOA(os.path.join(data_folder, data[i, 0]))
        for ii in range(len(times)):
            time = datetime.strptime(times[ii], "%H:%M")
            data_expanded[i * 13 + ii, 1] += timedelta(
                hours=time.hour, minutes=time.minute
            )
            data_expanded[i * 13 + ii, 2] = wav
            data_expanded[i * 13 + ii, 3] = refl[:, ii]
            data_expanded[i * 13 + ii, 4] = refl_uncs[:, ii]
            data_expanded[i * 13 + ii, 5] = doy_l[ii]
            data_expanded[i * 13 + ii, 6] = local_time[ii]
            data_expanded[i * 13 + ii, 7] = P[ii]
            data_expanded[i * 13 + ii, 8] = T[ii]
            data_expanded[i * 13 + ii, 9] = H2O[ii]
            data_expanded[i * 13 + ii, 10] = O3[ii]
            data_expanded[i * 13 + ii, 11] = AOD[ii]
            data_expanded[i * 13 + ii, 12] = ang[ii]
            data_expanded[i * 13 + ii, 13] = type[ii]
            data_expanded[i * 13 + ii, 14] = u_P[ii]
            data_expanded[i * 13 + ii, 15] = u_T[ii]
            data_expanded[i * 13 + ii, 16] = u_H2O[ii]
            data_expanded[i * 13 + ii, 17] = u_O3[ii]
            data_expanded[i * 13 + ii, 18] = u_AOD[ii]
            data_expanded[i * 13 + ii, 19] = u_ang[ii]
    return data_expanded


def read_db_radcalnet_TOA(data_folder, file, start_date, end_date):
    dbpath = os.path.join(data_folder, file)
    db = np.genfromtxt(dbpath, dtype=str)
    data = parse_radcalnet_dates(db)
    valid_ids = np.where(
        (data[:, 1] > start_date)
        & (data[:, 1] < end_date)
        & ([".output" in dat for dat in data[:, 0]])
    )[0]
    data = data[valid_ids, :]
    if len(data) == 0:
        raise ValueError(
            "no data found between the specified dates in the radcalnet database"
        )
    data_expanded = np.empty((len(data[:, 0]) * 13, 13), dtype=object)
    for i in range(len(data[:, 0])):
        data_expanded[i * 13 : (i + 1) * 13, 0] = data[i, 0]
        data_expanded[i * 13 : (i + 1) * 13, 1] = data[i, 1]
        (
            wav,
            times,
            refl,
            refl_uncs,
            P,
            T,
            H2O,
            O3,
            AOD,
            u_P,
            u_T,
            u_H2O,
            u_O3,
            u_AOD,
        ) = read_file_radcalnet_TOA(os.path.join(data_folder, data[i, 0]))
        for ii in range(len(times)):
            time = datetime.strptime(times[ii], "%H:%M")
            data_expanded[i * 13 + ii, 1] += timedelta(
                hours=time.hour, minutes=time.minute
            )
            data_expanded[i * 13 + ii, 2] = wav
            data_expanded[i * 13 + ii, 3] = refl[:, ii]
            data_expanded[i * 13 + ii, 4] = refl_uncs[:, ii]
            data_expanded[i * 13 + ii, 5] = P[ii]
            data_expanded[i * 13 + ii, 6] = H2O[ii]
            data_expanded[i * 13 + ii, 7] = O3[ii]
            data_expanded[i * 13 + ii, 8] = AOD[ii]
            data_expanded[i * 13 + ii, 9] = u_P[ii]
            data_expanded[i * 13 + ii, 10] = u_H2O[ii]
            data_expanded[i * 13 + ii, 11] = u_O3[ii]
            data_expanded[i * 13 + ii, 12] = u_AOD[ii]
    return data_expanded


def read_file_radcalnet_BOA(filepath):
    data2 = np.genfromtxt(filepath, dtype="str", delimiter="\t", skip_header=4)
    wav = data2[12:223, 0].astype(float)
    times = data2[2, 1:]
    refl = data2[12:223, 1:].astype(float)
    refl_uncs = data2[229:440, 1:].astype(float)
    doy_l = data2[3, 1:].astype(float)
    local_time = data2[4, 1:]
    P = data2[5, 1:].astype(float)
    T = data2[6, 1:].astype(float)
    H2O = data2[7, 1:].astype(float)
    O3 = data2[8, 1:].astype(float)
    AOD = data2[9, 1:].astype(float)
    ang = data2[10, 1:].astype(float)
    type = data2[11, 1:]
    u_P = data2[223, 1:].astype(float)
    u_T = data2[224, 1:].astype(float)
    u_H2O = data2[225, 1:].astype(float)
    u_O3 = data2[226, 1:].astype(float)
    u_AOD = data2[227, 1:].astype(float)
    u_ang = data2[228, 1:].astype(float)
    refl[refl == 9999] = np.nan
    refl_uncs[refl_uncs == 9999] = np.nan
    u_P[P == 9999] = np.nan
    u_T[T == 9999] = np.nan
    u_H2O[H2O == 9999] = np.nan
    u_O3[O3 == 9999] = np.nan
    u_AOD[AOD == 9999] = np.nan
    u_ang[ang == 9999] = np.nan
    P[P == 9999] = np.nan
    T[T == 9999] = np.nan
    H2O[H2O == 9999] = np.nan
    O3[O3 == 9999] = np.nan
    AOD[AOD == 9999] = np.nan
    ang[ang == 9999] = np.nan

    return wav, times, refl, refl_uncs, doy_l, local_time, P, T, H2O, O3, AOD, ang, type, u_P, u_T, u_H2O, u_O3, u_AOD, u_ang


def read_file_radcalnet_TOA(filepath):
    data2 = np.genfromtxt(filepath, dtype="str", delimiter="\t", skip_header=4)
    wav = data2[15:226, 0].astype(float)
    times = data2[2, 1:]
    refl = data2[15:226, 1:].astype(float)
    refl_uncs = data2[232:443, 1:].astype(float)
    P = data2[5, 1:].astype(float)
    T = data2[6, 1:].astype(float)
    H2O = data2[7, 1:].astype(float)
    O3 = data2[8, 1:].astype(float)
    AOD = data2[9, 1:].astype(float)
    u_P = data2[226, 1:].astype(float)
    u_T = data2[227, 1:].astype(float)
    u_H2O = data2[228, 1:].astype(float)
    u_O3 = data2[229, 1:].astype(float)
    u_AOD = data2[230, 1:].astype(float)
    refl[refl == 9999] = np.nan
    refl_uncs[refl_uncs == 9999] = np.nan
    P[P == 9999] = np.nan
    T[T == 9999] = np.nan
    H2O[H2O == 9999] = np.nan
    O3[O3 == 9999] = np.nan
    AOD[AOD == 9999] = np.nan
    u_P[P == 9999] = np.nan
    u_T[T == 9999] = np.nan
    u_H2O[H2O == 9999] = np.nan
    u_O3[O3 == 9999] = np.nan
    u_AOD[AOD == 9999] = np.nan
    return wav, times, refl, refl_uncs, P, T, H2O, O3, AOD, u_P, u_T, u_H2O, u_O3, u_AOD


def parse_radcalnet_dates(db):
    dates = np.empty((len(db), 2), dtype=object)
    dates[:, 0] = db
    for i, file in enumerate(db):
        dates[i, 1] = parse_date(file)
    return dates


def parse_date(filename):
    date_string = filename[7:15]
    date = datetime.strptime(date_string, "%Y_%j")
    return date
