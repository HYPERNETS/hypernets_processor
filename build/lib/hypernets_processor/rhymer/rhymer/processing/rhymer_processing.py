from hypernets_processor.rhymer.rhymer.shared.rhymer_shared import RhymerShared
from hypernets_processor.rhymer.rhymer.ancillary.rhymer_ancillary import RhymerAncillary
import numpy as np
import os

## interpolate Mobley sky reflectance LUT
## ths is sun zenith angle
## thv is viewing angle
## phi is photon travel angle with sun at 0°, phi = 180 - relative azimuth
## QV 2018-07-18
## Last modifications: QV 2018-08-02 added abs to phi lutpos
##                     QV 2019-07-10 integrated in rhymer
class RhymerProcessing:

    def __init__(self, context):
        self.context = context
        self.rhymeranc = RhymerAncillary(context)
        self.rhymershared=RhymerShared(context)
        self.dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        #self.path_ascii = os.path.join(dir_path, 'data', 'calibration_files_ascii', 'HYPSTAR_cal')

    def mobley_lut_interp(self, ths, thv, phi, wind=2.):
        rholut = self.mobley_lut_read()
        dval = rholut['header']

        # find wind speeds
        wind_id, wind_br = self.rhymershared.lutpos(dval['Wind'], wind)
        wind_w = wind_id - wind_br[0]

        # find geometry
        ths_id, ths_br = self.rhymershared.lutpos(dval['Theta-sun'], ths)
        thv_id, thv_br = self.rhymershared.lutpos(dval['Theta'], thv)
        phi_id, phi_br = self.rhymershared.lutpos(dval['Phi'], abs(phi))

        ## interpolate for both bracketing wind speeds
        it1 = self.rhymershared.interp3d(rholut['data'][wind_br[0], :, :, :], ths_id, thv_id, phi_id)
        it2 = self.rhymershared.interp3d(rholut['data'][wind_br[1], :, :, :], ths_id, thv_id, phi_id)

        ## and weigh to wind speed
        rint = it2 * wind_w + it1 * (1. - wind_w)
        return (rint)

    ## read Mobley sky reflectance LUT
    ## QV 2018-07-18
    ## Last modifications: 2019-07-10 (QV) integrated in rhymer

    def mobley_lut_read(self):
        vf = self.context.get_config_value("rholut")
        ifile = '{}/{}'.format(self.dir_path, '../rhymer/data/Shared/Mobley/{}.txt'.format(vf))

        header = '   I   J    Theta      Phi  Phi-view       rho'.split()
        data, cur = {}, None

        with open(ifile, 'r') as f:
            for li, line in enumerate(f.readlines()):
                line = line.strip()

                if 'rho for' in line:
                    sp = line.split()
                    ws = [sp[v] for v in range(1, len(sp) - 1) if (sp[v - 2] == 'SPEED') & (sp[v + 1] == 'm/s')]
                    ws = float(ws[0])
                    ths = [sp[v] for v in range(1, len(sp) - 1) if (sp[v - 2] == 'THETA_SUN') & (sp[v + 1] == 'deg')]
                    ths = float(ths[0])
                    cur = {'ws': ws, 'ths': ths}
                else:
                    if cur is None: continue

                    if cur['ws'] not in data:
                        data[cur['ws']] = {}

                    if cur['ths'] not in data[cur['ws']]:
                        data[cur['ws']][cur['ths']] = {h: [] for h in header}

                    sp = [float(v) for v in line.split()]
                    for ih, h in enumerate(header):
                        data[cur['ws']][cur['ths']][h].append(sp[ih])

        ## set up dimensions
        dval = {'Wind': list(data.keys())}
        dval['Theta-sun'] = list(data[dval['Wind'][0]])

        dim = [len(dval['Wind']), len(dval['Theta-sun'])]
        skip = ['I', 'J', 'Phi-view', 'rho']
        for k in data[dval['Wind'][0]][dval['Theta-sun'][0]].keys():
            if k in skip: continue
            tmp = data[dval['Wind'][0]][dval['Theta-sun'][0]][k]
            dval[k] = list(set(tmp))
            dval[k].sort()
            dim += [len(dval[k])]

        ## generate LUT array
        rholut = np.zeros(dim)
        for wi, wv in enumerate(dval['Wind']):
            for szi, sza in enumerate(dval['Theta-sun']):
                cd = data[wv][sza]
                for vzi, vza in enumerate(dval['Theta']):
                    for vai, vaa in enumerate(dval['Phi']):
                        if vzi == 0:
                            idx = 0
                        else:
                            idx = 1 + (vzi - 1) * (len(dval['Phi'])) + vai
                        rholut[wi, szi, vzi, vai] = cd['rho'][idx]
        return ({'header': dval, 'data': rholut})

    ## def similarity_read
    ## reads similarity spectrum
    ## written by Quinten Vanhellemont, RBINS for the PONDER project
    ## 2017-12
    ## modifications: 2018-04-17 (QV) added to acolite function
    ##                2019-07-10 (QV) integrated in rhymer

    def similarity_read(self, ifile=None):

        if ifile is None:
            ifile = '{}/Shared/REMSEM/similarityspectrumtable.txt'.format(self.context.get_config_value("rhymer_data_dir"))

        ss_data = {'wave': np.ndarray(0), 'ave': np.ndarray(0), 'std': np.ndarray(0), 'cv': np.ndarray(0)}

        with open(ifile, 'r') as f:
            for i, line in enumerate(f.readlines()):
                line = line.strip()
                sp = line.split()
                if i == 0:
                    continue
                else:
                    j = 0
                    while j < len(sp):
                        ss_data['wave'] = np.append(ss_data['wave'], float(sp[j]) / 1000.)
                        ss_data['ave'] = np.append(ss_data['ave'], float(sp[j + 1]))
                        ss_data['std'] = np.append(ss_data['std'], float(sp[j + 2]))
                        ss_data['cv'] = np.append(ss_data['cv'], float(sp[j + 3]))
                        j += 4

        ## sort indices
        idx = np.argsort(ss_data['wave'])
        for k in ss_data.keys(): ss_data[k] = ss_data[k][idx]
        return (ss_data)
