## reads default settings and updates with provided settings file
## QV 2019-07-10

def settings_read(settings_file=None, defaults='defaults_panthyr'):
    import os
    import rhymer as ry

    if os.path.exists(defaults):
        defaults_file = '{}'.format(defaults)
    else:
        defaults_file = '{}/{}/{}.txt'.format(ry.config['data_dir'], 'Settings', defaults)
    settings = ry.shared.config_read(defaults_file)

    if settings_file is not None:
        if os.path.exists(settings_file):
            user_file = '{}'.format(settings_file)
        else:
            user_file = '{}/{}/{}.txt'.format(ry.config['data_dir'], 'Settings', settings_file)
        settings_u = ry.shared.config_read(user_file)
        for t in settings_u: settings[t] = settings_u[t]

    return (settings)
