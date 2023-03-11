"""
Database schema specification for Hypernets land and water network
"""

# The set of defined processor schema is defined below in DB_DICT_DEFS. Each entry is the name of a defined schema
# format, the value is the schema definition.
#
# Each processor database schema is also defined below, in one of the two following ways:
#
# a. Dictionary definition
# ------------------------
#
# Each entry in the dictionary is the name of a table to be defined, the value of each entry is a dictionary that
# defines the table, it has the following entries:
#
# * "columns" - defines the table columns
#
#    each entry in the dictionary is the name of a column to be defined, the value of each entry is a dictionary that
#    defines the column, this has entries:
#
#    - "type" - defines the column type, value should be python type
#    - "foreign_key" (optional) - defines if column is foreign key to reference table. Value is dictionary structured
#      as: `{"reference_table": "<table_name>", "reference_column": "column_name"}`.
#      NB: This is not supported for defining sqlite databases. If this is required, please define as SQL command
#      (option b)
#    - other entries may be kwargs supported by dataset.table.Table.create_column
#
# * "primary_key" - defines the tables primary key, value is the column name.
# * other entries may be kwargs supported by dataset.database.Database.create_table
#
# b. SQL definition
# -----------------
#
# Databases may be defined with SQL commands as strings
#
#
# Database formats are defined following the specification defined in:
# Hypernets Team, Product Data Format Specification, v0.5 (2020)

from hypernets_processor.data_io.format.metadata import METADATA_DEFS

# Metadata Database
METADATA_DB = {}

for level in METADATA_DEFS.keys():
    coldict = {}
    for key in METADATA_DEFS[level].keys():
        coldict[key] = {"type": str}
    METADATA_DB[level] = {"columns": coldict}

# Anomaly Database
ANOMALY_DB = {
    "anomalies": {
        "columns": {
            "anomaly_id": {"type": str},
            "sequence_name": {"type": str},
            "sequence_path": {"type": str},
            "site_id": {"type": str},
            "datetime": {"type": str},
            "rel_product_dir": {"type": str},
            "product_level_last": {"type": str},
            "product_path_last": {"type": str},
            "solar_zenith_angle_min": {"type": str},
            "solar_zenith_angle_max": {"type": str},
            "solar_azimuth_angle_min": {"type": str},
            "solar_azimuth_angle_max": {"type": str},
        }
    }
}

# Archive Database
ARCHIVE_DB = {
    "products": {
        "columns": {
            "product_name": {"type": str},
            "datetime": {"type": str},
            "sequence_name": {"type": str},
            "site_id": {"type": str},
            "system_id": {"type": str},
            "product_level": {"type": str},
            "product_path": {"type": str},
            "rel_product_dir": {"type": str},
            "sequence_path": {"type": str},
            "latitude": {"type": str},
            "longitude": {"type": str},
            "solar_zenith_angle_min": {"type": str},
            "solar_zenith_angle_max": {"type": str},
            "solar_azimuth_angle_min": {"type": str},
            "solar_azimuth_angle_max": {"type": str},
            "viewing_zenith_angle_min": {"type": str},
            "viewing_zenith_angle_max": {"type": str},
            "viewing_azimuth_angle_min": {"type": str},
            "viewing_azimuth_angle_max": {"type": str},
        }
    }
}


# Database format defs
# --------------------

DB_DICT_DEFS = {"metadata": METADATA_DB, "anomaly": ANOMALY_DB, "archive": ARCHIVE_DB}
