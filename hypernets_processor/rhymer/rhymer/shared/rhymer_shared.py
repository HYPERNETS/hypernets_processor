class RhymerShared:

    def __init__(self, context):
        self.context = context

    def closest_idx(self, xlist, xval):
        print(xlist)
        print(xval)
        idx, xret = min(enumerate(xlist), key=lambda x: abs(float(x[1]) - float(xval)))
        return (idx, xret)

    ## QV 2019-07-04
    def config_read(self, file):
        settings = {}
        with open(file, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip()
                if len(line) == 0: continue
                if line[0] in ['%', '#', ';']: continue
                if "=" not in line: continue
                sp = [s.strip() for s in line.split('=')]
                v = [s.strip() for s in sp[1].split(',')]
                try:
                    v = [float(s) for s in v]
                except:
                    try:
                        v = [eval(s.capitalize()) for s in v]
                    except:
                        pass
                if len(v) == 1: v = v[0]
                settings[sp[0]] = v
        return settings

    ## def lutpos
    ## finds position of value in a (sorted) vector for LUT lookup
    ## written by Quinten Vanhellemont, RBINS for the PONDER project
    ## 2016-07-05
    ## modifications:

    def lutpos(self, vector, value):
        import numpy as np
        uidx = np.searchsorted(vector, value, side='right')
        uidx = max(0, uidx)
        uidx = min(uidx, len(vector) - 1)
        uvalue = vector[uidx]

        if uvalue > value:
            lidx = uidx - 1
            index = lidx + (value - (vector[lidx])) / abs(vector[lidx] - vector[uidx])
            bracket = (lidx, uidx)
            return index, bracket
        if uvalue <= value:
            lidx = uidx
            uidx = uidx
            index = float(lidx)
            bracket = (lidx, uidx)
            return index, bracket

        return 0, (0, 0)

    ## def interp3d
    ## interpolates 3D array for LUT lookup
    ## written by Quinten Vanhellemont, RBINS for the PONDER project
    ## 2016-07-05
    ## modifications:
    ## 2020-09-11 : CG changed the xbr ybr and zbr max value???

    def interp3d(self, data, xid, yid, zid):
        dim = data.shape
        # xbr = (int(xid), min(int(xid + 1), dim[0]))
        # ybr = (int(yid), min(int(yid + 1), dim[0]))
        # zbr = (int(zid), min(int(zid + 1), dim[0]))
        # # modified by CG - to be verified with QV
        xbr = (int(xid), min(int(xid + 1), int(dim[0]-1)))
        ybr = (int(yid), min(int(yid + 1), int(dim[1]-1)))
        zbr = (int(zid), min(int(zid + 1), int(dim[2]-1)))

        x = xid - xbr[0]
        y = yid - ybr[0]
        z = zid - zbr[0]

        d000 = data[xbr[0], ybr[0], zbr[0]]
        d100 = data[xbr[1], ybr[0], zbr[0]]
        d010 = data[xbr[0], ybr[1], zbr[0]]
        d001 = data[xbr[0], ybr[0], zbr[1]]
        d101 = data[xbr[1], ybr[0], zbr[1]]
        d011 = data[xbr[0], ybr[1], zbr[1]]
        d110 = data[xbr[1], ybr[1], zbr[0]]
        d111 = data[xbr[1], ybr[1], zbr[1]]

        return d000 * (1 - x) * (1 - y) * (1 - z) + d100 * x * (1 - y) * (1 - z) + d010 * (1 - x) * y * (
                    1 - z) + d001 * (
                       1 - x) * (1 - y) * z + d101 * x * (1 - y) * z + d011 * (1 - x) * y * z + d110 * x * y * (
                       1 - z) + d111 * x * y * z

    ## def download_file
    ## download_file with authorisation option
    ## written by Quinten Vanhellemont, RBINS for the PONDER project
    ## 2018-03-14
    ## modifications: 2018-11-19 (QV) added verbosity option, removed the parallel download

    def download_file(self, url, file, auth=None, session=None, parallel=False, verbosity=0):
        import requests
        import time

        import os
        file_path = os.path.abspath(file)
        start = time.time()

        r = requests.get(url, stream=True, auth=auth)

        if (r.ok):
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
        else:
            if verbosity > 2: print(r.text)
            raise Exception("File download failed")

        if verbosity > 1:
            print("Downloaded {}, elapsed Time: {:.1f}s".format(url, time.time() - start))
