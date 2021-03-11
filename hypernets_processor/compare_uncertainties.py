from hypernets_processor.version import __version__
import numpy as np
import xarray
import os.path
import glob
import matplotlib.pyplot as plt

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "25/2/2021"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"

directory=os.path.abspath(r"C:\Users\pdv\PycharmProjects\hypernets_deploy\archive_land")
tags=["L1A_RAD","L1A_IRR","L1B_RAD","L1B_IRR","L1C","L1C","L2A_REF"]
vars=["radiance","irradiance","radiance","irradiance","radiance","irradiance","reflectance"]
for i,tag in enumerate(tags):
    filepaths = [os.path.abspath(path) for path in glob.glob(
                os.path.join(directory,"*"+tag+"*v0.1.nc"))]
    file = xarray.open_dataset(filepaths[0])
    arr=np.empty((len(filepaths),)+file["u_random_"+vars[i]].values.shape)
    arr2=np.empty((len(filepaths),)+file["u_random_"+vars[i]].values.shape)
    arr3=np.empty((len(filepaths),)+file["u_random_"+vars[i]].values.shape)
    for ii,filepath in enumerate(filepaths):
        file=xarray.open_dataset(filepath)
        arr[ii,:,:]=file["u_random_"+vars[i]].values
        if tag=="L2A_REF":
            arr2[ii,:,:] = file["u_systematic_"+vars[i]].values
            arr3[ii,:,:] = file["u_systematic_"+vars[i]].values
        else:
            arr2[ii,:,:]=file["u_systematic_indep_"+vars[i]].values
            arr3[ii,:,:]=file["u_systematic_corr_rad_irr_"+vars[i]].values

    relunc=np.std(arr,axis=0)/np.mean(arr,axis=0)
    relunc2=np.std(arr2,axis=0)/np.mean(arr2,axis=0)
    relunc3=np.std(arr3,axis=0)/np.mean(arr3,axis=0)

    # plt.plot(relunc)
    # plt.plot(relunc2)
    # plt.plot(relunc3)
    # plt.show()

    print("the relative uncertainty on the %s uncertainty is for random, syst_indep and syst_corr: "%tag+vars[i],np.nanmean(relunc),np.nanmean(relunc2),np.nanmean(relunc3))

tags=["L1A_RAD","L1A_IRR"]
vars=["radiance","irradiance"]
for i,tag in enumerate(tags):
    filepaths = [os.path.abspath(path) for path in glob.glob(
                os.path.join(directory,"*"+tag+"*v0.1_SWIR.nc"))]
    file = xarray.open_dataset(filepaths[0])
    arr=np.empty((len(filepaths),)+file["u_random_"+vars[i]].values.shape)
    arr2=np.empty((len(filepaths),)+file["u_random_"+vars[i]].values.shape)
    arr3=np.empty((len(filepaths),)+file["u_random_"+vars[i]].values.shape)
    for ii,filepath in enumerate(filepaths):
        file=xarray.open_dataset(filepath)
        arr[ii,:,:]=file["u_random_"+vars[i]].values
        if tag=="L2A_REF":
            arr2[ii,:,:] = file["u_systematic_"+vars[i]].values
            arr3[ii,:,:] = file["u_systematic_"+vars[i]].values
        else:
            arr2[ii,:,:]=file["u_systematic_indep_"+vars[i]].values
            arr3[ii,:,:]=file["u_systematic_corr_rad_irr_"+vars[i]].values

    relunc=np.std(arr,axis=0)/np.mean(arr,axis=0)
    relunc2=np.std(arr2,axis=0)/np.mean(arr2,axis=0)
    relunc3=np.std(arr3,axis=0)/np.mean(arr3,axis=0)

    plt.plot(relunc)
    #plt.plot(np.mean(relunc2,axis=1))
    #plt.plot(np.mean(relunc3,axis=1))
    plt.show()

    print("the relative uncertainty on the %s uncertainty is for random, syst_indep and syst_corr: "%tag+vars[i],np.nanmean(relunc),np.nanmean(relunc2),np.nanmean(relunc3))
