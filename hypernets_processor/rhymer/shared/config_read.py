## QV 2019-07-04
def config_read(file):
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
    return (settings)
