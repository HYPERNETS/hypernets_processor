## read Mobley sky reflectance LUT
## QV 2018-07-18
## Last modifications: 2019-07-10 (QV) integrated in rhymer

def mobley_lut_read(ifile=None, version='M1999'):
    import numpy as np

    if ifile is None:
        import rhymer as ry
        if version == 'M1999':
            vf = 'rhoTable_AO1999'
        ifile = '{}/{}'.format(ry.config['data_dir'], 'Shared/Mobley/{}.txt'.format(vf))

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
