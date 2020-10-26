"""
Tests for Calibrate class
"""

from hypernets_processor.version import __version__
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
    def __init__(self,context):
        self.context = context
        if not os.path.exists(self.context.get_config_value("plotting_directory")):
            os.makedirs(self.context.get_config_value("plotting_directory"))
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
            plotpath = self.context.get_config_value("plotting_directory")+"plot_"+\
                       dataset.attrs['product_name']+"_series_"+str(
                series_id[i])+"."+self.context.get_config_value("plotting_fmt")

            ids = np.where((dataset['series_id'] == series_id[i]))[0]
            ydata_subset=dataset[measurandstring].values[:,ids]
            self.plot_variable(measurandstring,plotpath,dataset["wavelength"].values,
                               ydata_subset)

    def plot_series_in_sequence(self,measurandstring,dataset):
        plotpath = self.context.get_config_value("plotting_directory")+"plot_"+\
                   dataset.attrs['product_name']+"."+self.context.get_config_value("plotting_fmt")

        angle_labels=["sza= {:.2f}, saa= {:.2f}".format(dataset["solar_zenith_angle"].values[i],dataset["solar_azimuth_angle"].values[i]) for i in range(len(dataset["solar_zenith_angle"].values))]
        self.plot_variable(measurandstring,plotpath,dataset["wavelength"].values,
                           dataset[measurandstring].values,labels=angle_labels)

    def plot_diff_scans(self,measurandstring,dataset,dataset_avg=None):
        series_id = np.unique(dataset['series_id'])
        for i in range(len(series_id)):
            plotpath = self.context.get_config_value("plotting_directory")+"plot_diff_"+\
                       dataset.attrs['product_name']+"_series_"+str(
                series_id[i])+"."+self.context.get_config_value("plotting_fmt")


            ids = np.where((dataset['series_id'] == series_id[i]))[0]
            ydata_subset=dataset[measurandstring].values[:,ids]
            if dataset_avg is None:
                avgs=np.tile(np.mean(ydata_subset,axis=1)[...,None],len(ydata_subset[0]))
            else:
                avg_ids = np.where((dataset_avg['series_id'] == series_id[i]))[0]
                avgs = np.tile(dataset_avg[measurandstring].values[:,avg_ids],len(ydata_subset[0]))

            self.plot_variable("relative difference",plotpath,dataset["wavelength"].values,
                               (ydata_subset-avgs)/avgs)

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
        ax1.set_ylim([0,1])
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
        ax1.set_ylabel(r"Radiance ($mW\ nm^{-1}\ m^{-2}$)")
        ax1.set_ylim([0,100])
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
        fig1.savefig(plotpath,bbox_inches='tight')
        plt.close(fig1)

    def plot_other_var(self,measurandstring,plotpath,xdata,ydata,labels=None):
        fig1,ax1 = plt.subplots(figsize=(10,5))
        if labels is None:
            ax1.plot(xdata,ydata,alpha=0.3)
        else:
            for i in range(len(labels)):
                ax1.plot(xdata,ydata[:,i],label=labels[i],alpha=0.3)
            ax1.legend()
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel(measurandstring)
        fig1.savefig(plotpath,bbox_inches='tight')
        plt.close(fig1)