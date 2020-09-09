## parse PANTHYR measurement cycle
## i.e. count e and l measurements for each azimuth in the cycle
## zenith angle is used to differentiate Lsky and Lu
## QV July 2018
## Last modifications: 2019-07-10 (QV) renamed from PANTR, added .lower() to sensor ID as it is in some cases uppercase in the current deployment (RBINS ROOF)
from configparser import ConfigParser
from datetime import datetime
from hypernets_processor.data_io.hypernets_reader import read_hypernets_data

class CycleParse:

    def read_protocol(self, settings_file):
        defset = ConfigParser()
        defset.read(settings_file)
        protocol = dict(defset['MEASPROTOCOL'])['protocol']
        valheader = dict(defset['MEASPROTOCOL'])['valheader']
        valheader = valheader.split(',')
        nbrlu = dict(defset['MEASPROTOCOL'])['nbrlu']
        nbrlsky = dict(defset['MEASPROTOCOL'])['nbrlsky']
        nbred = dict(defset['MEASPROTOCOL'])['nbred']
        return protocol, valheader,nbrlu, nbrlsky, nbred

    def perform_checks(self, ds_rad, ds_irr, settings_file, verbosity=0, qf=10):

        print(settings_file)
        protocol, valheader = self.read_protocol(settings_file)

        if protocol != 'water_std':
            # here we should simply provide surface reflectance?
            # what about a non-standard protocol but that includes the required standard series?
            print('Unknown measurement protocol: {}'.format(protocol))
        else:
            selrad = []
            for a in ds_rad['radiance'].transpose("scan", "wavelength"):
                sena = ds_rad["viewing_azimuth_angle"].values
                senz = ds_rad["viewing_zenith_angle"].values
                ts = datetime.utcfromtimestamp(ds_rad['acquisition_time'].values)
                # not fromtimestamp?

                if ds_rad['quality_flag'].values[int(a.scan) - 1] < qf:
                    if (senz != 'NULL') & (sena != 'NULL'):
                        senz = float(senz)
                        sena = abs(float(sena))
                        selrad.append(int(a.scan))
                    else:
                        if verbosity > 2: print('NULL angles: Aquisition time {}, {}'.format(ts, ', '.join(
                            ['{}:{}'.format(k, scani[k].values) for k in ['scan', 'quality_flag']])))
                else:
                    if verbosity > 2: print('Quality flag {} : Aquisition time {}, {}'.format(ds_rad['quality_flag'].values[int(a.scan) - 1], ts, ', '.join(
                        ['{}:{}'.format(k, scani[k].values) for k in ['scan', 'quality_flag']])))

            if verbosity > 2: print('Number of valid radiance scan: {}'.format(len(selrad)))
            

            selirr = []
            for a in ds_irr['irradiance'].transpose("scan", "wavelength"):
                if ds_irr['quality_flag'].values[int(a.scan) - 1] < qf:
                    selirr.append(int(a.scan))
            if verbosity > 2: print('Number of valid irradiance measurements: {}'.format(len(selirr)))

            print(selirr)
        return (ds_rad.sel(scan=selrad), ds_irr.sel(scan=selirr))

    def cycleparse(self, rad, irr, settings_file, verbosity=0):

        # check which cycle we have and see if we have the required cycle
        print(settings_file)
        protocol, valheader,nbrlu, nbrlsky, nbred = self.read_protocol(settings_file)

        if protocol != 'water_std':
            # here we should simply provide surface reflectance?
            # what about a non-standard protocol but that includes the required standard series?
            print('Unknown measurement protocol: {}'.format(protocol))
        else:
            # check if correct number of radiance and irradiance data
             for i in rad['scan']:
                scani = rad.sel(scan=i)
                sena = scani["viewing_azimuth_angle"].values
                senz = scani["viewing_zenith_angle"].values
                ts = datetime.utcfromtimestamp(scani['acquisition_time'].values)
                # not fromtimestamp?

                if (senz != 'NULL') & (sena != 'NULL'):
                    senz = float(senz)
                    sena = abs(float(sena))
                else:
                    if verbosity > 2: print('NULL angles: Aquisition time {}, {}'.format(ts, ', '.join(
                        ['{}:{}'.format(k, scani[k].values) for k in ['scan', 'quality_flag']])))
                    continue

                # ## identify measurement
                measurement = None
                ## radiance
                if senz < 90: measurement = 'lu'
                if senz >= 90: measurement = 'lsky'
                if measurement is None: continue

                # ## check if we are in the same azimuth
                # ## Not sure why this is relevant -> Ask Quinten???
                # if cur_azimuth is not None:
                #     if cur_azimuth != sena:
                #         cur_data[cur_azimuth] = cur_sub_cycle
                #         cur_azimuth = None

                # ## change of azimuth
                # if cur_azimuth is None:
                #     cur_cycle_order = 'None'  # 'None'
                #     cycle_order = ['ed_before', 'lsky_before', 'lu', 'lsky_after', 'ed_after']
                #     cur_azimuth = sena
                #     cur_sub_cycle = {co: [] for co in cycle_order}

                # ## get sensor type
                # sensor = i[key_sensor].lower()
                # if sensor not in ['e', 'l']: continue
                #
                # ## get serial
                # sensor_id = i['rep_serial']
                #




                #
                # ## irradiance
                # if (sensor == 'e'):
                #     if senz == 180: measurement = 'ed'


                ## check where we are in the cycle_order
                if len(cycle_order) > 0:
                    if measurement not in cur_cycle_order:
                        if measurement in cycle_order[0]:
                            cur_cycle_order = cycle_order[0]
                            del cycle_order[0]

                if cur_cycle_order in cur_sub_cycle:
                    ## get values
                    values = [i[v] for v in valheader]

                    cur_sub_cycle[cur_cycle_order].append({'dev': sensor_id, 'data': [int(v) for v in values], 'record': i})

            if cur_azimuth is not None:
                # print(cur_azimuth)
                # for k in cur_sub_cycle:
                #    print(k, len(cur_sub_cycle[k]))
                cur_data[cur_azimuth] = cur_sub_cycle
                cur_azimuth = None

        return (cur_data)
