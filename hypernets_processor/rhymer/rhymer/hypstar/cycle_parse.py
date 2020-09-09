## parse PANTHYR measurement cycle
## i.e. count e and l measurements for each azimuth in the cycle
## zenith angle is used to differentiate Lsky and Lu
## QV July 2018
## Last modifications: 2019-07-10 (QV) renamed from PANTR, added .lower() to sensor ID as it is in some cases uppercase in the current deployment (RBINS ROOF)
from configparser import ConfigParser


class CycleParse:

    def read_protocol(self, settings_file):
        defset = ConfigParser()
        defset.read(settings_file)
        protocol = dict(defset['MEASPROTOCOL'])['protocol']
        valheader=dict(defset['MEASPROTOCOL'])['valheader']
        valheader=valheader.split(',')
        return protocol, valheader

    def perform_checks(self, ds_rad, ds_irr, settings_file, verbosity=0, qf=1):

        print(settings_file)
        protocol, valheader = self.read_protocol(settings_file)

        if protocol != 'water_std':
            # here we should simply provide surface reflectance?
            # what about a non-standard protocol but that includes the required standard series?
            print('Unknown measurement protocol: {}'.format(protocol))
        else:
            selrad = []
            for a in ds_rad['radiance'].transpose("scan", "wavelength"):
                if ds_rad['quality_flag'].values[int(a.scan) - 1] < 10:
                    selrad.append(int(a.scan))

            if verbosity > 2: print('Number of valid radiance scan: {}'.format(len(selrad)))

            selirr=[]
            for a in ds_irr['irradiance'].transpose("scan", "wavelength"):
                if ds_irr['quality_flag'].values[int(a.scan) - 1] < 10:
                    selirr.append(int(a.scan))
            if verbosity > 2: print('Number of invalid irradiance measurements: {}'.format(len(selrad)))

            print(selirr)
        return(ds_rad.sel(scan=selrad), ds_irr.sel(scan=selirr))

    # def read_viewing_angles(self, radiance, settings_file, verbosity=0):
    #
    #
    #
    #
    #     for i in cur_cycle_data:
    #         ## skip invalids
    #         if i['valid'] == 'n':
    #             if verbosity > 2: print('Invalid measurement: {}'.format(
    #                 ', '.join(['{}:{}'.format(k, i[k]) for =k in ['id', 'timestamp', 'valid']])))
    #
    #             continue
    #
    #         # print(i['id'])
    #         # print(i['timestamp'])
    #
    #         ## get sensor orientation
    #         senz = i[key_senz]
    #         sena = i[key_sena]
    #
    #         if (senz != 'NULL') & (sena != 'NULL'):
    #             senz = float(senz)
    #             sena = abs(float(sena))
    #         else:
    #             if verbosity > 2: print(
    #                 'NULL angles: {}'.format(', '.join(['{}:{}'.format(k, i[k]) for k in ['id', 'timestamp', 'valid']])))
    #             continue
    #
    #         ## check if we are in the same azimuth
    #         if cur_azimuth is not None:
    #             if cur_azimuth != sena:
    #                 cur_data[cur_azimuth] = cur_sub_cycle
    #                 cur_azimuth = None
    #
    #         ## change of azimuth
    #         if cur_azimuth is None:
    #             cur_cycle_order = 'None'  # 'None'
    #             cycle_order = ['ed_before', 'lsky_before', 'lu', 'lsky_after', 'ed_after']
    #             cur_azimuth = sena
    #             cur_sub_cycle = {co: [] for co in cycle_order}
    #
    #         ## get sensor type
    #         sensor = i[key_sensor].lower()
    #         if sensor not in ['e', 'l']: continue
    #
    #         ## get serial
    #         sensor_id = i['rep_serial']
    #
    #         ## identify measurement
    #         measurement = None
    #
    #         ## irradiance
    #         if (sensor == 'e'):
    #             if senz == 180: measurement = 'ed'
    #
    #         ## radiance
    #         if (sensor == 'l'):
    #             if senz < 90: measurement = 'lu'
    #             if senz >= 90: measurement = 'lsky'
    #         if measurement is None: continue
    #
    #         ## check where we are in the cycle_order
    #         if len(cycle_order) > 0:
    #             if measurement not in cur_cycle_order:
    #                 if measurement in cycle_order[0]:
    #                     cur_cycle_order = cycle_order[0]
    #                     del cycle_order[0]
    #
    #         if cur_cycle_order in cur_sub_cycle:
    #             ## get values
    #             values = [i[v] for v in valheader]
    #
    #             cur_sub_cycle[cur_cycle_order].append({'dev': sensor_id, 'data': [int(v) for v in values], 'record': i})
    #
    #     if cur_azimuth is not None:
    #         # print(cur_azimuth)
    #         # for k in cur_sub_cycle:
    #         #    print(k, len(cur_sub_cycle[k]))
    #         cur_data[cur_azimuth] = cur_sub_cycle
    #         cur_azimuth = None
    #
    #     return (cur_data)
