import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from scipy.stats import chisquare, goodness_of_fit

results_path = r"T:/ECO/EOServer/joe/hypernets_plots/plane_models/"

# read and bin data
data_19 = pd.read_csv(
    r"T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/joe/GHNA_2022_plane_definition.csv"
)
data_0875 = pd.read_csv(
    r"T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/joe/prelim_cc0875.csv"
)
data_unmasked = pd.read_csv(
    r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\joe\GHNA_2022_prelim_and_raa10.csv"
)


def raa_binning(data, raa_limits):

    if raa_limits[1] > raa_limits[0]:
        new_data = data[(data["raa"] > raa_limits[0]) & (data["raa"] < raa_limits[1])]
        new_data = new_data.reset_index(drop=True)
        return new_data

    if raa_limits[1] < raa_limits[0]:
        new_data = data[(data["raa"] > raa_limits[0]) | (data["raa"] < raa_limits[1])]
        new_data = new_data.reset_index(drop=True)
        return new_data


data_19_30_90 = raa_binning(data_19, (30, 90))
data_19_90_150 = raa_binning(data_19, (90, 150))
data_19_150_210 = raa_binning(data_19, (150, 210))
data_19_210_270 = raa_binning(data_19, (210, 270))
data_19_270_330 = raa_binning(data_19, (270, 330))
data_19_330_30 = raa_binning(data_19, (330, 30))

data_19_list = [
    data_19_30_90,
    data_19_90_150,
    data_19_150_210,
    data_19_210_270,
    data_19_270_330,
    data_19_330_30,
]

data_0875_30_90 = raa_binning(data_0875, (30, 90))
data_0875_90_150 = raa_binning(data_0875, (90, 150))
data_0875_150_210 = raa_binning(data_0875, (150, 210))
data_0875_210_270 = raa_binning(data_0875, (210, 270))
data_0875_270_330 = raa_binning(data_0875, (270, 330))
data_0875_330_30 = raa_binning(data_0875, (330, 30))

data_0875_list = [
    data_0875_30_90,
    data_0875_90_150,
    data_0875_150_210,
    data_0875_210_270,
    data_0875_270_330,
    data_0875_330_30,
]

data_unmasked_30_90 = raa_binning(data_unmasked, (30, 90))
data_unmasked_90_150 = raa_binning(data_unmasked, (90, 150))
data_unmasked_150_210 = raa_binning(data_unmasked, (150, 210))
data_unmasked_210_270 = raa_binning(data_unmasked, (210, 270))
data_unmasked_270_330 = raa_binning(data_unmasked, (270, 330))
data_unmasked_330_30 = raa_binning(data_unmasked, (330, 30))

data_unmasked_list = [
    data_unmasked_30_90,
    data_unmasked_90_150,
    data_unmasked_150_210,
    data_unmasked_210_270,
    data_unmasked_270_330,
    data_unmasked_330_30,
]

# define plane surface model


def quad_plane(xy, a, b, c, d, e, f):
    x, y = xy
    return a + b * x + c * y + d * x**2 + e * y**2 + f * x * y


def lin_plane(xy, a, b, c):
    x, y = xy
    return a + b * x + c * y


# curve fit
def plane_fit_and_plot(data, data_setting, title, stds, plot=False):
    x = data[" sza"].values
    y = data[" vza"].values
    z = data[" refl_550nm"].values

    popt, pcov = curve_fit(quad_plane, (x, y), z)
    below = popt - stds * np.sqrt(np.diag(pcov))
    above = popt + stds * np.sqrt(np.diag(pcov))

    z_below = (
        quad_plane((data_setting[" sza"].values, data_setting[" vza"].values), *below)
        - data_setting[" refl_550nm"].values * 0.05
    )
    z_above = (
        quad_plane((data_setting[" sza"].values, data_setting[" vza"].values), *above)
        + data_setting[" refl_550nm"].values * 0.05
    )

    if plot is True:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        ax.scatter(
            data_setting[" sza"].values,
            data_setting[" vza"].values,
            data_setting[" refl_550nm"].values,
        )

        x_range = np.linspace(0, 90, 1000)
        y_range = np.linspace(0, 90, 1000)

        X, Y = np.meshgrid(x_range, y_range)
        Z = quad_plane((X, Y), *popt)
        Z_below = quad_plane((X, Y), *below) - 0.05 * Z
        Z_above = quad_plane((X, Y), *above) + 0.05 * Z

        ax.plot_surface(X, Y, Z, alpha=0.5)
        ax.plot_surface(X, Y, Z_above, alpha=0.5)
        ax.plot_surface(X, Y, Z_below, alpha=0.5)

        ax.set_xlabel("SZA")
        ax.set_ylabel("VZA")
        ax.set_zlabel("Reflectance")
        # fig.savefig(results_path + title)
        plt.show()

        fig, axs = plt.subplots(1, 3, figsize=(6, 4), sharey=True)
        for i in range(3):
            axs[i].plot(Y, quad_plane(((i + 1) * 20, Y), *popt), color="blue")
            axs[i].plot(
                Y, quad_plane(((i + 1) * 20, Y), *below) - 0.1 * Z, color="green"
            )
            axs[i].plot(
                Y, quad_plane(((i + 1) * 20, Y), *above) + 0.1 * Z, color="orange"
            )
            axs[i].set_title(f"SZA = {(i+1)*20}")
            axs[i].scatter(
                data_setting[
                    data_setting[" sza"].between((i + 1) * 20 - 1, (i + 1) * 20 + 1)
                ][" vza"].values,
                data_setting[
                    data_setting[" sza"].between((i + 1) * 20 - 1, (i + 1) * 20 + 1)
                ][" refl_550nm"].values,
                color="black",
                s=5,
            )
            axs[i].set_xlabel("VZA")
            axs[0].set_ylabel("Reflectance")
            fig.suptitle("RAA (270,330)")
            # fig.savefig(results_path + 'sza_slices_tol01_270_330.png')
        plt.show()

    outliers = data_setting[
        (data_setting[" refl_550nm"] > z_above)
        | (data_setting[" refl_550nm"] < z_below)
    ]
    good_data = data_setting[
        (data_setting[" refl_550nm"] < z_above)
        & (data_setting[" refl_550nm"] > z_below)
    ]
    good_data.reset_index(drop=True, inplace=True)
    outliers.reset_index(drop=True, inplace=True)

    return outliers, good_data


# redefine outliers using planes
outs_19, good_19 = plane_fit_and_plot(
    data_19_list[0], data_unmasked_list[0], "", 3, plot=False
)
for i in range(len(data_19_list) - 1):
    outs_19 = pd.concat(
        [
            outs_19,
            plane_fit_and_plot(
                data_19_list[i + 1], data_unmasked_list[i + 1], "", 3, plot=False
            )[0],
        ],
        ignore_index=True,
    )
    good_19 = pd.concat(
        [
            good_19,
            plane_fit_and_plot(
                data_19_list[i + 1], data_unmasked_list[i + 1], "", 3, plot=False
            )[1],
        ],
        ignore_index=True,
    )

"""
outs_0875, good_0875 = plane_fit_and_plot(data_0875_list[0], data_unmasked_list[0], '', 3, plot = False)
for i in range(len(data_0875_list) - 1):
    outs_0875 = pd.concat([outs_0875, plane_fit_and_plot(data_0875_list[i+1], data_unmasked_list[i+1], '', 3, plot = False)[0]], ignore_index = True)
    good_0875 = pd.concat([good_0875, plane_fit_and_plot(data_0875_list[i+1], data_unmasked_list[i+1], '', 3, plot = False)[1]], ignore_index = True)
"""

# outs_19.to_csv(r'T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/joe/GHNA_2022_outliers.csv')
# good_19.to_csv(r'T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/joe/GHNA_2022_good.csv')


# outs_0875.to_csv(r'T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/joe/outliers_unmasked_0875.csv')
# good_0875.to_csv(r'T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/joe/good_unmasked_0875.csv')


print(len(outs_19), len(good_19))
print("....")
# print(len(outs_0875), len(good_0875))

plane_fit_and_plot(data_19_330_30, data_unmasked_330_30, "plane_330_30", 3, True)
