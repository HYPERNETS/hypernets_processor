import xarray as xr
import obsarray

name="HYPERNETS_L_TEST_L2A_REF_20220718T1317_20230305T1849_v0.3.nc"
dat2=xr.open_dataset(r"C:\Users\pdv\OneDrive - National Physical Laboratory\Desktop\GONA_data\archive_test\%s"%name)


print(dat2["quality_flag"].values.dtype,dat2["quality_flag"].encoding)
print(dat2["reflectance"].values.dtype,dat2["reflectance"].encoding)
print(dat2["solar_zenith_angle"].values.dtype,dat2["solar_zenith_angle"].encoding)
print(dat2["n_valid_scans"].values.dtype,dat2["n_valid_scans"].encoding)
print(dat2.flag["quality_flag"]["saturation"])