import xarray as xr
import obsarray
from obsarray import DatasetUtil
import numpy as np

path=r"C:\Users\pdv\OneDrive - National Physical Laboratory\Desktop\GONA_data\archive_test\\"
data=xr.open_dataset(path+"HYPERNETS_W_TEST_L1C_ALL_20211216T1240_20230307T1101_v0.3.nc")

print(data.flag["quality_flag"])
print(data["quality_flag"]>0)
print("here",data.flag["quality_flag"]["saturation"].value.values)
print([DatasetUtil.get_set_flags(flag) for flag in data["quality_flag"]])
print(DatasetUtil.get_flags_mask_or(data["quality_flag"],["outliers","saturation"]))

# print(dat2["quality_flag"].values.dtype,dat2["quality_flag"].encoding)
# print(dat2["reflectance"].values.dtype,dat2["reflectance"].encoding)
# print(dat2["u_rel_random_reflectance"].values.dtype,dat2["u_rel_random_reflectance"].encoding)
# print(dat2["solar_zenith_angle"].values.dtype,dat2["solar_zenith_angle"].encoding)
# print(dat2["n_valid_scans"].values.dtype,dat2["n_valid_scans"].encoding)