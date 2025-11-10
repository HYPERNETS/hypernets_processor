import xarray as xr
import numpy as np

filename = "GHNAv1_bounds"

data_path = (
    f"T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/bounds/{filename}.nc"
)

data = xr.open_dataset(data_path)
raa_vals = [
    np.mean([float(x) for x in data.raa.values[i].split("_")])
    for i in range(len(data.raa.values))
]
raa_vals[-1] = 0
data["raa"] = raa_vals


data.to_netcdf(
    f"T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/bounds/{filename}_corrected.nc"
)
