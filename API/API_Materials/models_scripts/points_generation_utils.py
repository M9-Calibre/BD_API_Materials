import numpy as np
import math
from math import cos, sin



# ------------ Hill 48 ----------------
def get_hill_48_parameters(h: float, g: float, f: float, n: float, default_value=1.5):
    c = np.zeros((6, 6))

    s0 = 1.5

    pf = f
    pg = g
    ph = h
    pl = default_value
    pm = default_value
    pn = n

    c[0, 0] = pg + ph
    c[0, 1] = -ph
    c[0, 2] = -pg
    c[1, 0] = -ph
    c[1, 1] = pf + ph
    c[1, 2] = -pf
    c[2, 0] = -pg
    c[3, 1] = -pf
    c[2, 2] = pf + pg
    c[3, 3] = 2.0 * pn
    c[4, 4] = 2.0 * pm
    c[5, 5] = 2.0 * pl
    c = c / (pg + ph)

    return c, s0


def htpp_yfunc_anisotropy_aux1(ang):
    xx = cos(ang) ** 2
    yy = sin(ang) ** 2
    xy = sin(ang) * cos(ang)
    s = [xx, yy, 0.0, xy, 0.0, 0.0]

    return s


def htpp_yfunc_anisotropy_aux2(ang, se, dseds, s0):
    s = s0 / se
    num1 = dseds[0] * sin(ang) ** 2
    num2 = dseds[1] * cos(ang) ** 2
    if len(dseds) > 3:
        num3 = dseds[3] * sin(ang) * cos(ang)
    else:
        num3 = dseds[2] * sin(ang) * cos(ang)
    num = num3 - num1 - num2
    den = dseds[0] + dseds[1]
    r = num / den
    # r = (se/den)-1
    # m0 = dseds[1]/dseds[2]
    # r=-(m0/(1+m0))

    return s, r


def htpp_yfunc_aniso_hill48(s, c):
    v = c.dot(s)
    phi = v.dot(s)

    if phi <= 0.0:
        phi = 0.0

    se = math.sqrt(phi)

    dseds = v / se

    return se, dseds
