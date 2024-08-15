import numpy as np
import math
from math import cos, sin


# ------------ Hill 48 ----------------
def get_hill_48_parameters(h: float, g: float, f: float, n: float, default_value=1.5):
    c = np.zeros((6, 6))

    s0 = 1

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
    c[1, 1] = pf + pg
    c[1, 2] = -pf
    c[2, 0] = -pg
    c[2, 1] = -pf
    c[2, 2] = pf + ph
    c[3, 3] = 2.0 * pl
    c[4, 4] = 2.0 * pm
    c[5, 5] = 2.0 * pn
    c = c / (pg + ph)

    return c, s0


def htpp_yfunc_anisotropy_aux1(ang, shear=None):
    round_range = 4
    xx = cos(ang) ** 2
    yy = sin(ang) ** 2
    xy = shear if shear else sin(ang) * cos(ang)

    # xx = round(xx, round_range)
    # yy = round(yy, round_range)
    # xy = round(xy, round_range)
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


# ------------ Yield 2000 ----------------
def htpp_yfunc_yld2000_2d_param(cp):
    a = np.zeros((8, 1))

    s0 = cp[0]
    a[0] = cp[1]
    a[1] = cp[2]
    a[2] = cp[3]
    a[3] = cp[4]
    a[4] = cp[5]
    a[5] = cp[6]
    a[6] = cp[7]
    a[7] = cp[8]
    em = cp[9]

    return a, em, s0


def htpp_yfunc_ylocus_yld2000_2d(x, s1, s2, s12, a, em, s0):
    s = [s1 * x, s2 * x, s12 * x]

    am = htpp_yfunc_yld2000_2d_am(a)

    phi, x, y = htpp_yfunc_yld2000_2d_phi(am, em, s)
    # print(f"{x=}")
    q = phi[0] + phi[1]
    if q <= 0.0:
        q = 0.0
    se = ((0.5 * q) ** (1.0 / em)) - s0
    # print(f"{se=}")
    return se


def htpp_yfunc_yld2000_2d_am(a):
	am = np.zeros((2,3,3))

	am[0,0,0] =  2.0*a[0]
	am[0,0,1] = -1.0*a[0]
	am[0,1,0] = -1.0*a[1]
	am[0,1,1] =  2.0*a[1]
	am[0,2,2] =  3.0*a[6]

	am[1,0,0] = -2.0*a[2]+2.0*a[3]+8.0*a[4]-2.0*a[5]
	am[1,0,1] =      a[2]-4.0*a[3]-4.0*a[4]+4.0*a[5]
	am[1,1,0] =  4.0*a[2]-4.0*a[3]-4.0*a[4]+    a[5]
	am[1,1,1] = -2.0*a[2]+8.0*a[3]+2.0*a[4]-2.0*a[5]
	am[1,2,2] =  9.0*a[7]

	am[0] = am[0]/3.0
	am[1] = am[1]/9.0
	return am


def htpp_yfunc_yld2000_2d_phi(am,em,s):
	p = [1.0,-1.0]

	y = np.zeros((2,3))
	for n in range(2):
		y[n] = am[n].dot(s)

	x = np.zeros((2,2))
	for n in range(2):
		a = math.sqrt((y[n,0]-y[n,1])**2 + 4*y[n,2]**2)
		for i in range(2):
			x[n,i] = 0.5*(y[n,0]+y[n,1]+p[i]*a)

	phi = np.zeros(2)
	phi[0] = abs(x[0,0]-x[0,1])**em
	phi[1] = abs(2*x[1,1]+x[1,0])**em + abs(2*x[1,0]+x[1,1])**em

	return phi,x,y
