import numpy as np
import hypernets_brdf_data_io as data_io
import os
import glob
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd

results_path = r"T:/ECO/EOServer/joe/hypernets_plots/polar_plots_JSIT/"

data_19 = pd.read_csv(
    r"T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/joe/prelim_cc19.csv"
)
data_0875 = pd.read_csv(
    r"T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/joe/prelim_cc0875.csv"
)
data_JSIT = pd.read_csv(
    r"T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/joe/JSIT_dates_times_raa.csv"
)

data_WWUKv3 = pd.read_csv(
    r"T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/WWUKv3_QC_good.csv"
)


def get_month(data):
    months = []
    for i in range(len(data)):
        month = str(data["date"][i])[4:6]
        months.append(month)
    new_data = data.assign(month=months)
    return new_data


data_19 = get_month(data_19)
data_0875 = get_month(data_0875)
data_JSIT = get_month(data_JSIT)
data_WWUKv3 = get_month(data_WWUKv3)


def plot_polar_reflectance(
    plotpath, vza, vaa, sza, saa, refl, wavelength, vmin=None, vmax=None, label=None
):
    raa_tol = 2.5
    vza_tol = 5

    vaa = vaa % 360
    saa = saa % 360
    raa = (saa - vaa + 360) % 360

    raa_grid = np.arange(0, 360, 5)
    vza_grid = np.array([0, 10, 20, 30, 40, 50, 60])

    vaa_mesh, vza_mesh = np.meshgrid(np.radians(raa_grid), vza_grid)

    refl_2d = np.zeros((len(raa_grid), len(vza_grid)))
    sza_list = []
    saa_list = []
    for i in range(len(raa_grid)):
        for j in range(len(vza_grid)):
            id_series = np.where(
                (np.abs(raa - raa_grid[i]) < raa_tol)
                & (np.abs(vza - vza_grid[j]) < vza_tol)
            )[0]
            if len(id_series) == 1:
                refl_2d[i, j] = refl[id_series]
                saa_list.append(saa[id_series][0])
                sza_list.append(sza[id_series][0])

            elif len(id_series) > 1:
                refl_2d[i, j] = np.mean(refl[id_series])
                saa_list.append(float(np.mean(saa[id_series])))
                sza_list.append(float(np.mean(sza[id_series])))

    saa_list = np.radians(saa_list)

    refl_2d[refl_2d == 0] = np.nan

    fig = plt.figure()
    ax = plt.subplot(1, 1, 1, projection="polar")
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi / 2.0)
    im = ax.pcolormesh(
        vaa_mesh,
        vza_mesh,
        refl_2d.T,
        shading="auto",
        cmap=plt.get_cmap("jet"),
        vmin=vmin,
        vmax=vmax,
    )
    # ax.scatter(saa_list, sza_list, color="black", marker="o")

    cbar = fig.colorbar(im)

    if label is None:
        cbar.set_label("reflectance at %s nm" % wavelength, rotation=270, labelpad=15)
    else:
        cbar.set_label(label, rotation=270, labelpad=15)

    fig.savefig(plotpath)
    plt.close(fig)


def plot_polar_reflectance_std(
    plotpath, vza, vaa, refl, wavelength, vmin=None, vmax=None, label=None
):
    vaa_tol = 2
    vza_tol = 2

    vaa = vaa % 360

    vaa_grid = np.arange(8, 368, 15)
    vza_grid = np.array([0, 5, 10, 20, 30, 40, 50, 60])

    vaa_mesh, vza_mesh = np.meshgrid(np.radians(vaa_grid), vza_grid)

    refl_2d = np.zeros((len(vaa_grid), len(vza_grid)))
    for i in range(len(vaa_grid)):
        for j in range(len(vza_grid)):
            id_series = np.where(
                (np.abs(vaa - vaa_grid[i]) < vaa_tol)
                & (np.abs(vza - vza_grid[j]) < vza_tol)
            )[0]
            if len(id_series) == 1:
                refl_2d[i, j] = refl[id_series]

            elif len(id_series) > 1:
                refl_2d[i, j] = np.std(refl[id_series])

    refl_2d[refl_2d == 0] = np.nan

    fig = plt.figure()
    ax = plt.subplot(1, 1, 1, projection="polar")
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi / 2.0)
    im = ax.pcolormesh(
        vaa_mesh,
        vza_mesh,
        refl_2d.T,
        shading="auto",
        cmap=plt.get_cmap("jet"),
        vmin=vmin,
        vmax=vmax,
    )

    cbar = fig.colorbar(im)

    if label is None:
        cbar.set_label("reflectance at %s nm" % wavelength, rotation=270, labelpad=15)
    else:
        cbar.set_label(label, rotation=270, labelpad=15)

    fig.savefig(plotpath)
    plt.close(fig)


def monthly_plotter(data, name):
    mon = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    tim = [
        530,
        600,
        630,
        700,
        730,
        800,
        830,
        900,
        930,
        1000,
        1030,
        1100,
        1130,
        1200,
        1230,
        1300,
        1330,
        1400,
        1430,
        1500,
        1530,
        1600,
        1630,
        1700,
        1730,
        1800,
    ]
    for i in range(len(mon)):
        data_monthly = data[data["month"] == mon[i]]

        if len(data_monthly) != 0:
            for j in range(len(tim) - 1):
                data_mon_time = data_monthly[
                    (data_monthly["time"] > tim[j])
                    & (data_monthly["time"] < tim[j + 1])
                ]

                if len(data_mon_time) != 0:
                    plot_polar_reflectance(
                        results_path + name + "_{}_{}_mean".format(mon[i], tim[j]),
                        data_mon_time[" vza"].values,
                        data_mon_time[" vaa"].values,
                        data_mon_time[" sza"].values,
                        data_mon_time[" saa"].values,
                        data_mon_time[" refl_550nm"].values,
                        550,
                    )
                    plot_polar_reflectance_std(
                        results_path + name + "_{}_{}_std".format(mon[i], tim[j]),
                        data_mon_time[" vza"].values,
                        data_mon_time[" vaa"].values,
                        data_mon_time[" refl_550nm"].values,
                        550,
                    )


# plot_polar_reflectance_std(results_path + 'test.png', data_subset[' vza'].values, data_subset[' vaa'].values, data_subset[' refl_550nm'].values, 550)
# monthly_plotter(data_19, '1_9')
# monthly_plotter(data_WWUKv3, 'WWUKv3')
aug = data_WWUKv3[data_WWUKv3["month"] == "08"]
sep = data_WWUKv3[data_WWUKv3["month"] == "09"]


def plot_month(data, plotname):
    plot_polar_reflectance(
        results_path + plotname,
        data[" vza"].values,
        data[" vaa"].values,
        data[" sza"].values,
        data[" saa"].values,
        data[" refl_550nm"].values,
        550,
    )


plot_month(aug, "WWUKv3_aug.png")
plot_month(sep, "WWUKv3_sep.png")
