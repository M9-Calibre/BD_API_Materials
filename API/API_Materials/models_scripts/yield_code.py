import sys
import math
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from typing import Dict
import numpy as np


def run_yld2000(arguments):
    return run_model(arguments, model="yld2000")


def run_yld2004(arguments):
    return run_model(arguments, model="yld2004")


def run_model(arguments: Dict[str, float], model: str = "yld2000"):
    ensure_matplotlib_patch()

    arg_keys = ["alpha1", "alpha2", "alpha3", "alpha4", "alpha5", "alpha6", "alpha7", "alpha8", "a"]
    cp = [355.] + [arguments[name] for name in arg_keys]

    if model == 'yld2000':
        yld = 1
    elif model == 'yld2004':
        yld = 2

    # Creating data pairs of S11,S22,S12
    x11 = np.arange(-1000, 1000, 25)
    x22 = np.arange(-1000, 1000, 25)
    x12 = np.zeros((len(x11)))

    s = np.empty((len(x11), 4))
    s[:, 0] = x11
    s[:, 1] = x22
    s[:, 2] = x12

    # Set input model parameters (cp)
    if yld == 1:
        #cp = [355, 1.011, 0.964, 1.191, 0.995, 1.010, 1.018, 0.977, 0.935, 6]
        a, em, s0 = htpp_yfunc_yld2000_2d_param(cp)
    elif yld == 2:
        #cp = [355, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 6]
        cp1, cp2, a, s0 = htpp_yfunc_yld2004_param(cp)

    yyi = np.zeros((len(x11), len(x22)))
    yy = np.zeros((len(x11) * len(x22), 2))
    h = 0
    l = 0
    x = 1
    for i in range(len(x11)):
        for j in range(len(x22)):
            if yld == 1:
                yyi[i, j] = htpp_yfunc_ylocus_yld2000_2d(x, s[i, 0], s[j, 1], a, em, s0)
            elif yld == 2:
                yyi[i, j] = htpp_yfunc_ylocus_yld2004(x, s[i, 0], s[j, 1], cp1, cp2, a, s0)
            yy[l, 0] = yyi[i, j]
            l = l + 1
        h = h + 1

    plt.clf()
    c1 = plt.contour(x11 / s0, x22 / s0, yyi / s0, 0, linestyles='-', linewidths=0.9, colors='k')

    np.set_printoptions(suppress=True, formatter={'float_kind': '{:f}'.format}, threshold=sys.maxsize)

    # Legend settings
    h1, l1 = c1.legend_elements()
    plt.legend([h1[0], h1[1]], ['Yield locus'])
    plt.axhline(0, linestyle='-', color='k', linewidth=0.3)  # horizontal lines
    plt.axvline(0, linestyle='-', color='k', linewidth=0.3)  # vertical lines
    plt.xlabel('$\sigma_2/\sigma_0$ [MPa]')
    plt.ylabel('$\sigma_1/\sigma_0$ [MPa]')
    # plt.ylim(-1.5,1.5)
    # plt.xlim(-1.5,1.5)

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = "data:image/png;base64," + base64.b64encode(buf.read()).decode('utf-8')
    # print(img)
    # plt.show()
    # plt.close()

    return img


# ------------------------------------------------------------------------------
# ---------------------------------------------------------- IMPORT COEFFICIENTS
# ------------------------------------------------------------------------------
def htpp_yfunc_yld2004_param(cp):
    cp1 = np.zeros((6, 6))
    cp2 = np.zeros((6, 6))

    s0 = cp[0]
    cp1[0, 1] = -cp[1]
    cp1[0, 2] = -cp[2]
    cp1[1, 0] = -cp[3]
    cp1[1, 2] = -cp[4]
    cp1[2, 0] = -cp[5]
    cp1[2, 1] = -cp[6]
    cp1[3, 3] = cp[7]
    cp1[4, 4] = cp[8]
    cp1[5, 5] = cp[9]
    cp2[0, 1] = -cp[10]
    cp2[0, 2] = -cp[11]
    cp2[1, 0] = -cp[12]
    cp2[1, 2] = -cp[13]
    cp2[2, 0] = -cp[14]
    cp2[2, 1] = -cp[15]
    cp2[3, 3] = cp[16]
    cp2[4, 4] = cp[17]
    cp2[5, 5] = cp[18]
    a = 6

    return cp1, cp2, a, s0


# ------------------------------------------------------------------------------
# --------------------------------------------------- CALCULATE YIELD FUNCTION 2
# ------------------------------------------------------------------------------
def htpp_yfunc_yld2004_sub(sp):
    hp = np.zeros(3)
    hp[0] = (sp[0] + sp[1] + sp[2]) / 3.0
    hp[1] = (sp[4] ** 2 + sp[5] ** 2 + sp[3] ** 2 - sp[1] * sp[2] - sp[2] * sp[0] - sp[0] * sp[1]) / 3.0
    hp[2] = (2 * sp[4] * sp[5] * sp[3] + sp[0] * sp[1] * sp[2] - sp[0] * sp[5] ** 2 - sp[1] * sp[4] ** 2 - sp[2] * sp[
        3] ** 2) / 2.0

    hpq = math.sqrt(hp[0] ** 2 + hp[1] ** 2 + hp[2] ** 2)
    psp = np.zeros(3)
    if hpq > 1.0e-16:
        cep = hp[0] ** 2 + hp[1]
        ceq = (2 * hp[0] ** 3 + 3 * hp[0] * hp[1] + 2 * hp[2]) / 2.0
        cetpq = ceq / cep ** (3.0 / 2.0)
        if cetpq > 1.0:
            cetpq = 1.0
        elif cetpq < -1.0:
            cetpq = -1.0
        cet = math.acos(cetpq)

        psp[0] = 2 * math.sqrt(cep) * math.cos(cet / 3.0) + hp[0]
        psp[1] = 2 * math.sqrt(cep) * math.cos((cet + 4.0 * math.pi) / 3.0) + hp[0]
        psp[2] = 2 * math.sqrt(cep) * math.cos((cet + 2.0 * math.pi) / 3.0) + hp[0]
    else:
        cetpq = 0.0

    return psp, cetpq, hp


# ------------------------------------------------------------------------------
# ------------------------------ CALCULATE COEFFICIENT OF EQUIVALENT STRESS DC 2
# ------------------------------------------------------------------------------
def htpp_yfunc_yld2004_coef_sub(cp):
    aap = np.zeros(3)
    aap[0] = (cp[0, 1] + cp[0, 2] - 2.0 * cp[1, 0] + cp[1, 2] - 2.0 * cp[2, 0] + cp[2, 1]) / 9.0
    aap[1] = ((2.0 * cp[1, 0] - cp[1, 2]) * (cp[2, 1] - 2.0 * cp[2, 0]) + (2.0 * cp[2, 0] - cp[2, 1]) * (
                cp[0, 1] + cp[0, 2]) + (cp[0, 1] + cp[0, 2]) * (2.0 * cp[1, 0] - cp[1, 2])) / 27.0
    aap[2] = (cp[0, 1] + cp[0, 2]) * (cp[1, 2] - 2.0 * cp[1, 0]) * (cp[2, 1] - 2.0 * cp[2, 0]) / 54.0

    ppp = aap[0] ** 2 + aap[1]
    qqp = (2 * aap[0] ** 3 + 3 * aap[0] * aap[1] + 2 * aap[2]) / 2.0
    ttp = math.acos(qqp / ppp ** (3.0 / 2.0))

    bbp = np.zeros(3)
    bbp[0] = 2 * math.sqrt(ppp) * math.cos(ttp / 3.0) + aap[0]
    bbp[1] = 2 * math.sqrt(ppp) * math.cos((ttp + 4 * math.pi) / 3.0) + aap[0]
    bbp[2] = 2 * math.sqrt(ppp) * math.cos((ttp + 2 * math.pi) / 3.0) + aap[0]

    return bbp


# ------------------------------------------------------------------------------
# -------------------------------- CALCULATE COEFFICIENT OF EQUIVALENT STRESS DC
# ------------------------------------------------------------------------------
def htpp_yfunc_yld2004_coef(cp1, cp2, a):
    bbp1 = htpp_yfunc_yld2004_coef_sub(cp1)
    bbp2 = htpp_yfunc_yld2004_coef_sub(cp2)
    dc = 0.0
    for i in range(3):
        for j in range(3):
            dc += abs(bbp1[i] - bbp2[j]) ** a

    return dc


# ------------------------------------------------------------------------------
# ------------------------------------- CALCULATE YIELD FUNCTION FOR YIELD LOCUS
# ------------------------------------------------------------------------------
def htpp_yfunc_ylocus_yld2004(x, s1, s2, cp1, cp2, a, s0):
    s = [s1 * x, s2 * x, 0, 0.1, 0, 0]
    cl = np.zeros((6, 6))
    for i in range(3):
        for j in range(3):
            cl[i, j] = -1
            if i == j:
                cl[i, j] = 2

    for i in range(3, 6):
        cl[i, i] = 3
    cl = cl / 3.0

    dc = htpp_yfunc_yld2004_coef(cp1, cp2, a)
    ctp1 = np.dot(cp1, cl)
    ctp2 = cp2.dot(cl)
    sp1 = np.dot(ctp1, s)
    sp2 = ctp2.dot(s)

    psp1, cetpq1, hp1 = htpp_yfunc_yld2004_sub(sp1)
    psp2, cetpq2, hp2 = htpp_yfunc_yld2004_sub(sp2)

    f = 0.0
    for i in range(3):
        for j in range(3):
            f += abs(psp1[i] - psp2[j]) ** a
    se = (f / dc) ** (1.0 / a) - s0

    return se


# ------------------------------------------------------------------------------
# --------------------------------------- CALCULATE PHI VALUES OF YIELF FUNCTION
# ------------------------------------------------------------------------------
def htpp_yfunc_yld2000_2d_phi(am, em, s):
    p = [1.0, -1.0]

    y = np.zeros((2, 3))
    for n in range(2):
        y[n] = am[n].dot(s)

    x = np.zeros((2, 2))
    for n in range(2):
        a = math.sqrt((y[n, 0] - y[n, 1]) ** 2 + 4 * y[n, 2] ** 2)
        for i in range(2):
            x[n, i] = 0.5 * (y[n, 0] + y[n, 1] + p[i] * a)

    phi = np.zeros(2)
    phi[0] = abs(x[0, 0] - x[0, 1]) ** em
    phi[1] = abs(2 * x[1, 1] + x[1, 0]) ** em + abs(2 * x[1, 0] + x[1, 1]) ** em

    return phi, x, y


# ------------------------------------------------------------------------------
# ---------------------------------------------------------- IMPORT COEFFICIENTS
# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
# --------------------------------------------- SET LINEAR TRANSFORMATION MATRIX
# ------------------------------------------------------------------------------
def htpp_yfunc_yld2000_2d_am(a):
    am = np.zeros((2, 3, 3))

    am[0, 0, 0] = 2.0 * a[0]
    am[0, 0, 1] = -1.0 * a[0]
    am[0, 1, 0] = -1.0 * a[1]
    am[0, 1, 1] = 2.0 * a[1]
    am[0, 2, 2] = 3.0 * a[6]

    am[1, 0, 0] = -2.0 * a[2] + 2.0 * a[3] + 8.0 * a[4] - 2.0 * a[5]
    am[1, 0, 1] = a[2] - 4.0 * a[3] - 4.0 * a[4] + 4.0 * a[5]
    am[1, 1, 0] = 4.0 * a[2] - 4.0 * a[3] - 4.0 * a[4] + a[5]
    am[1, 1, 1] = -2.0 * a[2] + 8.0 * a[3] + 2.0 * a[4] - 2.0 * a[5]
    am[1, 2, 2] = 9.0 * a[7]

    am[0] = am[0] / 3.0
    am[1] = am[1] / 9.0

    return am


# ------------------------------------------------------------------------------
# ------------------------------------- CALCULATE YIELD FUNCTION FOR YIELD LOCUS
# ------------------------------------------------------------------------------
def htpp_yfunc_ylocus_yld2000_2d(x, s1, s2, a, em, s0):
    s = [s1 * x, s2 * x, 0.0]

    am = htpp_yfunc_yld2000_2d_am(a)

    phi, x, y = htpp_yfunc_yld2000_2d_phi(am, em, s)

    q = phi[0] + phi[1]
    if q <= 0.0:
        q = 0.0
    se = ((0.5 * q) ** (1.0 / em)) - s0

    return se


# Patch
def ensure_matplotlib_patch():
    _old_show = plt.show

    def show():
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        # Encode to a base64 str
        img = 'data:image/png;base64,' + \
              base64.b64encode(buf.read()).decode('utf-8')
        # Write to stdout
        print(img)
        plt.clf()

    plt.show = show