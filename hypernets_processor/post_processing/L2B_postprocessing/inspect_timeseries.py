import datetime

import numpy as np
import hypernets_processor.post_processing.L2B_postprocessing.hypernets_brdf_data_io as data_io
import os
import glob
import matplotlib

matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd

# set appropriate folders (different for linux or windows) and settings
data_path = r"T:\ECO\EOServer\data\insitu\hypernets\archive"
results_path = r"./"
site = "GHNA"

# results_path = os.path.join(results_path,brdf_model)
if not os.path.exists(results_path):
    os.mkdir(results_path)
start_time = "20250701T0000"
stop_time = "20260901T0000"

start_tod = [None]
stop_tod = [None]



def get_vals(data):
    acquisitionTime = data.acquisition_time.values
    accx = data.acceleration_x_mean.values
    accy = data.acceleration_y_mean.values
    accz = data.acceleration_z_mean.values
    vzas = data.viewing_zenith_angle.values
    vaas = data.viewing_azimuth_angle.values
    
    return acquisitionTime, accx, accy, accz, vzas, vaas


##running
if os.path.exists(os.path.join(results_path, "GHNA_acceleration_%s_%s.csv") % (start_time, stop_time)):
    print("Results already exist.")
    aquisitionTime_all, accx_all, accy_all, accz_all, vzas_all, vaas_all = pd.read_csv(
        os.path.join(results_path, "GHNA_acceleration_%s_%s.csv") % (start_time, stop_time)
    ).values.T

else:

    files = glob.glob(os.path.join(data_path, "GHNA", "*", "*", "*", "*", "*L1B_IRR*.nc"))

    print("Files In")

    for ii in range(len(start_tod)):
        files = data_io.filter_files_quick(
            files, start_time, stop_time, tod_start=start_tod[ii], tod_stop=stop_tod[ii]
        )
    print("Files Sorted")

    aquisitionTime_all = np.zeros(len(files))
    accx_all = np.zeros(len(files))
    accy_all = np.zeros(len(files))
    accz_all = np.zeros(len(files))
    vzas_all = np.zeros(len(files))
    vaas_all = np.zeros(len(files))

    for ifile, file in enumerate(files):
        print("Processing file: " + str(ifile) + " of " + str(len(files)))
        data = xr.open_dataset(file)
        acquisitionTime, accx, accy, accz, vzas, vaas = get_vals(data)
        aquisitionTime_all[ifile] = np.mean(acquisitionTime)
        accx_all[ifile] = np.mean(accx)
        accy_all[ifile] = np.mean(accy)
        accz_all[ifile] = np.mean(accz)
        vzas_all[ifile] = np.mean(vzas)
        vaas_all[ifile] = np.mean(vaas)

    #save to csv
    df = pd.DataFrame(
        {
            "acquisition_time": aquisitionTime_all,
            "accx": accx_all,
            "accy": accy_all,
            "accz": accz_all,
            "vzas": vzas_all,
            "vaas": vaas_all,
        }
    )
    df.to_csv(os.path.join(results_path, "GHNA_acceleration_%s_%s.csv") % (start_time, stop_time), index=False)


aquisitionTime_all = [datetime.datetime.fromtimestamp(t) for t in aquisitionTime_all]
plt.plot(aquisitionTime_all, accx_all)
plt.savefig(os.path.join(results_path, "GHNA_acceleration_x.png"))
plt.clf()

plt.plot(aquisitionTime_all, accy_all)
plt.savefig(os.path.join(results_path, "GHNA_acceleration_y.png"))
plt.clf()

plt.plot(aquisitionTime_all, accz_all)
plt.savefig(os.path.join(results_path, "GHNA_acceleration_z.png"))
plt.clf()

plt.plot(aquisitionTime_all, vzas_all)
plt.savefig(os.path.join(results_path, "GHNA_viewing_zenith_angle.png"))
plt.clf()

plt.plot(aquisitionTime_all, vaas_all)
plt.savefig(os.path.join(results_path, "GHNA_viewing_azimuth_angle.png"))
plt.clf()
