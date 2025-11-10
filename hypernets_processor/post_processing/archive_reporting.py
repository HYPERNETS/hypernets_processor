import sqlite3
from sqlite3 import Error
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md

path2files = r"T:/ECO/EOServer/data/insitu/hypernets/archive"
path2figs = r"T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc"

path2files = r"C:\Users\pdv\data\insitu\hypernets\archive"

include_sites = ["GHNA", "JSIT", "WWUK", "LOBE", "JAES"]
start_date = "2022-01-01" #include all dates
stop_date = None #include all dates

# start_date = "2022-01-01"
# stop_date = "2025-12-31"

import sqlite3
from sqlite3 import Error


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

dbcon = create_connection("/{}/archive.db".format(path2files))
SQL_Query = pd.read_sql_query("""select * from products""", dbcon)
prods = pd.DataFrame(SQL_Query)
#only select relevant sites and product levels
prodsel = prods[
    prods["product_level"].str.contains(
        "L_L1B|L_L2A|L_L2B"
    )
]
prodsel = prodsel[
    prodsel["site_id"].str.contains(
        "|".join(include_sites)
    )
]
#only select valid date range
prodsel.index = pd.to_datetime(prodsel.datetime_start, format='mixed')
prodsel["date"] = prodsel.index.floor("D")
prodsel["date"] = pd.to_datetime(prodsel.date)
if start_date is not None:
    prodsel = prodsel[prodsel.index >= pd.to_datetime(start_date)]
if stop_date is not None:
    prodsel = prodsel[prodsel.index <= pd.to_datetime(stop_date)]   

fig = plt.figure(figsize=(15, 5))
ax = fig.add_subplot(1, 1, 1)
cross = pd.crosstab(prodsel.site_id, prodsel.product_level)  # ,margins=True, dropna=False)
cross.plot(kind="bar", ax=ax, stacked=False)
ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), title="Products")
ax.set_ylabel("Number of sequences")

plt.tight_layout()
plt.savefig("{}/all_products_archive.png".format(path2figs))

for site in prodsel["site_id"].unique():
    prodsel = prodsel[prodsel["site_id"] == site]
    prodsel = prodsel[
        prodsel["product_level"].str.contains(
            "L_L1B|L_L2A|L_L2B"
        )
    ]
    print(site,prodsel.date.nanmin(), prodsel.date.nanmax())

    sel_dates = pd.date_range(str(prodsel.date.min()), str(prodsel.date.max()), freq="M").date
    
    fig = plt.figure(figsize=(15, 5))
    ax = fig.add_subplot(1, 1, 1)
    print(sel_dates)

    cross = pd.crosstab(prodsel.date, prodsel.product_level)  # ,margins=True, dropna=False)
    cross["date"] = cross.index
    cross = cross.resample("M", on="date").sum().reindex(sel_dates)
    cross.plot(kind="bar", ax=ax, stacked=False)
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), title="Products")
    ax.set_ylabel("Number of sequences")

    plt.tight_layout()
    plt.savefig("{}/{}_products_archive.png".format(path2figs, site))


    