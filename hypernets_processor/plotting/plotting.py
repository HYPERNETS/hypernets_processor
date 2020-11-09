"""
Tests for Calibrate class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.dataset_util import DatasetUtil

import matplotlib.pyplot as plt
import numpy as np
import os.path

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "9/10/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"


class Plotting():
    def __init__(self,context,path=None):
        self.context = context
        if path is None:
            if self.context.get_config_value("plotting_directory") is not None:
                self.path = self.context.get_config_value("plotting_directory")
            else:
                self.path = os.path.join(self.context.get_config_value("archive_directory"),"plots")
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        pass

    def plot_variable(self,measurandstring,*args,**kwargs):
        if measurandstring == "radiance":
            self.plot_radiance(*args,**kwargs)
        elif measurandstring == "irradiance":
            self.plot_irradiance(*args,**kwargs)
        elif measurandstring == "reflectance":
            self.plot_reflectance(*args,**kwargs)
        elif measurandstring == "digital_number":
            self.plot_DN(*args,**kwargs)
        else:
            self.plot_other_var(measurandstring,*args,**kwargs)


    def plot_scans_in_series(self,measurandstring,dataset):
        series_id = np.unique(dataset['series_id'])
        for i in range(len(series_id)):
            plotpath = os.path.join(self.path,"plot_"+\
                       dataset.attrs['product_name']+"_series_"+str(
                series_id[i])+"."+self.context.get_config_value("plotting_format"))

            ids = np.where((dataset['series_id'] == series_id[i]))[0]
            ydata_subset=dataset[measurandstring].values[:,ids]
            self.plot_variable(measurandstring,plotpath,dataset["wavelength"].values,
                               ydata_subset)

    def plot_series_in_sequence(self,measurandstring,dataset):
        plotpath = os.path.join(self.path,"plot_"+
                   dataset.attrs['product_name']+"."+self.context.get_config_value("plotting_format"))

        angle_labels=["vza= {:.2f}, vaa= {:.2f}".format(dataset["viewing_zenith_angle"].values[i],dataset["viewing_azimuth_angle"].values[i]) for i in range(len(dataset["viewing_zenith_angle"].values))]
        self.plot_variable(measurandstring,plotpath,dataset["wavelength"].values,
                           dataset[measurandstring].values,labels=angle_labels)

    def plot_diff_scans(self,measurandstring,dataset,dataset_avg=None):
        series_id = np.unique(dataset['series_id'])
        for i in range(len(series_id)):
            plotpath = os.path.join(self.path,"plot_diff_"+
                       dataset.attrs['product_name']+"_series_"+str(
                series_id[i])+"."+self.context.get_config_value("plotting_format"))

            ids = np.where(dataset['series_id'] == series_id[i])[0]

            ydata_subset=dataset[measurandstring].values[:,ids]
            mask=DatasetUtil.unpack_flags(dataset["quality_flag"])["outliers"]
            mask = mask[ids]

            if dataset_avg is None:
                ids_used = np.where((dataset['series_id'] == series_id[i]) & np.invert(
                    DatasetUtil.unpack_flags(dataset["quality_flag"])["outliers"]))[0]
                ydata_subset_used = dataset[measurandstring].values[:,ids_used]
                avgs=np.tile(np.mean(ydata_subset_used,axis=1)[...,None],len(ids))
            else:
                avg_ids = np.where((dataset_avg['series_id'] == series_id[i]))[0]
                avgs = np.tile(dataset_avg[measurandstring].values[:,avg_ids],len(ids))

            self.plot_variable("relative difference",plotpath,dataset["wavelength"].values,
                               (ydata_subset-avgs)/avgs,ylim=[-0.3,0.3],mask=mask)

    def plot_radiance(self,plotpath,xdata,ydata,labels=None):
        fig1,ax1 = plt.subplots(figsize=(10,5))
        if labels is None:
            ax1.plot(xdata,ydata,alpha=0.3)
        else:
            for i in range(len(labels)):
                ax1.plot(xdata,ydata[:,i],label=labels[i],alpha=0.3)
            ax1.legend()
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel(r"Radiance ($mW\ nm^{-1}\ m^{-2}\ sr^{-1}$)")
        ymax = np.percentile(ydata,95)*1.2
        ax1.set_ylim([0,ymax])
        fig1.savefig(plotpath,bbox_inches='tight')
        plt.close(fig1)

    def plot_irradiance(self,plotpath,xdata,ydata,labels=None):
        fig1,ax1 = plt.subplots(figsize=(10,5))
        if labels is None:
            ax1.plot(xdata,ydata,alpha=0.3)
        else:
            for i in range(len(labels)):
                ax1.plot(xdata,ydata[:,i],label=labels[i],alpha=0.3)
            ax1.legend()
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel(r"Irradiance ($mW\ nm^{-1}\ m^{-2}$)")
        ymax = np.percentile(ydata,95)*1.2
        ax1.set_ylim([0,ymax])
        fig1.savefig(plotpath,bbox_inches='tight')
        plt.close(fig1)

    def plot_DN(self,plotpath,xdata,ydata,labels=None):
        fig1,ax1 = plt.subplots(figsize=(10,5))
        if labels is None:
            ax1.plot(xdata,ydata,alpha=0.3)
        else:
            for i in range(len(labels)):
                ax1.plot(xdata,ydata[:,i],label=labels[i],alpha=0.3)
            ax1.legend()
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel(r"digital_number")
        fig1.savefig(plotpath,bbox_inches='tight')
        plt.close(fig1)

    def plot_reflectance(self,plotpath,xdata,ydata,labels=None):
        fig1,ax1 = plt.subplots(figsize=(10,5))
        if labels is None:
            ax1.plot(xdata,ydata,alpha=0.3)
        else:
            for i in range(len(labels)):
                ax1.plot(xdata,ydata[:,i],label=labels[i],alpha=0.3)
            ax1.legend()
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel(r"Reflectance")
        ymax=np.percentile(ydata,95)*1.2
        ax1.set_ylim([0,ymax])
        fig1.savefig(plotpath,bbox_inches='tight')
        plt.close(fig1)

    def plot_other_var(self,measurandstring,plotpath,xdata,ydata,labels=None,ylim=None,mask=None):
        fig1,ax1 = plt.subplots(figsize=(10,5))
        if labels is None and mask is None or len(np.where(mask)[0])==0:
            ax1.plot(xdata,ydata,alpha=0.3)
        elif mask is None:
            for i in range(len(labels)):
                ax1.plot(xdata,ydata[:,i],label=labels[i],alpha=0.3)
        else:
            print(len(np.where(mask)[0]))
            ax1.plot(xdata,ydata[:,np.where(mask)].reshape((len(ydata),len(np.where(mask)[0]))),label="masked",alpha=0.3,color="red")
            ax1.plot(xdata,ydata[:,np.where(np.invert(mask))].reshape((len(ydata),len(np.where(np.invert(mask))[0]))),label="used",alpha=0.3,color="green")

        if labels is not None or mask is not None:
            handles,labels = plt.gca().get_legend_handles_labels()
            by_label = dict(zip(labels,handles))
            ax1.legend(by_label.values(),by_label.keys())
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel(measurandstring)
        if ylim is not None:
            ax1.set_ylim(ylim)
        else:
            ymax = np.percentile(ydata,95)*1.2
            ax1.set_ylim([0,ymax])
        fig1.savefig(plotpath,bbox_inches='tight')
        plt.close(fig1)
