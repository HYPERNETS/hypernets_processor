





import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.pyplot import tight_layout
import scipy.optimize as spo
from setuptools.windows_support import windows_only

#read in data
windows_results_path = r"T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/joe"

linux_data_path = r"/mnt/t/data/insitu/hypernets/post_processing_qc"
windows_data_path = r"T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc"

data = pd.read_csv(windows_data_path + r"/JSIT_None_None_None_None.csv")



maintenance_dates = ['20240513', '20240514', '20240515', '20240516', '20240517', '20240518', '20240519', '20240520']


##get outlier dataset

def get_outliers(data, sigmas):
    mean = data[' refl_550nm'].mean()
    stde = data[' refl_550nm'].std()
    print(mean)
    print(stde)
    max_range = mean + (stde*sigmas)
    min_range = mean - (stde*sigmas)
    outliers = data[(data[' refl_550nm'] > max_range) | (data[' refl_550nm'] < min_range)]
    good_data = data[(data[' refl_550nm'] < max_range) & (data[' refl_550nm'] > min_range)]
    good_data.reset_index(drop = True, inplace = True)
    outliers.reset_index(drop = True, inplace = True)

    fig, axs = plt.subplots(1, 3, figsize = (6,4), sharey = True)
    for i in range(3):
        axs[i].axhline(y = mean, color='blue')
        axs[i].axhline(y = mean - (stde*sigmas) , color='green')
        axs[i].axhline(y = mean + (stde*sigmas), color='orange')
        axs[i].set_title(f'SZA = {(i + 1) * 20}')
        axs[i].scatter(data[data[' sza'].between((i + 1) * 20 - 1, (i + 1) * 20 + 1)][' vza'].values,
                       data[data[' sza'].between((i + 1) * 20 - 1, (i + 1) * 20 + 1)][' refl_550nm'].values,
                       color='black', s=5)
        axs[i].set_xlabel('VZA')
        axs[0].set_ylabel('Reflectance')
    plt.show()
    return outliers, good_data


##get dates and times of measurements

def get_dates_times(data):
    dates = []
    times = []
    for i in range(len(data)):
        date = data['# id'][i][3:11]
        time = data['# id'][i][12:16]
        dates.append(date)
        times.append(time)
    new_data = data.assign(date = dates, time = times)
    return new_data

##get relative azimuthal angle

def get_raa(data):
    data.loc[:, 'raa'] = (data.loc[:, ' vaa'] - data.loc[:, ' saa'] + 360)%360



##manual instrument maintenance day removals

def maintenance_check(data, bad_dates):
### note bad_dates need to be in speech marks###    
    bad_inds = []
#get dates of measurements
    for i in range(len(data)):
        date = data['date'][i]

#remove maintenance dates
        if date in bad_dates:
            bad_index = i
            bad_inds.append(bad_index)
        else:
            continue
    
    cleaned_data = data.drop(bad_inds)
    cleaned_data.reset_index(drop = True, inplace = True)
    return cleaned_data

##sunrise check

def sza_check(data, sza_limit):
    bad_inds = []
    for i in range(len(data)):
        sza = data[' sza'][i]
        if sza > sza_limit:
            bad_index = i
            bad_inds.append(bad_index)
        else:
            continue

    cleaned_data = data.drop(bad_inds)
    cleaned_data.reset_index(drop = True, inplace = True)
    return cleaned_data

def cutter(data, column, type, cut_value):
    if type == 'above':
        clean_data = data[data[column] < cut_value]

    if type == 'below':
        clean_data = data[data[column] > cut_value]

    if type == 'between':
        clean_data = data[(data[column] > cut_value[0]) & (data[column] < cut_value[1])]

    percent = ((len(data) - len(clean_data))/len(data)) * 100
    print('Checks remove {:.2f}% of data'.format(percent))
    return clean_data

##cleaning

def run_checks(data,
               maintenance = False, bad_dates = None,
               sza = False, sza_limit = None, sza_cut_type = None,
               vza = False, vza_limit = None, vza_cut_type = None):
    clean_data = get_dates_times(data)
    get_raa(clean_data)
    if maintenance is True:
        clean_data = maintenance_check(clean_data, bad_dates)
    else:
        pass
    
    if sza is True:
        clean_data = cutter(clean_data, ' sza', sza_cut_type, sza_limit)
    else:
        pass

    if vza is True:
        clean_data = cutter(clean_data, ' vza', vza_cut_type, vza_limit)
    else:
        pass

    percent = ((len(data) - len(clean_data))/len(data)) * 100
    print('Checks remove {:.2f}% of data'.format(percent))
    return clean_data

##cutting tool


##cut 1 dimension and plot
def cut_and_plot_1d(outliers, good_data, cut1, cut1_typ, cut1_ran, x_lab):

    var1 = np.arange(cut1_ran[0], cut1_ran[1], 1)

    out_cuts = []
    good_cuts = []
    diff = []

    for i in range(len(var1)):
        outliers_cut = cutter(outliers, cut1, cut1_typ, var1[i])
        good_cut = cutter(good_data, cut1, cut1_typ, var1[i])

        o_percent = ((len(outliers) - len(outliers_cut)) / len(outliers)) * 100
        g_percent = ((len(good_data) - len(good_cut)) / len(good_data)) * 100

        out_cuts.append(o_percent)
        good_cuts.append(g_percent)
        diff.append(o_percent - g_percent)

    plt.plot( var1, good_cuts, color = 'g', label = 'Good Data')
    plt.plot(var1, out_cuts, color = 'r', label = 'Outliers')
    plt.xlabel(x_lab)
    plt.ylabel('Percent of Data Cut')
    plt.axis([cut1_ran[0], cut1_ran[1], 0, 100])
    plt.grid(alpha = 0.5, color = 'black')
    plt.legend()
    plt.show()



##cut 2 dimensions and plot a 2d colormap
def cut_and_plot_2d(outliers, good_data, cut1, cut1_typ, cut1_ran, cut2, cut2_typ, cut2_ran, x_lab, y_lab):

    var1 = np.arange(cut1_ran[0], cut1_ran[1], 1)
    var2 = np.arange(cut2_ran[0], cut2_ran[1], 1)

    out_cuts = np.zeros((len(var1), len(var2)))
    good_cuts = np.zeros((len(var1), len(var2)))

    for i in range(len(var1)):
        outlier_cut = cutter(outliers, cut1, cut1_typ, var1[i])
        goo_cut = cutter(good_data, cut1, cut1_typ, var1[i])
        for j in range(len(var2)):
            outliers_cut = cutter(outlier_cut, cut2, cut2_typ, var2[j])
            o_percent = ((len(outliers) - len(outliers_cut)) / len(outliers)) * 100

            good_cut = cutter(goo_cut, cut2, cut2_typ, var2[j])
            g_percent = ((len(good_data) - len(good_cut)) / len(good_data)) * 100

            out_cuts[i, j] = o_percent
            good_cuts[i, j] = g_percent

    fig, axs = plt.subplots(1, 3, figsize=(6, 4), layout='constrained')
    axs[0].set_xlabel(x_lab)
    axs[0].set_ylabel(y_lab)
    axs[1].set_xlabel(x_lab)
    axs[1].set_ylabel(y_lab)
    axs[0].set_title('Outliers')
    axs[1].set_title('Good Data')
    axs[2].set_xlabel(x_lab)
    axs[2].set_ylabel(y_lab)
    axs[2].set_title('Difference')
    images = []
    norm = colors.Normalize(vmin=np.min(np.append(out_cuts, good_cuts)), vmax=np.max(np.append(out_cuts, good_cuts)))
    images.append(axs[0].imshow(out_cuts, interpolation='nearest', origin='lower', extent=[cut2_ran[0], cut2_ran[1], cut1_ran[0], cut1_ran[1]], norm=norm))
    images.append(axs[1].imshow(good_cuts, interpolation='nearest', origin='lower', extent=[cut2_ran[0], cut2_ran[1], cut1_ran[0], cut1_ran[1]], norm=norm))
    images.append(axs[2].imshow(out_cuts - good_cuts, interpolation='nearest', origin='lower', extent=[cut2_ran[0], cut2_ran[1], cut1_ran[0], cut1_ran[1]],norm=norm))
    fig.colorbar(images[0], ax=axs, label='Percent of Data Cut')
    plt.show()


##outputting results
def write_csv(data, filename):
    data.to_csv(windows_results_path + filename)

def plot_data(filename, x, y, x_label = None, y_label = None, title = None):
    fig, ax = plt.subplots(1, 1, figsize = (6,4), dpi = 150)
    ax.plot(x, y)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    fig.savefig(windows_results_path + filename)

#more_wav_data = pd.read_csv(windows_data_path + r'/GHNA_refl_2022_None_None_None_None.csv')
data = get_dates_times(data)
get_raa(data)
clean = run_checks(data, maintenance = False, bad_dates = maintenance_dates,
                   sza = False, sza_limit = 70, sza_cut_type = 'above')

more_wav_raa = cutter(cutter(clean, 'raa', 'below', 10), 'raa', 'above', 350)
print(len(clean), len(data))

o, g = get_outliers(clean, 3)
print(len(o), len(g))

#write_csv(clean, '/JSIT_dates_times_raa.csv')
'''
write_csv(clean_more_wav, '/more_wav_prelim_checks_2024_GHNA.csv')
'''
#print(len(get_outliers(clean_more_wav, 3)[0]), len(get_outliers(clean_more_wav, 3)[1]))
##running cuts and plotting
'''
data = get_dates_times(data)
get_raa(data)
clean = run_checks(data, maintenance = True, bad_dates = maintenance_dates,
                   sza = True, sza_limit = 70, sza_cut_type = 'above')

good_data = pd.read_csv(windows_data_path + r'/joe/good_tol01_cloud_checked_GHNA_2024.csv')
outliers = pd.read_csv(windows_data_path + r'/joe/outliers_tol01_cloud_checked_GHNA_2024.csv')


good_clean_19 = run_checks(good_data, maintenance = False, bad_dates =  maintenance_dates,
                           sza = False, sza_limit = 20, sza_cut_type = 'below',
                           vza = True, vza_limit = 15, vza_cut_type = 'below')

out_clean_19 = run_checks(outliers, maintenance = False, bad_dates =  maintenance_dates,
                          sza = False, sza_limit = 10, sza_cut_type = 'below',
                          vza = True, vza_limit = 15, vza_cut_type = 'below')


clean_raa = cutter(cutter(clean, 'raa', 'below', 15), 'raa', 'above', 345)
print(len(clean), len(clean_raa))
#clean_o_raa = cutter(cutter(outliers, 'raa', 'below', 5), 'raa', 'above', 355)
#print(len(outliers), len(clean_o_raa))

#write_csv(clean, '/maintenance_sza70_2024_GHNA.csv')

#cut_and_plot_1d(outliers, good_data, ' vza', 'below', (0,30), 'VZA Cut')

#cut_and_plot_2d(outliers, good_data, 'raa', 'below', (0,20), 'raa', 'above', (340,360), 'RAA Cut Above', 'RAA Cut Below')
'''

#outliers = pd.read_csv(r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\joe\GHNA_2022_outliers.csv')
#good_data = pd.read_csv(r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\joe\GHNA_2022_good.csv')


'''
saa_and_sza_good = good_data[(good_data[' saa'] > 70)
                    & (good_data[' saa'] < 85)
                    & (good_data[' vaa'] > 260)
                    & (good_data[' vaa'] < 300)
                    & (good_data[' sza'] > 60)
                    & (good_data[' sza'] < 70)]

print(len(good_data), len(saa_and_sza_good))

saa_and_sza_out = outliers[(outliers[' saa'] > 70)
                    & (outliers[' saa'] < 85)
                    & (outliers[' vaa'] > 260)
                    & (outliers[' vaa'] < 300)
                    & (outliers[' sza'] > 60)
                    & (outliers[' sza'] < 70)]

print(len(outliers), len(saa_and_sza_out))
'''
'''
saa_and_sza_good = good_data[(good_data[' saa'] > 255)
                    & (good_data[' saa'] < 265)
                    & (good_data[' vaa'] > 290)
                    & (good_data[' sza'] > 65)
                    & (good_data[' sza'] < 70)]

print(len(good_data), len(saa_and_sza_good))

saa_and_sza_out = outliers[(outliers[' saa'] > 255)
                    & (outliers[' saa'] < 265)
                    & (outliers[' vaa'] > 290)
                    & (outliers[' sza'] > 65)
                    & (outliers[' sza'] < 70)]

print(len(outliers), len(saa_and_sza_out))

saa_and_vza_good = good_data[(good_data[' saa'] < 180)
                    & (good_data[' vza'] < 1)]

print(len(good_data), len(saa_and_vza_good))

saa_and_vza_out = outliers[(outliers[' saa'] < 180)
                    & (outliers[' vza'] < 1)]

print(len(outliers), len(saa_and_vza_out))

saa_sza_vza_good = good_data[(good_data[' saa'] < 180)
                    & (good_data[' vza'] < 8)
                    & (good_data[' vza'] > 4)
                    & (good_data[' sza'] > 55)]

print(len(good_data), len(saa_sza_vza_good))

saa_sza_vza_out = outliers[(outliers[' saa'] < 180)
                    & (outliers[' vza'] < 8)
                    & (outliers[' vza'] > 4)
                    & (outliers[' sza'] > 55)]

print(len(outliers), len(saa_sza_vza_out))
'''