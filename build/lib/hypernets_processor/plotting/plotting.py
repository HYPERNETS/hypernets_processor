"""
Tests for Calibrate class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.style.use("seaborn-colorblind")

import numpy as np
import os.path
import warnings
from obsarray.templater.dataset_util import DatasetUtil

"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "9/10/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"


class Plotting:
    def __init__(self, context, path=None, plot_format=None):
        self.context = context
        if path is None:
            self.path = HypernetsWriter(context).return_plot_directory()
        else:
            self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        if plot_format is None:
            self.plot_format = context.get_config_value("plotting_format")
        else:
            self.plot_format = plot_format
        pass

    def plot_variable(self, measurandstring, *args, **kwargs):
        try:
            if measurandstring == "radiance":
                self.plot_radiance(*args, **kwargs)
            elif measurandstring == "irradiance":
                self.plot_irradiance(*args, **kwargs)
            elif measurandstring == "reflectance":
                self.plot_reflectance(*args, **kwargs)
            elif measurandstring == "digital_number":
                self.plot_DN(*args, **kwargs)
            else:
                self.plot_other_var(measurandstring, *args, **kwargs)

        except:
            print("plot failed for %s" % measurandstring)

    def plot_scans_in_series(self, measurandstring, dataset):
        series_id = np.unique(dataset["series_id"])
        for i in range(len(series_id)):
            plotpath = os.path.join(
                self.path,
                "plot_"
                + measurandstring
                + "_"
                + dataset.attrs["product_name"]
                + "_series_"
                + str(series_id[i])
                + "."
                + self.plot_format,
            )

            ids = np.where((dataset["series_id"] == series_id[i]))[0]
            ydata_subset = dataset[measurandstring].values[:, ids]
            if measurandstring == "digital_number":
                self.plot_variable(
                    measurandstring, plotpath, range(len(ydata_subset)), ydata_subset
                )
            else:
                self.plot_variable(
                    measurandstring,
                    plotpath,
                    dataset["wavelength"].values,
                    ydata_subset,
                )

    def plot_series_in_sequence(self, measurandstring, dataset, ylim=None):
        plotpath = os.path.join(
            self.path,
            "plot_"
            + measurandstring
            + "_"
            + dataset.attrs["product_name"]
            + "."
            + self.plot_format,
        )

        if measurandstring == "irradiance":
            angle_labels = dataset["acquisition_time"].values
        else:
            angle_labels = [
                "vza= {:.2f}, vaa= {:.2f}".format(
                    dataset["viewing_zenith_angle"].values[i],
                    dataset["viewing_azimuth_angle"].values[i],
                )
                for i in range(len(dataset["viewing_zenith_angle"].values))
            ]

        if len(angle_labels) > 10:
            linestyles = [
                (0, (3, np.abs(dataset["viewing_zenith_angle"].values[i]) / 10.0))
                if (np.abs(dataset["viewing_azimuth_angle"].values[i]) < 180)
                else (0, (1, np.abs(dataset["viewing_zenith_angle"].values[i]) / 10.0))
                for i in range(len(dataset["viewing_zenith_angle"].values))
            ]

        else:
            linestyles = ["solid"] * len(angle_labels)

        self.plot_variable(
            measurandstring,
            plotpath,
            dataset["wavelength"].values,
            dataset[measurandstring].values,
            labels=angle_labels,
            linestyles=linestyles,
            ylim=ylim,
        )

    def plot_series_in_sequence_vza(self, measurandstring, dataset, vza):
        plotpath = os.path.join(
            self.path,
            "plot_"
            + measurandstring
            + "_"
            + dataset.attrs["product_name"]
            + "_vza"
            + str(vza)
            + "."
            + self.plot_format,
        )

        if measurandstring == "irradiance":
            angle_labels = dataset["acquisition_time"].values
        else:
            angle_labels = np.array(
                [
                    "vza= {:.2f}, vaa= {:.2f}".format(
                        dataset["viewing_zenith_angle"].values[i],
                        dataset["viewing_azimuth_angle"].values[i],
                    )
                    for i in range(len(dataset["viewing_zenith_angle"].values))
                ]
            )

        id_vza = np.where(dataset["viewing_zenith_angle"].values == vza)[0]
        self.plot_variable(
            measurandstring,
            plotpath,
            dataset["wavelength"].values,
            dataset[measurandstring].values[:, id_vza],
            labels=angle_labels[id_vza],
            linestyles=["solid"] * len(id_vza),
        )

    def plot_series_in_sequence_vaa(self, measurandstring, dataset, vaa):
        plotpath = os.path.join(
            self.path,
            "plot_"
            + measurandstring
            + "_"
            + dataset.attrs["product_name"]
            + "_vaa"
            + str(vaa)
            + "."
            + self.plot_format,
        )

        if measurandstring == "irradiance":
            angle_labels = dataset["acquisition_time"].values
        else:
            angle_labels = np.array(
                [
                    "vza= {:.2f}, vaa= {:.2f}".format(
                        dataset["viewing_zenith_angle"].values[i],
                        dataset["viewing_azimuth_angle"].values[i],
                    )
                    for i in range(len(dataset["viewing_zenith_angle"].values))
                ]
            )

        id_vaa = np.where(dataset["viewing_azimuth_angle"].values == vaa)[0]

        self.plot_variable(
            measurandstring,
            plotpath,
            dataset["wavelength"].values,
            dataset[measurandstring].values[:, id_vaa],
            labels=angle_labels[id_vaa],
            linestyles=["solid"] * len(id_vaa),
        )

    def plot_diff_scans(self, measurandstring, dataset, dataset_avg=None):
        series_id = np.unique(dataset["series_id"])
        for i in range(len(series_id)):
            plotpath = os.path.join(
                self.path,
                "plot_diff_"
                + measurandstring
                + "_"
                + dataset.attrs["product_name"]
                + "_series_"
                + str(series_id[i])
                + "."
                + self.plot_format,
            )

            ids = np.where(dataset["series_id"] == series_id[i])[0]

            ydata_subset = dataset[measurandstring].values[:, ids]
            mask = DatasetUtil.unpack_flags(dataset["quality_flag"])["outliers"]
            mask = mask[ids]

            if dataset_avg is None:
                ids_used = np.where(
                    (dataset["series_id"] == series_id[i])
                    & np.invert(
                        DatasetUtil.unpack_flags(dataset["quality_flag"])["outliers"]
                    )
                )[0]
                ydata_subset_used = dataset[measurandstring].values[:, ids_used]
                avgs = np.tile(np.mean(ydata_subset_used, axis=1)[..., None], len(ids))
            else:
                avg_ids = np.where((dataset_avg["series_id"] == series_id[i]))[0]
                avgs = np.tile(
                    dataset_avg[measurandstring].values[:, avg_ids], len(ids)
                )

            self.plot_variable(
                "relative difference",
                plotpath,
                dataset["wavelength"].values,
                (ydata_subset - avgs) / avgs,
                ylim=[-0.3, 0.3],
                mask=mask,
            )

    def plot_relative_uncertainty(self, measurandstring, dataset, L2=False):
        plotpath = os.path.join(
            self.path,
            "plot_unc_"
            + measurandstring
            + "_"
            + dataset.attrs["product_name"]
            + "."
            + self.plot_format,
        )

        yrand = dataset["u_rel_random_" + measurandstring].values
        if L2:
            ysyst = dataset["u_rel_systematic_" + measurandstring].values
            yerr = np.concatenate((yrand, ysyst), axis=1)
            ylabel = np.concatenate(
                (
                    np.repeat(["random uncertainty"], len(yrand[0])),
                    np.repeat(["systematic uncertainty"], len(ysyst[0])),
                )
            )
        else:
            ysyst_corr = dataset[
                "u_rel_systematic_corr_rad_irr_" + measurandstring
            ].values
            ysyst_indep = dataset["u_rel_systematic_indep_" + measurandstring].values
            yerr = np.concatenate((yrand, ysyst_indep, ysyst_corr), axis=1)
            ylabel = np.concatenate(
                (
                    np.repeat(["random uncertainty"], len(yrand[0])),
                    np.repeat(
                        ["independent systematic uncertainty"], len(ysyst_indep[0])
                    ),
                    np.repeat(
                        ["correlated (rad-irr) systematic uncertainty"],
                        len(ysyst_corr[0]),
                    ),
                )
            )
        self.plot_variable(
            "relative uncertainty " + measurandstring + " (%)",
            plotpath,
            dataset["wavelength"].values,
            yerr,
            labels=ylabel,
            ylim=[0, 20],
        )

    def plot_correlation(self, measurandstring, dataset, L2=False):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            plotpath = os.path.join(
                self.path,
                "plot_corr_"
                + measurandstring
                + "_"
                + dataset.attrs["product_name"]
                + "."
                + self.plot_format,
            )

            if L2:
                ycorr = dataset["err_corr_systematic_" + measurandstring].values
                wavs = dataset["wavelength"].values
                fig1, ax1 = plt.subplots(figsize=(5, 5))
                im = ax1.pcolormesh(wavs, wavs, ycorr, vmin=0, vmax=1, cmap="gnuplot")
                ax1.set_ylabel("wavelength (nm)")
                ax1.set_xlabel("wavelength (nm)")
                ax1.set_title("systematic correlation matrix")
                fig1.colorbar(im, ax=ax1)
                fig1.savefig(plotpath, bbox_inches="tight")
                plt.close(fig1)

            else:
                ycorr_indep = dataset[
                    "err_corr_systematic_indep_" + measurandstring
                ].values
                ycorr_corr = dataset[
                    "err_corr_systematic_corr_rad_irr_" + measurandstring
                ].values
                wavs = dataset["wavelength"].values
                fig1, (ax1, ax2) = plt.subplots(ncols=2, nrows=1, figsize=(10, 5))
                ax1.pcolormesh(wavs, wavs, ycorr_indep, vmin=0, vmax=1, cmap="gnuplot")
                ax1.set_ylabel("wavelength (nm)")
                ax1.set_xlabel("wavelength (nm)")
                ax1.set_title("independent systematic correlation matrix")
                im = ax2.pcolormesh(
                    wavs, wavs, ycorr_corr, vmin=0, vmax=1, cmap="gnuplot"
                )
                ax2.set_ylabel("wavelength (nm)")
                ax2.set_xlabel("wavelength (nm)")
                ax2.set_title("correlated (rad-irr) systematic correlation matrix")
                fig1.colorbar(im, ax=ax2)
                fig1.savefig(plotpath, bbox_inches="tight")
                plt.close(fig1)

    def plot_radiance(
        self,
        plotpath,
        xdata,
        ydata,
        labels=None,
        linestyles=None,
        linecolour=None,
        ylim=None,
    ):
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        if labels is None:
            ax1.plot(xdata, ydata, alpha=0.3)
        else:
            for i in range(len(labels)):
                if linestyles is None:
                    ax1.plot(xdata, ydata[:, i], label=labels[i], alpha=0.3)
                else:
                    ax1.plot(
                        xdata, ydata[:, i], label=labels[i], ls=linestyles[i], alpha=0.3
                    )
            if len(labels) > 10:
                ax1.legend(
                    bbox_to_anchor=(1.04, 1), loc="upper left", fontsize=8, ncol=2
                )
            else:
                ax1.legend(fontsize=8, loc="upper right")
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel(r"Radiance ($mW\ nm^{-1}\ m^{-2}\ sr^{-1}$)")
        if ylim is not None:
            ax1.set_ylim(ylim)
        else:
            ymax = np.percentile(ydata, 95) * 1.2
            if np.isfinite(ymax):
                ax1.set_ylim([0, ymax])
        fig1.savefig(plotpath, bbox_inches="tight")
        plt.close(fig1)

    def plot_irradiance(
        self,
        plotpath,
        xdata,
        ydata,
        labels=None,
        linestyles=None,
        linecolour=None,
        ylim=None,
    ):
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        if labels is None:
            ax1.plot(xdata, ydata, alpha=0.3)
        else:
            for i in range(len(labels)):
                ax1.plot(xdata, ydata[:, i], label=labels[i], alpha=0.3)
            ax1.legend(fontsize=8)
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel(r"Irradiance ($mW\ nm^{-1}\ m^{-2}$)")
        if ylim is not None:
            ax1.set_ylim(ylim)
        else:
            ymax = np.percentile(ydata, 95) * 1.2
            if np.isfinite(ymax):
                ax1.set_ylim([0, ymax])
        fig1.savefig(plotpath, bbox_inches="tight")
        plt.close(fig1)

    def plot_DN(
        self,
        plotpath,
        xdata,
        ydata,
        labels=None,
        linestyles=None,
        linecolour=None,
        ylim=None,
    ):
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        if labels is None:
            ax1.plot(xdata, ydata, alpha=0.3)
        else:
            for i in range(len(labels)):
                if linestyles is None:
                    ax1.plot(xdata, ydata[:, i], label=labels[i], alpha=0.3)
                else:
                    ax1.plot(
                        xdata, ydata[:, i], label=labels[i], ls=linestyles[i], alpha=0.3
                    )
            ax1.legend(fontsize=8, ncol=2)
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel(r"digital_number")
        if ylim is not None:
            ax1.set_ylim(ylim)
        fig1.savefig(plotpath, bbox_inches="tight")
        plt.close(fig1)

    def plot_reflectance(
        self,
        plotpath,
        xdata,
        ydata,
        labels=None,
        linestyles=None,
        linecolour=None,
        ylim=None,
    ):
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        if labels is None:
            ax1.plot(xdata, ydata, alpha=0.3)
        else:
            for i in range(len(labels)):
                if linestyles is None:
                    ax1.plot(xdata, ydata[:, i], label=labels[i], alpha=0.3)
                else:
                    ax1.plot(
                        xdata, ydata[:, i], label=labels[i], ls=linestyles[i], alpha=0.3
                    )
            if len(labels) > 10:
                ax1.legend(
                    bbox_to_anchor=(1.04, 1), loc="upper left", fontsize=8, ncol=2
                )
            else:
                ax1.legend(loc="lower right", fontsize=8)
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel(r"Reflectance")
        if ylim is not None:
            ax1.set_ylim(ylim)
        else:
            ymax = np.percentile(ydata, 95) * 1.2
            if np.isfinite(ymax):
                ax1.set_ylim([0, ymax])
        fig1.savefig(plotpath, bbox_inches="tight")
        plt.close(fig1)

    def plot_other_var(
        self,
        measurandstring,
        plotpath,
        xdata,
        ydata,
        labels=None,
        ylim=None,
        mask=None,
        linestyles=None,
        linecolour=None,
    ):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fig1, ax1 = plt.subplots(figsize=(10, 5))
            if labels is None and mask is None or ydata.shape[1] == 1:
                ax1.plot(xdata, ydata, alpha=0.3)
            elif mask is None:
                for i in range(len(labels)):
                    if linestyles is None:
                        ax1.plot(xdata, ydata[:, i], label=labels[i], alpha=0.3)
                    else:
                        ax1.plot(
                            xdata,
                            ydata[:, i],
                            label=labels[i],
                            ls=linestyles[i],
                            alpha=0.3,
                        )
            elif len(np.where(mask)[0]) == 0:
                ax1.plot(xdata, ydata, alpha=0.3)
            else:
                ax1.plot(
                    xdata,
                    ydata[:, np.where(mask)].reshape(
                        (len(ydata), len(np.where(mask)[0]))
                    ),
                    label="masked",
                    alpha=0.3,
                    color="red",
                )
                if not all(mask):
                    ax1.plot(
                        xdata,
                        ydata[:, np.where(np.invert(mask))].reshape(
                            (len(ydata), len(np.where(np.invert(mask))[0]))
                        ),
                        label="used",
                        alpha=0.3,
                        color="blue",
                    )

            if labels is not None or mask is not None:
                handles, labels = plt.gca().get_legend_handles_labels()
                colors = ["red", "blue", "orange", "cyan", "magenta", "green"]
                icol = 0
                labelsb = []
                handlesb = []
                for i, p in enumerate(ax1.get_lines()):
                    if p.get_label() in labelsb:  # check for Name already exists
                        idx = labels.index(p.get_label())  # find ist index
                        p.set_c(ax1.get_lines()[idx].get_c())  # set color
                        p.set_label("_" + p.get_label())  # hide label in auto-legend

                    elif p.get_label()[0] != "_":
                        labelsb.append(p.get_label())
                        handlesb.append(p)
                        p.set_c(colors[icol])
                        icol += 1
                ax1.legend(handlesb, labelsb)  # correct legend

            ax1.set_xlabel("Wavelength (nm)")
            ax1.set_ylabel(measurandstring)
            if ylim is not None:
                ax1.set_ylim(ylim)
            else:
                ymax = np.percentile(ydata, 95) * 1.2
                if np.isfinite(ymax):
                    ax1.set_ylim([0, ymax])
            fig1.savefig(plotpath, bbox_inches="tight")
            plt.close(fig1)

    def plot_quality_irradiance(self, dataset, irrscaled, irrref, refsza):

        plotpath = os.path.join(
            self.path,
            "plot_clearskycheck_irradiance_"
            + dataset.attrs["product_name"]
            + "."
            + self.plot_format,
        )

        angle_labels = [
            "time= {:.0f}, sza= {:.2f}, rescaled to sza= {:.0f}".format(
                dataset["acquisition_time"].values[i],
                dataset["solar_zenith_angle"].values[i],
                refsza,
            )
            for i in range(len(dataset["viewing_zenith_angle"].values))
        ]
        angle_labels = np.append(angle_labels, ["clear sky RT model sza=%s" % refsza])
        ydata = np.hstack((irrscaled, np.atleast_2d(irrref).T))
        self.plot_irradiance(
            plotpath, dataset["wavelength"].values, ydata, labels=angle_labels
        )
