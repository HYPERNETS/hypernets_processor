"""Run MCMC for atmospheric retrieval"""
import punpy

"""___Built-In Modules___"""
from GHNA_processing.data_io.read_hypernets import read_db_hypernets, read_hypernets_file
from GHNA_processing.data_io.read_radcalnet import read_db_radcalnet_BOA
from GHNA_processing.RadCalNet_conversion.convert_radcalnet import Convert_RadCalNet


"""___Third-Party Modules___"""
import datetime as dt
from datetime import datetime, timedelta
import numpy as np
import os
import matplotlib.pyplot as plt
import comet_maths as cm

"""___NPL Modules___"""


__author__ = "Pieter De Vis <pieter.de.vis@npl.co.uk>"

#outputs for GHNA processing
#output_path = r"\\mnt\\t\\ECO\\EOServer\\data\\insitu\\hn_processor"
#paths for windows use
# output_path = os.path.join(r"T:\\", "ECO", "EOServer", "data", "insitu", "hn_processor")
# hypernets_path = r"\\eoserver\home\data\insitu\hypernets\archive"
# db_path = r"\\eoserver\home\data\calvalresults\v2"
# radcalnet_path = os.path.join(r"T:\\", "ECO", "EOServer", "data", "insitu", "radcalnet", "RadCalNetAll-sites-May2024", "GONA")
# asd_path = os.path.join(r"T:\\", "ECO", "EOServer", "data", "insitu", "asd_gobabeb_2020", "wref_corrected.txt")
# BRDF_file = os.path.join(r"T:\\", "ECO", "EOServer", "data", "insitu", "brdf","all_wavelengths" , "BRDFparams_all_20231024T0820_20240516T1143.pkl")
# irr_file = os.path.join(r"T:\\", "ECO", "EOServer", "data", "insitu", "brdf", "irr_all.nc")

#paths for eoserver use
output_path = r"/mnt/t/data/insitu/hn_processor/v2_vza20"
hypernets_path = r"/home/data/insitu/hypernets/archive"
db_path="/home/data/calvalresults/v2"
radcalnet_path = r"/mnt/t/data/insitu/radcalnet/RadCalNetAll-sites-May2024/GONA"
# #os.path.join("mnt", "t", "ECO", "EOServer", "data", "insitu", "radcalnet", "Radcalnet_alldata_aug23", "GONA")
asd_path = r"/mnt/t/data/insitu/asd_gobabeb_2020/wref_corrected.txt"
#os.path.join("mnt", "t", "ECO", "EOServer", "data", "insitu", "asd_gobabeb_2020", "wref_corrected.txt")
BRDF_file = r"/mnt/t/data/insitu/brdf/all_wavelengths/BRDFparams_all_20231024T0820_20240516T1143.pkl"
irr_file = r"/mnt/t/data/insitu/brdf/irr_all.nc"


conv = Convert_RadCalNet(output_path, BRDF_file, irr_file)
vza_hyp = 20

def identify_matchups(site, radcalnet_db, start_date, end_date, only_passed_qc=False):
    """
    Return catalogue product url(s) that satisfy query

    :param query: catalogue query
    :return: product urls satisfying query
    """
    print("identifying matchups")
    start_datetime, end_datetime = parse_startend(start_date, end_date)
    hypcat = read_db_hypernets(db_path, hypernets_path, site, start_date, end_date,only_passed_qc=only_passed_qc)
    hypcat_datetimes = np.array([
        dt.datetime.strptime(hypdat[3], "%Y-%m-%d %H:%M:%S.%f") for hypdat in hypcat
    ])

    radcat = read_db_radcalnet_BOA(
        radcalnet_path, db_path, radcalnet_db, start_datetime, end_datetime
    )
    radcat_datetimes = radcat[:, 1]

    matchups = np.empty((len(radcat_datetimes), 5), dtype=object)
    for i in range(len(radcat_datetimes)):
        matchups[i, 0] = radcat[i]
        id_best = np.argmin(np.abs(radcat_datetimes[i] - hypcat_datetimes))
        if radcat_datetimes[i]>hypcat_datetimes[id_best]:
            id_best_before = id_best
            id_best_after = min(id_best + 1,len(hypcat)-1)
        else:
            id_best_before = id_best -1
            id_best_after = id_best

        matchups[i, 1] = hypcat[id_best_before, :]
        matchups[i, 2] = hypcat[id_best_after, :]
        diff = (
                radcat_datetimes[i] - hypcat_datetimes[id_best_before]
        )
        matchups[i, 3] = diff.days * 24 * 60 + diff.seconds / 60
        diff = (
                radcat_datetimes[i] - hypcat_datetimes[id_best_after]
        )
        matchups[i, 4] = diff.days * 24 * 60 + diff.seconds / 60
    return matchups

def filter_matchups(matchups, timediff=None):
    if timediff is not None:
        condition = (abs(matchups[:, 3]) < timediff) & (abs(matchups[:, 4]) < timediff)
        matchups = matchups[np.where(condition)[0], :]
        print(len(matchups), "matchups found within %s min" % timediff)
    return matchups

def parse_startend(start_date, end_date):
    if not isinstance(start_date, datetime):
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        except:
            raise ValueError("start_date does not have the right format")

    if not isinstance(end_date, datetime):
        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except:
            raise ValueError("end_date does not have the right format")
    return start_date, end_date

def process_matchup(matchup):
    prop=punpy.MCPropagation(10, parallel_cores=1)

    rcn_name=matchup[0][0]
    rcn_datetime=matchup[0][1].timestamp()
    rcn_wav=matchup[0][2]
    rcn_refl=matchup[0][3]
    u_rcn_refl=matchup[0][4]
    atm_prop=matchup[0][5]
    u_atm_prop=matchup[0][6]

    hypernets_ds_pre = read_hypernets_file(matchup[1][-1], vza=vza_hyp)
    print(hypernets_ds_pre.reflectance.values[100,:])
    hypernets_ds_pre = conv.correct_to_nadir(hypernets_ds_pre)
    print(hypernets_ds_pre.reflectance.values[100,:])
    hypernets_datetime_pre = np.mean(hypernets_ds_pre.acquisition_time.values)

    hyp_wav_pre = hypernets_ds_pre.wavelength.values
    hyp_refl_pre = np.mean(hypernets_ds_pre.reflectance.values, axis=1)
    hyp_std_pre = np.std(hypernets_ds_pre.reflectance.values, axis=1)
    u_rand_pre = ((
            (np.mean(hypernets_ds_pre.u_rel_random_reflectance.values, axis=1)
            * 0.01
            * hyp_refl_pre)**2
            + hyp_std_pre**2)**0.5
        / np.sqrt(3))
    u_syst_pre = (
            np.mean(hypernets_ds_pre.u_rel_systematic_reflectance.values, axis=1)
            * 0.01
            * hyp_refl_pre
    )
    u_hyp_refl_pre = np.sqrt(u_rand_pre ** 2 + u_syst_pre ** 2)
    cov_hyp_refl_pre = cm.convert_corr_to_cov(np.eye(len(u_rand_pre)),u_rand_pre) + cm.convert_corr_to_cov(hypernets_ds_pre.err_corr_systematic_reflectance.values,u_syst_pre)
    corr_hyp_refl_pre = cm.convert_cov_to_corr(cov_hyp_refl_pre,u_hyp_refl_pre)

    print(corr_hyp_refl_pre,cm.uncertainty_from_covariance(cov_hyp_refl_pre)/u_hyp_refl_pre)

    hypernets_ds_aft = read_hypernets_file(matchup[2][-1], vza=vza_hyp)
    hypernets_ds_aft = conv.correct_to_nadir(hypernets_ds_aft)
    hypernets_datetime_aft = np.mean(hypernets_ds_aft.acquisition_time.values)
    hyp_wav_aft = hypernets_ds_aft.wavelength.values
    hyp_refl_aft = np.mean(hypernets_ds_aft.reflectance.values, axis=1)
    hyp_std_aft = np.std(hypernets_ds_aft.reflectance.values, axis=1)
    u_rand_aft = ((
            (np.mean(hypernets_ds_aft.u_rel_random_reflectance.values, axis=1)
            * 0.01
            * hyp_refl_aft)**2
            + hyp_std_aft**2)**0.5
            / np.sqrt(3))
    u_syst_aft = (
            np.mean(hypernets_ds_aft.u_rel_systematic_reflectance.values, axis=1)
            * 0.01
            * hyp_refl_aft
    )
    u_hyp_refl_aft = np.sqrt(u_rand_aft ** 2 + u_syst_aft ** 2)
    cov_hyp_refl_aft = cm.convert_corr_to_cov(np.eye(len(u_rand_aft)), u_rand_aft) + cm.convert_corr_to_cov(
        hypernets_ds_aft.err_corr_systematic_reflectance.values, u_syst_aft)
    corr_hyp_refl_aft = cm.convert_cov_to_corr(cov_hyp_refl_aft, u_hyp_refl_aft)
    # plt.plot(rcn_wav,rcn_refl,"b")
    # plt.plot(hyp_wav_aft,hyp_refl_aft,"r")
    # plt.plot(hyp_wav_aft,hyp_refl_aft,"g")
    # plt.show()


    asd_corrected = np.loadtxt(asd_path, dtype='str', delimiter='\t')
    asd_wvslice = asd_corrected[1:2151,0]
    asd_wavs = asd_wvslice.astype(float)
    asd_reflslice = asd_corrected[1:2151,1:88]
    asd_refl_full = asd_reflslice.astype(float)
    asd_refl = np.average(asd_refl_full, axis=1)
    asd_stdv = np.nanstd(asd_refl_full, axis=1)
    u_asd_refl = asd_stdv/np.sqrt(asd_refl_full.shape[1])
    # visual check of asd data
    # plt.plot(asd_wavs,asd_refl_full)
    # #plt.fill_between(asd_wavs, asd_refl_ - asd_stdv, asd_refl + asd_stdv,
    #                  #alpha=0.3, label='ASD Std Dev')
    # plt.title('All ASD Data GHNA March 2020 (WR Corrected)', fontsize=20)
    # plt.xlabel('Wavelengths (nm)', fontsize=20)
    # plt.ylabel('Reflectances', fontsize=20)
    # plt.grid()
    # plt.xlim(350,2500)
    # plt.legend()
    # plt.show()
    #plt.plot(asd_wavs, asd_stdv)
    #plt.show()

    rcn_refl_pre = conv.spectral_processing(rcn_wav,hyp_wav_pre,hyp_refl_pre,asd_wavs,asd_refl)
    u_rcn_refl_pre, corr_rcn_refl_pre = prop.propagate_standard(conv.spectral_processing,[rcn_wav,hyp_wav_aft,hyp_refl_pre,asd_wavs,asd_refl],[None,None,u_hyp_refl_pre,None,u_asd_refl],corr_x=[None,None,corr_hyp_refl_pre,None,"rand"],return_corr=True)
    rcn_refl_aft = conv.spectral_processing(rcn_wav,hyp_wav_aft,hyp_refl_aft,asd_wavs,asd_refl)
    u_rcn_refl_aft, corr_rcn_refl_aft = prop.propagate_standard(conv.spectral_processing,[rcn_wav,hyp_wav_aft,hyp_refl_aft,asd_wavs,asd_refl],[None,None,u_hyp_refl_aft,None,u_asd_refl],corr_x=[None,None,corr_hyp_refl_aft,None,"rand"],return_corr=True)

    rcn_refl_interpolated = conv.time_interpolation(hypernets_datetime_pre, rcn_refl_pre, hypernets_datetime_aft, rcn_refl_aft, rcn_datetime)#provide the times and hypernets reflectances
    u_rcn_refl_interpolated = prop.propagate_standard(conv.time_interpolation,[hypernets_datetime_pre, rcn_refl_pre, hypernets_datetime_aft, rcn_refl_aft, rcn_datetime],[None, u_rcn_refl_pre, None, u_rcn_refl_aft, None], corr_x=[None, corr_rcn_refl_pre, None, corr_rcn_refl_aft, None], return_corr=False)

    plt.plot(rcn_wav, rcn_refl, label='GONA RadCalNet')
    plt.plot(asd_wavs, asd_refl, label='ASD')
    # plt.plot(hyp_wav_pre, hyp_refl_pre, label = 'HYPERNETS Pre')
    # plt.plot(hyp_wav_aft, hyp_refl_aft, label='HYPERNETS After')
    plt.plot(rcn_wav, rcn_refl_interpolated, label='GHNA Interpolated')
    plt.xlabel('Wavelengths (nm)', fontsize=18)
    plt.ylabel('Reflectances', fontsize=18)
    plt.title('Dataset Comparison', fontsize=20)
    plt.grid()
    plt.legend()
    plt.savefig(os.path.join(output_path, "plots", 'comparison_%s.png' % (datetime.fromtimestamp(rcn_datetime).strftime("%Y%m%dT%H%M%S"))))
    plt.clf()

    plt.plot(rcn_wav, (rcn_refl_interpolated-rcn_refl)/rcn_refl*100, label='(GHNA-GONA)/GONA')
    plt.xlabel('Wavelengths (nm)', fontsize=18)
    plt.ylabel('relative difference (%)', fontsize=18)
    plt.grid()
    plt.legend()
    plt.savefig(os.path.join(output_path, "plots", 'comparison_%s_reldiff.png' % (datetime.fromtimestamp(rcn_datetime).strftime("%Y%m%dT%H%M%S"))))
    plt.clf()

    return rcn_refl_interpolated, u_rcn_refl_interpolated, rcn_wav

def main(start_date, end_date):
    matchups=identify_matchups("GHNA", "GONA_alldata_list_230124.txt", start_date, end_date)

    matchups = filter_matchups(matchups, 30)

    with open(os.path.join(output_path,"matchups.txt"), 'w') as f:
        f.write("# radcalnet_name hypernets_name_before hypernets_name_after timediff_before, timediff_after \n")
        for i in range(len(matchups)):
            f.write("%s %s %s %s %s \n"%(matchups[i,0][0],matchups[i,1][0],matchups[i,2][0],matchups[i,3],matchups[i,4]))

    output_files = []
    rcn_times = []
    rcn_files = []
    rcn_doy_l = []
    rcn_local_time = []
    rcn_p = []
    rcn_t = []
    rcn_h2o = []
    rcn_o3 = []
    rcn_aod = []
    rcn_ang = []
    rcn_type = []

    rcn_u_p = []
    rcn_u_t = []
    rcn_u_h2o = []
    rcn_u_o3 = []
    rcn_u_aod = []
    rcn_u_ang = []


    for i in range(len(matchups)):
        rcn_files.append(matchups[i, 0][0])
        rcn_times.append(matchups[i, 0][1])
        rcn_doy_l.append(matchups[i, 0][5])
        rcn_p.append(matchups[i, 0][7])
        rcn_t.append(matchups[i, 0][8])
        rcn_h2o.append(matchups[i, 0][9])
        rcn_o3.append(matchups[i, 0][10])
        rcn_aod.append(matchups[i, 0][11])
        rcn_ang.append(matchups[i, 0][12])
        rcn_type.append(matchups[i,0][13])

        rcn_u_p.append(matchups[i,0][14])
        rcn_u_t.append(matchups[i, 0][15])
        rcn_u_h2o.append(matchups[i, 0][16])
        rcn_u_o3.append(matchups[i, 0][17])
        rcn_u_aod.append(matchups[i, 0][18])
        rcn_u_ang.append(matchups[i, 0][19])
        if matchups[i,0][0] not in output_files:
            output_files.append(matchups[i,0][0])
    print(output_files)

    rcn_files = np.array(rcn_files)
    rcn_times = np.array(rcn_times)
    rcn_local_time = np.array(rcn_local_time)
    rcn_doy_l = np.array(rcn_doy_l)
    rcn_p = np.array(rcn_p)
    rcn_t = np.array(rcn_t)
    rcn_h2o = np.array(rcn_h2o)
    rcn_o3 = np.array(rcn_o3)
    rcn_aod = np.array(rcn_aod)
    rcn_ang = np.array(rcn_ang)
    rcn_type = np.array(rcn_type)

    rcn_u_p = np.array(rcn_u_p)
    rcn_u_t = np.array(rcn_u_t)
    rcn_u_h2o = np.array(rcn_u_h2o)
    rcn_u_o3 = np.array(rcn_u_o3)
    rcn_u_aod = np.array(rcn_u_aod)
    rcn_u_ang = np.array(rcn_u_ang)

    times_UTC=["08:00","08:30","09:00","09:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00"]

    for ii in range(0,len(output_files)):
        print(np.where(rcn_files==output_files[ii])[0])
        output_refl_day = np.empty(len(rcn_files[np.where(rcn_files==output_files[ii])[0]]), dtype=object)
        output_u_refl_day = np.empty(len(rcn_files[np.where(rcn_files==output_files[ii])[0]]), dtype=object)
        output_doy_l = rcn_doy_l[np.where(rcn_files == output_files[ii])[0]]
        output_times_day = rcn_times[np.where(rcn_files==output_files[ii])[0]]
        output_p_day = rcn_p[np.where(rcn_files == output_files[ii])[0]]
        output_t_day = rcn_t[np.where(rcn_files == output_files[ii])[0]]
        output_h2o_day = rcn_h2o[np.where(rcn_files == output_files[ii])[0]]
        output_o3_day = rcn_o3[np.where(rcn_files == output_files[ii])[0]]
        output_aod_day = rcn_aod[np.where(rcn_files == output_files[ii])[0]]
        output_ang_day = rcn_ang[np.where(rcn_files == output_files[ii])[0]]
        output_type_day = rcn_type[np.where(rcn_files == output_files[ii])[0]]

        output_u_p_day = rcn_u_p[np.where(rcn_files == output_files[ii])[0]]
        output_u_t_day = rcn_u_t[np.where(rcn_files == output_files[ii])[0]]
        output_u_h2o_day = rcn_u_h2o[np.where(rcn_files == output_files[ii])[0]]
        output_u_o3_day = rcn_u_o3[np.where(rcn_files == output_files[ii])[0]]
        output_u_aod_day = rcn_u_aod[np.where(rcn_files == output_files[ii])[0]]
        output_u_ang_day = rcn_u_ang[np.where(rcn_files == output_files[ii])[0]]

        print(output_refl_day.shape, output_times_day, output_t_day, output_h2o_day, output_o3_day, output_aod_day, output_ang_day, output_type_day)

        for iii in range(len(output_refl_day)):
            for i in range(len(matchups)):
                if matchups[i, 0][0]==output_files[ii] and matchups[i,0][1]==output_times_day[iii]:
                    output_refl_day[iii],output_u_refl_day[iii],rcn_wav = process_matchup(matchups[i])
        print(output_refl_day)

        with open(os.path.join(output_path, output_files[ii].replace('GONA01', 'GHNA01')), 'w') as f:
            f.write("Site:\tGHNA01\n")
            f.write("Lat:\t-23.60153\n")
            f.write("Lon:\t15.12589\n")
            f.write("Alt:\t510.0\n\n")

            f.write("Year:")
            for iv in range(len(times_UTC)):
                f.write("\t%s" % output_times_day[0].strftime("%Y"))
            f.write("\n")

            f.write("DOY(U):")
            for iv in range(len(times_UTC)):
                f.write("\t%s" % output_times_day[0].strftime("%j"))
            f.write("\n")

            f.write("UTC:")
            for iv in range(len(times_UTC)):
                f.write("\t%s"%times_UTC[iv])
            f.write("\n")

            f.write("DOY(L):")
            for iv in range(len(times_UTC)):
                f.write("\t%s" % output_times_day[0].strftime("%j"))
            f.write("\n")

            f.write("Local:")
            for iv in range(len(times_UTC)):
                time_local = datetime.strptime(times_UTC[iv], "%H:%M")
                time_local_corrected = time_local + timedelta(hours=1)
                f.write("\t%s"%time_local_corrected.strftime("%H:%M"))
            f.write("\n")

            f.write("P:")
            for iv in range(len(times_UTC)):
                time_present=False
                for iii in range(len(output_refl_day)):
                    if times_UTC[iv]==output_times_day[iii].strftime("%H:%M"):
                        time_present = True
                        f.write("\t%.2f" % output_p_day[iii])
                if not time_present:
                    f.write("\t9999")
            f.write("\n")

            f.write("T:")
            for iv in range(len(times_UTC)):
                time_present=False
                for iii in range(len(output_refl_day)):
                    if times_UTC[iv]==output_times_day[iii].strftime("%H:%M"):
                        time_present = True
                        f.write("\t%.1f" % output_t_day[iii])
                if not time_present:
                    f.write("\t9999")
            f.write("\n")

            f.write("WV:")
            for iv in range(len(times_UTC)):
                time_present=False
                for iii in range(len(output_refl_day)):
                    if times_UTC[iv]==output_times_day[iii].strftime("%H:%M"):
                        time_present = True
                        f.write("\t%.2f" % output_h2o_day[iii])
                if not time_present:
                    f.write("\t9999")
            f.write("\n")

            f.write("O3:")
            for iv in range(len(times_UTC)):
                time_present=False
                for iii in range(len(output_refl_day)):
                    if times_UTC[iv]==output_times_day[iii].strftime("%H:%M"):
                        time_present = True
                        f.write("\t%.2f" % output_o3_day[iii])
                if not time_present:
                    f.write("\t9999")
            f.write("\n")

            f.write("AOD:")
            for iv in range(len(times_UTC)):
                time_present=False
                for iii in range(len(output_refl_day)):
                    if times_UTC[iv]==output_times_day[iii].strftime("%H:%M"):
                        time_present = True
                        f.write("\t%.3f" % output_aod_day[iii])
                if not time_present:
                    f.write("\t9999")
            f.write("\n")

            f.write("Ang:")
            for iv in range(len(times_UTC)):
                time_present=False
                for iii in range(len(output_refl_day)):
                    if times_UTC[iv]==output_times_day[iii].strftime("%H:%M"):
                        time_present = True
                        f.write("\t%.3f" % output_ang_day[iii])
                if not time_present:
                    f.write("\t9999")
            f.write("\n")

            f.write("Type:")
            for iv in range(len(times_UTC)):
                time_present=False
                for iii in range(len(output_refl_day)):
                    if times_UTC[iv]==output_times_day[iii].strftime("%H:%M"):
                        time_present = True
                        f.write("\t%s" % output_type_day[iii])
                if not time_present:
                    f.write("\tR")
            f.write("\n")

            for iw in range(len(rcn_wav)):
                f.write("%d"%(rcn_wav[iw]))
                for iv in range(len(times_UTC)):
                    time_present=False
                    for iii in range(len(output_refl_day)):
                        if times_UTC[iv]==output_times_day[iii].strftime("%H:%M"):
                            time_present = True
                            f.write("\t%.4f" % (output_refl_day[iii][iw]))
                    if not time_present:
                        f.write("\t9999")
                f.write("\n")

            f.write("\n")

            f.write("P:")
            for iv in range(len(times_UTC)):
                time_present=False
                for iii in range(len(output_refl_day)):
                    if times_UTC[iv]==output_times_day[iii].strftime("%H:%M"):
                        time_present = True
                        f.write("\t%.2f" % output_u_p_day[iii])
                if not time_present:
                    f.write("\t9999")
            f.write("\n")

            f.write("T:")
            for iv in range(len(times_UTC)):
                time_present=False
                for iii in range(len(output_refl_day)):
                    if times_UTC[iv]==output_times_day[iii].strftime("%H:%M"):
                        time_present = True
                        f.write("\t%.2f" % output_u_t_day[iii])
                if not time_present:
                    f.write("\t9999")
            f.write("\n")

            f.write("WV:")
            for iv in range(len(times_UTC)):
                time_present=False
                for iii in range(len(output_refl_day)):
                    if times_UTC[iv]==output_times_day[iii].strftime("%H:%M"):
                        time_present = True
                        f.write("\t%.2f" % output_u_h2o_day[iii])
                if not time_present:
                    f.write("\t9999")
            f.write("\n")

            f.write("O3:")
            for iv in range(len(times_UTC)):
                time_present=False
                for iii in range(len(output_refl_day)):
                    if times_UTC[iv]==output_times_day[iii].strftime("%H:%M"):
                        time_present = True
                        f.write("\t%.2f" % output_u_o3_day[iii])
                if not time_present:
                    f.write("\t9999")
            f.write("\n")

            f.write("AOD:")
            for iv in range(len(times_UTC)):
                time_present=False
                for iii in range(len(output_refl_day)):
                    if times_UTC[iv]==output_times_day[iii].strftime("%H:%M"):
                        time_present = True
                        f.write("\t%.3f" % output_u_aod_day[iii])
                if not time_present:
                    f.write("\t9999")
            f.write("\n")

            f.write("Ang:")
            for iv in range(len(times_UTC)):
                time_present=False
                for iii in range(len(output_refl_day)):
                    if times_UTC[iv]==output_times_day[iii].strftime("%H:%M"):
                        time_present = True
                        f.write("\t%.3f" % output_u_ang_day[iii])
                if not time_present:
                    f.write("\t9999")
            f.write("\n")

            for iw in range(len(rcn_wav)):
                f.write("%d"%(rcn_wav[iw]))
                for iv in range(len(times_UTC)):
                    time_present=False
                    for iii in range(len(output_refl_day)):
                        if times_UTC[iv]==output_times_day[iii].strftime("%H:%M"):
                            time_present = True
                            f.write("\t%.4f" % (output_u_refl_day[iii][iw]))
                    if not time_present:
                        f.write("\t9999")
                if not iw==(len(rcn_wav)-1):
                    f.write("\n")

if __name__ == "__main__":
    main("2022-05-17", "2023-11-08")
