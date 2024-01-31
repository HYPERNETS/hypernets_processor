import sqlite3
from sqlite3 import Error
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
path2figs="/home/data/insitu/hypernets/QC/"
path2files="/home/data/insitu/hypernets/archive/"
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

def closest_idx(xlist, xval):
        idx, xret = min(enumerate(xlist), key=lambda x: abs(float(x[1]) - float(xval)))
        return (idx, xret)

def get_flag_encoding(da):
    """
    Returns flag encoding for flag type data array
    :type da: xarray.DataArray
    :param da: data array
    :return: flag meanings
    :rtype: list
    :return: flag masks
    :rtype: list
    """

    try:
        flag_meanings = da.attrs["flag_meanings"].split()
        flag_masks = [int(fm) for fm in da.attrs["flag_masks"].split(",")]
    except KeyError:
        raise KeyError(da.name + " not a flag variable")

    return flag_meanings, flag_masks


def get_flags(da):
    """
    Returns flag encoding for flag type data array
    :type da: xarray.DataArray
    :param da: data array
    :return: flag meanings
    :rtype: list
    :return: flag masks
    :rtype: list
    """

    try:
        flag_meanings = da.attrs["flag_meanings"].split()
        flag_masks = [int(fm) for fm in da.attrs["flag_masks"].split(",")]
    except KeyError:
        raise KeyError(da.name + " not a flag variable")

    return [([i],flag_meanings[i],flag_masks[i]) for i in range(0,len(flag_meanings))
            if ds['quality_flag'].values[i]!=0]

def flags(da):
    qf=da["quality_flag"].values
    flagsname=get_flag_encoding(da["quality_flag"])[0]
    flagsval=get_flag_encoding(da["quality_flag"])[1]
    flags=np.full((len(qf),len(flagsname)),False,dtype=bool)
    for i in range(0,len(qf)):
        n=qf[i]
        while n > 0:
            r=2**round(np.log2(n))
            for j in range(0,len(flagsval)):
                flags[i,j]=(r==flagsval[j])
            n=n-r
    flags=pd.DataFrame(flags, columns=flagsname)
    return flags



dbcon=create_connection("/{}/anomaly.db".format(path2files))
SQL_Query = pd.read_sql_query(
    '''select * from anomalies''', dbcon)
df = pd.DataFrame(SQL_Query)
df.index=pd.to_datetime(df.datetime)
df['date']=df.index.floor('D')
print(df.datetime)
print(df['site_id'].unique())

dbcon=create_connection("/{}/archive.db".format(path2files))
SQL_Query = pd.read_sql_query(
    '''select * from products''', dbcon)
prods = pd.DataFrame(SQL_Query)
all_dates = pd.date_range("2023-01-01", "2023-12-31", freq='M').date

for site in df['site_id'].unique():
    print(site)
    prodsel = prods[prods['site_id'] == site]
    nseq = len(prodsel['sequence_name'].unique())
    dfsel = df[df['site_id'] == site]

    fig = plt.figure(figsize=(15, 5))
    gs = GridSpec(nrows=2, ncols=2)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[1, :])
    ax3 = fig.add_subplot(gs[0, 1])

    # print number of anomalies for site
    df1 = pd.crosstab(dfsel.date, dfsel.anomaly_id)
    df1 = df1.rename_axis(None, axis=1).reset_index()
    df1.index = pd.to_datetime(df1['date'])
    df1 = df1.drop(columns='date')
    # df1.plot.bar()
    dfsum = df1.sum()
    dfsum.plot(kind="bar", ax=ax1)
    ax1.set_ylabel("Number of sequences")
    ax1.set_title('Anomalies for {} seqs. at {}'.format(nseq, site))

    dfsel.index = pd.to_datetime(dfsel.datetime)
    dfsel['date'] = dfsel.index.floor('D')
    dfsel['date'] = pd.to_datetime(dfsel.date)
    cross = pd.crosstab(dfsel.date, dfsel.anomaly_id)  # ,margins=True, dropna=False)
    cross['date'] = cross.index
    cross = cross.resample('M', on='date').sum().reindex(all_dates)
    cross.plot(kind="bar", ax=ax2, stacked=False)
    ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5), title='Anomalies')
    ax2.set_ylabel("Number of sequences")

    filtered_df = prodsel[prodsel["product_level"].str.contains("L0A_RAD|L0A_IRR|L_L1A_RAD|L_L1A_IRR|L_L1B|L_L1C|L_L2A")]
    filtered_df.index = pd.to_datetime(filtered_df.datetime_SEQ)
    filtered_df['date'] = filtered_df.index.floor('D')
    cross = pd.crosstab(filtered_df.date, filtered_df.product_level)  # ,margins=True, dropna=False)
    cross['date'] = cross.index
    cross = cross.resample('M', on='date').sum().reindex(all_dates)
    cross.plot(kind="bar", ax=ax3, stacked=False)

    ax3.legend(loc='center left', bbox_to_anchor=(1, 0.5), title='Proc. level')
    ax3.set_ylabel("Number of sequences")

    plt.tight_layout()
    plt.savefig('{}/{}_nseq{}_anomalies_archive.png'.format(path2figs, site, nseq))

