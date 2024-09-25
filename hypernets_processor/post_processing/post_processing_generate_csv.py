import numpy as np
import hypernets_brdf_data_io as data_io
import os
import glob
import matplotlib.pyplot as plt

# set appropriate folders (different for linux or windows) and settings

#for windows:
# data_path = r"T:\ECO\EOServer\data\insitu\hypernets\archive"
# results_path = r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc"

# for eoserver:
data_path = r"/mnt/t/data/insitu/hypernets/archive"
results_path = r"/mnt/t/data/insitu/hypernets/post_processing_qc"

site = "GHNA"

# results_path = os.path.join(results_path,brdf_model)
if not os.path.exists(results_path):
    os.mkdir(results_path)
start_time = "20220517T0700"
stop_time = "20220901T0700"
wavelength = 550

# start_tod = ["0900","0930","1000","1030","1100"]
# stop_tod = ["0930","1000","1030","1100","1130"]
#
# start_tod = ["0900","1000","1100"]
# stop_tod = ["1000","1100","1200"]

start_tod = [None]
stop_tod = [None]

# #set minimum and maximum reflectance for colourbar plots (Set to None to let it work it out automatically)
vmin=0.18
vmax=0.28

vzas=[20,30,40]
vaas=[83,98,113,263,278,298]

files = glob.glob(os.path.join(data_path, "GHNA", "*", "*", "*", "*", "*L2A*.nc"))

for ii in range(len(start_tod)):
    files = data_io.filter_files_start_stop(files, start_time, stop_time, tod_start=start_tod[ii], tod_stop=stop_tod[ii])

    for vza in vzas:
        for vaa in vaas:
            # read in hypernets data (which returns object of brdf_model.BRDFMeasurements)
            HCRFmeas = data_io.read_data_hypernets(
                files, i=None, vza=vza, vaa=vaa,
            )

            HCRFmeas.export_csv(os.path.join(results_path,"test_%s_%s_%s_%s.csv"%(vza,vaa,start_tod[ii],stop_tod[ii])),wavelength)

            fig1,ax1=plt.subplots()
            ax1.plot(HCRFmeas.get_datetimes(), HCRFmeas.get_reflectance(wavelength), "o", label="before")
            ax1.set_xlabel("datetime")
            ax1.set_ylabel("reflectance")
            ax1.legend(ncol=2)
            ax1.set_ylim([vmin,vmax])
            fig1.savefig(os.path.join(results_path,"refl_calibration_diff_%s_%s_%s_%s.png"%(vza,vaa,start_tod[ii],stop_tod[ii])))
            plt.clf()