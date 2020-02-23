"""
Standard metadata for Hypernets L1, L2a and L2b files, for the land a water network
"""

COMMON_METADATA = {"resource_abstract": "The HYPERNETS project (Horizon 2020 research and innovation, grant agreement "
                                        "No 775983) has the overall aim to provide high quality in situ measurements to"
                                        "support the (visible/SWIR) optical Copernicus products. Therefore a new "
                                        "multi-head hyperspectral spectroradiometer dedicated to land and water surface"
                                        " reflectance validation with instrument pointing capabilities and embedded "
                                        "calibration device has been established. The instrument has been deployed at "
                                        "24 sites covering a range of water and land types and a range of climatic and"
                                        "logistic conditions (www.hypernets.eu).",
                   "metadata_language": "eng",
                   "lineage": "Dataset is quality assured (ATBD document link)",
                   "unique_resource_code_identifier": "doi.xxxx",
                   "spatial_data_theme": "point",
                   "data_created": None,  # adds on write
                   "project": "HYPERNETS",
                   "acknowledgement": "HYPERNETS project is funded by Horizon 2020 research and innovation programm, "
                                      "grant agreement No 775983. Consortium of HYPERNETS project, PI of hypernets test"
                                      " sites, ... are acknowledged.",
                   "licence": "Attribution-NonCommercial-NoDerivs CC BY-NC-ND",
                   "limitations_on_public_access": "no limitations to public access",
                   "conditions_applying_to_access_and_use": "no conditions to access and use",
                   "degree_of_conformity": "no evaluated"
                   }

L1_METADATA = {"resource_title": "HYPERNETS network dataset of downwelling irradiance and upwelling and downwelling "
                                 "radiance"}

L2_METADATA = {"resource_title": "HYPERNETS network dataset of spectral surface reflectance"}

LAND_NETWORK_METADATA = {"responsible_party": "National Physical Laboratory, UK",
                         "creator_name": "Hunt Sam",
                         "creator_email": "sam.hunt@npl.co.uk",
                         "topic_category": "land, environment, geoscientific information"}

WATER_NETWORK_METADATA = {"responsible_party": "Royal Belgian Institute for Natural Sciences, "
                                               "Directorate Natural Environment, REMSEM",
                          "creator_name": "Goyens Clémence",
                          "creator_email": "cgoyens@naturalsciences.be",
                          "topic_category": "oceans, environment, inland waters, geoscientific information"}
