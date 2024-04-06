.. description of using HYPERNETS data
   Author: Pieter De Vis
   Email: pieter.de.vis@npl.co.uk
   Created: 20/03/24

.. _user_using_hypernets:

Using HYPERNETS data
======================

This section provides info on how to use the HYPERNETS data produced by the **hypernets_processor** module.
The HYPERNETS products include products from L0A (raw data) to L2B (quality checked reflectance data), which each have different variables, uncertainties, quality flags and metadata.
In this section we will briefly describe what data is available in each of the files and how to access it.
We will also briefly discuss the plots made by the processor and how to access these.
The **hypernets_processor** also produces some SQL databases. These are desribed in :ref:`SQL`.
We do not provide further details on how to access these databases, since they are only meant for internal use.

Reading HYPERNETS products
##########################
The HYPERNETS L0A-L2B data are stored as `netCDF <https://www.unidata.ucar.edu/software/netcdf/>`_ files.
These can be opened using software such as `panoply <https://www.giss.nasa.gov/tools/panoply/>`_).
Within python, the `xarray <https://docs.xarray.dev/en/stable/>`_ package is commonly used to open NetCDF files::

   import xarray as xr
   ds_HYP = xr.open_dataset("comet_training/HYPERNETS_L_GHNA_L2A_REF_20240112T0901_20240315T1804_v2.0.nc")  # read digital effects table

It is often useful to select a specific series in the sequence (especially for land sequences which have many different viewing geometries)::

   vza=0
   vaa=90
   vzadiff=(ds_HYP["viewing_zenith_angle"].values - vza)
   vaadiff=(np.abs(ds_HYP["viewing_azimuth_angle"].values - vaa%360))
   angledif_series = vzadiff** 2 + vaadiff ** 2
   id_series = np.where(angledif_series == np.min(angledif_series))[0]
   ds_HYP = ds_HYP.isel(series=id_series)

The `obsarray <https://obsarray.readthedocs.io/en/latest/>`_ package (which is an extension to xarray) can also be used to more conveniently access flags and uncertainties (see below).
A Jupyter notebook showing how to do this is avaiable `here <https://colab.research.google.com/github/comet-toolkit/comet_training/blob/main/hypernets_surface_reflectance.ipynb>`_.

Handling HYPERNETS flags
-------------------------
The flags detailed in :ref:`flags`, are stored in the netCDF files as a binary number, where each bit encodes for one flag.
There is a flag for each series in the HYPERNETS sequence (see :ref:`data_structure`).
The binary numbers as well as a list with the meanings of each flag can be accessed as follows using xarray::

   import xarray as xr
   import numpy as np

   ds_HYP = xr.open_dataset("HYPERNETS_L_GHNA_L2A_REF_20240112T0901_20240315T1804_v2.0.nc")  # read hypernets file
   print(ds_HYP["quality_flag"].values)
   print(ds_HYP["quality_flag"].attrs["flag_meanings"])

Obsarray has useful functionalily to handle these flags.
There is a DataSetUtil module in obsarray, which can be used as follows to show the meanings of the flags that are set for each series in the sequence::

   from obsarray.templater.dataset_util import DatasetUtil
   print([DatasetUtil.get_set_flags(flag) for flag in ds_HYP["quality_flag"]])

As well as functions to check if certain flags are set for each series::

   print(DatasetUtil.get_flags_mask_or(ds_HYP["quality_flag"], ["outliers", "series_missing"]))
   print(DatasetUtil.get_flags_mask_and(ds_HYP["quality_flag"], ["outliers", "series_missing"]))

This can also be used to remove data with certain flags from the hupernets products::

   bad_flags=["pt_ref_invalid", "half_of_scans_masked", "not_enough_dark_scans", "not_enough_rad_scans",
              "not_enough_irr_scans", "no_clear_sky_irradiance", "variable_irradiance",
              "half_of_uncertainties_too_big", "discontinuity_VNIR_SWIR", "single_irradiance_used"]
   flagged = DatasetUtil.get_flags_mask_or(ds_HYP["quality_flag"], bad_flags) # bools for each series if any bad flag is set
   id_series_valid = np.where(~flagged)[0] # select indexes for which no bad flags are set
   ds_HYP = ds_HYP.isel(series=id_series_valid) # for all variables in ds_hyp, keep only the series with no bad flags set

For further details we refer to the `Jupyter notebook <https://colab.research.google.com/github/comet-toolkit/comet_training/blob/main/hypernets_surface_reflectance.ipynb>`_.

Accessing and propagating HYPERNETS uncertainties
--------------------------------------------------
The examples shown below are also available in `this Jupyter notebook <https://colab.research.google.com/github/comet-toolkit/comet_training/blob/main/hypernets_surface_reflectance.ipynb>`_.

**xarray**:
The uncertainty variables in the netCDF files can be accessed simply using xarray, and include error correlation information in the attributes:::

   import xarray as xr
   import numpy as np

   ds_HYP = xr.open_dataset("HYPERNETS_L_GHNA_L2A_REF_20240112T0901_20240315T1804_v2.0.nc")  # read hypernets file
   print(ds_HYP["u_rel_systematic_reflectance"])  # print xarray variable (includes dimensions and attributes)
   print(ds_HYP["u_rel_systematic_reflectance"].values)  # print uncertainty values only

In the output, we see that the err_corr_1_params attribute refers to the error correlation matrix variable. This one is also available in the dataset::

   print(ds_HYP["err_corr_systematic_reflectance"].values)

**obsarray**:
`obsarray <https://obsarray.readthedocs.io/en/latest/>`_ can be used
to conveniently handle uncertainties in the HYPERNETS products.
It can e.g. be used to inspect uncertainty variables for a particular variable, and calculate the total uncertainties::

   import obsarray
   print(ds_HYP.unc["reflectance"])
   print(ds.unc["temperature"].total_unc())

For further functionality we refer to `this jupiter notebook <https://colab.research.google.com/github/comet-toolkit/comet_training/blob/main/obsarray_example.ipynb>`_ on using obsarray.

**punpy**:
`punpy <https://punpy.readthedocs.io/en/latest/>`_ can be used to conveniently propagate uncertainties in the HYPERNETS products.
In the `Jupyter notebook <https://colab.research.google.com/github/comet-toolkit/comet_training/blob/main/hypernets_surface_reflectance.ipynb>`_, we show an example of
how to propagate HYPERNETS uncertainties through integration over the Sentinel-2A SRF. In summary, a subclass of the punpy MeasurementFunction Class
needs to be made with implementations for the meas_function(), get_argument_names() and get_measurand_name_and_unit().
Once this is done, the uncertainties can simply be propagated as follows::

   from punpy import MCPropagation
   prop = MCPropagation(100,parallel_cores=1)
   band_int_S2 = BandIntegrateS2A(prop, use_err_corr_dict=True)
   ds_HYP_full_S2 = band_int_S2.propagate_ds(ds_HYP_full)
   print(ds_HYP_full_S2)

For site owners
################

accessing data directories on HYPERNETS servers
----------------------------------------------------
The following lines are also useful terminal commands to access the data. For instance to get the number of directories::

$ ls | wc -l
$ ls -dq *SEQ* | wc -l

To list all directories::

$ ls /waterhypernet/HYPSTAR/Raw/MAFR/DATA > MAFR_seqlist.csv

To investigate the directory size::

$ du -sh (readable direcotry size)

