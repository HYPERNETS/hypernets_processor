## interpolate Mobley sky reflectance LUT
## ths is sun zenith angle
## thv is viewing angle
## phi is photon travel angle with sun at 0°, phi = 180 - relative azimuth
## QV 2018-07-18
## Last modifications: QV 2018-08-02 added abs to phi lutpos
##                     QV 2019-07-10 integrated in rhymer

def mobley_lut_interp(ths, thv, phi, wind=2., rholut=None):
    import rhymer as ry
    if rholut is None: rholut = ry.processing.mobley_lut_read()
    dval = rholut['header']

    ## find wind speeds
    wind_id, wind_br = ry.shared.lutpos(dval['Wind'], wind)
    wind_w = wind_id - wind_br[0]

    ## find geometry
    ths_id, ths_br = ry.shared.lutpos(dval['Theta-sun'], ths)
    thv_id, thv_br = ry.shared.lutpos(dval['Theta'], thv)
    phi_id, phi_br = ry.shared.lutpos(dval['Phi'], abs(phi))

    ## interpolate for both bracketing wind speeds
    it1 = ry.shared.interp3d(rholut['data'][wind_br[0], :, :, :], ths_id, thv_id, phi_id)
    it2 = ry.shared.interp3d(rholut['data'][wind_br[1], :, :, :], ths_id, thv_id, phi_id)

    ## and weigh to wind speed
    rint = it2 * wind_w + it1 * (1. - wind_w)
    return (rint)
