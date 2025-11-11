import sqlite3
from sqlite3 import Error
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md

# path2files = r"/archive/test"
# path2figs = r"/home/admin/post_processing/"
# path2files = r"T:/ECO/EOServer/data/insitu/hypernets/archive"
path2figs = r"T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc"

path2files = r"C:\Users\pdv\data\insitu\hypernets\archive"

include_sites = None
include_sites = ["GHNA","WWUK","JSIT","JAES","LOBE"]
start_date = "2022-01-01" #include all dates
stop_date = None #include all dates


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

dbcon = create_connection("/{}/anomaly.db".format(path2files))
SQL_Query = pd.read_sql_query("""select * from anomalies""", dbcon)
df = pd.DataFrame(SQL_Query)
df.index = pd.to_datetime(df.datetime)
df["date"] = df.index.floor("D")
print(df.datetime)
print(df["site_id"].unique())

dbcon = create_connection("/{}/archive.db".format(path2files))
SQL_Query = pd.read_sql_query("""select * from products""", dbcon)
prods = pd.DataFrame(SQL_Query)

#only select relevant sites and product levels
if include_sites is None:
    prodsel = prods
else:
    prodsel = prods[
        prods["site_id"].str.contains(
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

for site in prodsel["site_id"].unique():
    print(site)
    prodsel = prods[prods["site_id"] == site]
    nseq = len(prodsel["sequence_name"].unique())
    dfsel = df[df["site_id"] == site]

    dates=prodsel.datetime_start.unique()
    dates.sort()
    sel_dates = pd.date_range(dates[2], dates[-1], freq="ME").date

    fig = plt.figure(figsize=(10, 15))
    gs = GridSpec(nrows=2, ncols=2)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[1, :])
    ax3 = fig.add_subplot(gs[0, 1])

    # print number of anomalies for site
    df1 = pd.crosstab(dfsel.date, dfsel.anomaly_id)
    df1 = df1.rename_axis(None, axis=1).reset_index()
    df1.index = pd.to_datetime(df1["date"])
    df1 = df1.drop(columns="date")
    # df1.plot.bar()
    dfsum = df1.sum()
    dfsum.plot(kind="bar", ax=ax1)
    ax1.set_ylabel("Number of sequences")
    ax1.set_title("Anomalies for {} seqs. at {}".format(nseq, site))

    dfsel.index = pd.to_datetime(dfsel.datetime)
    dfsel["date"] = dfsel.index.floor("D")
    dfsel["date"] = pd.to_datetime(dfsel.date)
    cross = pd.crosstab(dfsel.date, dfsel.anomaly_id)  # ,margins=True, dropna=False)
    cross["date"] = cross.index
    cross = cross.resample("ME", on="date").sum().reindex(sel_dates)
    cross.plot(kind="bar", ax=ax2, stacked=False)
    ax2.legend(loc="center left", bbox_to_anchor=(1, 0.5), title="Anomalies")
    ax2.set_ylabel("Number of sequences")

    filtered_df = prodsel[
        prodsel["product_level"].str.contains(
            "L0A_RAD|L0A_IRR|L_L1A_RAD|L_L1A_IRR|L_L1B|L_L1C|L_L2A|L_L2B"
        )
    ]
    filtered_df.index = pd.to_datetime(filtered_df.datetime_SEQ)
    filtered_df["date"] = filtered_df.index.floor("D")
    cross = pd.crosstab(
        filtered_df.date, filtered_df.product_level
    )  # ,margins=True, dropna=False)
    cross["date"] = cross.index
    cross = cross.resample("M", on="date").sum().reindex(sel_dates)
    cross.plot(kind="bar", ax=ax3, stacked=False)

    ax3.legend(loc="center left", bbox_to_anchor=(1, 0.5), title="Proc. level")
    ax3.set_ylabel("Number of sequences")

    plt.tight_layout()
    plt.savefig("{}/{}_nseq{}_anomalies_archive.png".format(path2figs, site, nseq))
