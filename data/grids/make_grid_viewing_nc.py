import numpy as np
import xarray as xr
import os

vza = [0, 5, 10, 20, 30, 40, 50, 60]
vaa = [83, 98, 113, 263, 278, 293]

vza_grid, vaa_grid = np.meshgrid(vza, vaa, indexing="ij")

remove_indices = np.where((vza_grid == 0) & (vaa_grid < 180))[0]

vza_grid = np.delete(vza_grid, remove_indices)
vaa_grid = np.delete(vaa_grid, remove_indices)

reference_grid = xr.Dataset(
    data_vars={
        "viewing_zenith_angle": (
            ["series"],
            vza_grid.ravel(),
        ),
        "viewing_azimuth_angle": (
            ["series"],
            vaa_grid.ravel(),
        ),
    },
    coords={"series": range(len(vza_grid.ravel()))},
)

this_dir = os.path.dirname(os.path.abspath(__file__))

reference_grid.to_netcdf(os.path.join(this_dir, "viewing_angles_extended_sequence.nc"))
