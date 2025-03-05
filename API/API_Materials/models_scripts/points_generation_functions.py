from API_Materials.models_scripts.points_generation_utils import *
from math import pi

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

#### Yield ####
### ----- Hill 48 ----- ###
def calculate_yield_48_3d(h: float, g: float, f: float, n: float) -> dict:
    # TODO: Not sure if this beginning setup is exclusive to this function or not
    # Creating mesh points for populating the equations

    x_min = -2
    x_max = 2
    y_min = -2
    y_max = 2
    z_min = -2
    z_max = 2
    step = 0.1
    shear_step = 0.1  # 0.005

    x1, x2, x3 = np.meshgrid(np.arange(x_min, x_max, step), np.arange(y_min, y_max, step),
                             np.arange(z_min, z_max, step))

    z0 = h * (x1 - x2) ** 2 + g * (x1 ** 2) + f * (x2 ** 2) + 2 * n * (x3 ** 2)
    dic = {
        "value": z0.ravel(),
        # "x": np.linspace(x_min, x_max, z0[0][0].size),
        # "y": np.linspace(y_min, y_max, z0[0][0].size),
        # "value": np.linspace(z_min, z_max, z0[0][0].size)
        "x": x1.ravel(),
        "y": x2.ravel(),
        "z": x3.ravel()
    }
    z0.ravel()

    x1_2d, x2_2d = np.meshgrid(np.arange(x_min, x_max, shear_step), np.arange(y_min, y_max, shear_step))
    dic["shear_x"] = x1_2d.ravel()
    dic["shear_y"] = x2_2d.ravel()
    dic["shears"] = {}
    for idx, val in enumerate(np.arange(0, 0.61, 0.2)):
        dic["shears"][val] = {}
        z = h * (x1_2d - x2_2d) ** 2 + g * (x1_2d ** 2) + f * (x2_2d ** 2) + 2 * n * (val ** 2)
        dic["shears"][val]["value"] = z.ravel()
        dic["shears"][val]["z"] = val

    # Extra teste
    # sus_step = 0.001
    # x1_2d2, x2_2d2 = np.meshgrid(np.arange(x_min, x_max, sus_step), np.arange(y_min, y_max, sus_step))
    # for idx, val in enumerate(np.arange(0, 0.61, 0.2)):
    #     z = h * (x1_2d2 - x2_2d2) ** 2 + g * (x1_2d2 ** 2) + f * (x2_2d2 ** 2) + 2 * n * (val ** 2)
    #     teste_float = 0.00001
    #     print("------------")
    #     print(f'shear: = {val}')
    #     print(f'small_float: {teste_float}')
    #     print(f'z == 1: {np.any(z == 1)}')
    #     print(f'z >= 1 - small_float and z <= 1 + small_float: {np.any(np.logical_and(z >= 1 - teste_float, z <= 1 + teste_float))}')

    return dic


def calculate_yield_48(h: float, g: float, f: float, n: float) -> np.ndarray:
    c, s0 = get_hill_48_parameters(h, g, f, n)

    angle = np.linspace(0, pi / 2, 91)  # X axis (radians)
    sAngles, rAngles = [], []  # Y1 and Y2

    xx = []
    yy = []
    xy = []
    for i in range(0, len(angle)):
        s = htpp_yfunc_anisotropy_aux1(angle[i])
        xx.append(s[0])
        yy.append(s[1])
        xy.append(s[3])
        se, dseds = htpp_yfunc_aniso_hill48(s, c)
        sAng, rAng = htpp_yfunc_anisotropy_aux2(angle[i], se, dseds, s0)
        sAngles.append(sAng)
        rAngles.append(rAng)

    # convert angles to degrees
    degree_angles = np.degrees(angle)
    sAngles = np.round(sAngles, 8)
    rAngles = np.round(rAngles, 8)
    dic = {
        "x": degree_angles,
        "s": sAngles,
        "r": rAngles,
        "xx": xx,
        "yy": yy,
        "xy": xy
    }

    # Add shear
    # shears = np.arange(0, 0.61, 0.2)
    # for shear, idx in enumerate(shears):
    #     shearSAngles = []
    #     shearRAngles = []
    #     for i in range(0, len(angle)):
    #         s = htpp_yfunc_anisotropy_aux1(angle[i], shear)
    #         se, dseds = htpp_yfunc_aniso_hill48(s, c)
    #         sAng, rAng = htpp_yfunc_anisotropy_aux2(angle[i], se, dseds, s0)
    #         shearSAngles.append(sAng)
    #         shearRAngles.append(rAng)

    # dic[f"z{idx}"] = shearSAngles
    # dic[f"shear{idx}"] = shear

    return dic


### ----- Yield 2000 ----- ###
def calculate_yield_2000_3d(alpha1: float, alpha2: float, alpha3: float, alpha4: float, alpha5: float, alpha6: float,
                            alpha7: float, alpha8: float, alpha) -> dict:
    min_range = -1000
    max_range = 1000
    step = 25

    # Creating data pairs of S11,S22,S12
    # x11 = np.arange(min_range, max_range, step)
    # x22 = np.arange(min_range, max_range, step)
    # x12 = np.arange(min_range, max_range, step)

    x11, x22, x12 = np.meshgrid(np.arange(min_range, max_range, step), np.arange(min_range, max_range, step),
                                np.arange(min_range, max_range, step))

    cp = [355, alpha1, alpha2, alpha3, alpha4, alpha5, alpha6, alpha7, alpha8, alpha]
    a, em, s0 = htpp_yfunc_yld2000_2d_param(cp)

    yy1 = np.zeros((len(x11), len(x22), len(x12)))
    x = 1
    for i in range(len(x11)):
        for j in range(len(x22)):
            for k in range(len(x12)):
                yy1[i, j, k] = htpp_yfunc_ylocus_yld2000_2d(x, x11[i, j, k], x22[i, j, k], x12[i, j, k], a, em,
                                                            s0)

    dic = {
        "z0": yy1.ravel(),
        "x": x11.ravel(),
        "y": x22.ravel(),
        "value": x12.ravel()
    }

    # Add shears
    x1_2d, x2_2d = np.meshgrid(np.arange(min_range, max_range, step), np.arange(min_range, max_range, step))
    for idx, shear in enumerate(np.arange(0, 0.61, 0.2)):
        yy = np.zeros((len(x1_2d), len(x2_2d)))
        for i in range(len(x1_2d)):
            for j in range(len(x2_2d)):
                yy[i, j] = htpp_yfunc_ylocus_yld2000_2d(1, x1_2d[i, j], x2_2d[i, j], shear, a, em, s0)
        dic[f"z{idx + 1}"] = yy.ravel()
        dic[f"shear{idx + 1}"] = shear

    return dic


### ----- Yield 2004 ----- ###
def calculate_yield_2004_3d(**kwargs) -> dict:
    # This uses "kwargs" instead to facilitate because there is a lot lmao
    min_range = -1000
    max_range = 1000
    step = 25

    # Creating data pairs of S11,S22,S12
    # x11 = np.arange(min_range, max_range, step)
    # x22 = np.arange(min_range, max_range, step)
    # x12 = np.arange(min_range, max_range, step)

    x11, x22, x12 = np.meshgrid(np.arange(min_range, max_range, step), np.arange(min_range, max_range, step),
                                np.arange(min_range, max_range, step))

    # Add correct args to array
    cp = [355]
    idx_order = [12, 13, 21, 23, 31, 32, 44, 55, 66]  # Used only to get the variables in kwargs
    for idx in idx_order:
        cp.append(kwargs[f"c{idx}"])
    for idx in idx_order:
        cp.append(kwargs[f"cc{idx}"])
    cp.append(kwargs["alpha"])

    cp1,cp2,a,s0 = htpp_yfunc_yld2004_param(cp)

    yy1 = np.zeros((len(x11), len(x22), len(x12)))
    x = 1
    for i in range(len(x11)):
        for j in range(len(x22)):
            for k in range(len(x12)):
                yy1[i, j, k] = htpp_yfunc_ylocus_yld2004(x, x11[i, j, k], x22[i, j, k], x12[i, j, k], cp1, cp2,
                                                            a, s0)

    dic = {
        "z0": yy1.ravel(),
        "x": x11.ravel(),
        "y": x22.ravel(),
        "value": x12.ravel()
    }

    # Add shears
    x1_2d, x2_2d = np.meshgrid(np.arange(min_range, max_range, step), np.arange(min_range, max_range, step))
    for idx, shear in enumerate(np.arange(0, 0.61, 0.2)):
        yy = np.zeros((len(x1_2d), len(x2_2d)))
        for i in range(len(x1_2d)):
            for j in range(len(x2_2d)):
                yy[i, j] = htpp_yfunc_ylocus_yld2004(1, x1_2d[i, j], x2_2d[i, j], shear, cp1, cp2, a, s0)
        dic[f"z{idx + 1}"] = yy.ravel()
        dic[f"shear{idx + 1}"] = shear

    return dic

#### Hardening ####


# Constants and parameters (these would need to be initialized properly)
constants = {
    "young": 180000.0,  # Young's modulus
    "poiss": 0.3,  # Poisson's ratio
    "raypi": 400.0,  # Material property
    "granqp": 300.0,  # Material property
    "petibp": 20.0,  # Material property
    "grc1p": 60000.0,  # Material property
    "grd1p": 200.0,  # Material property
    "linHard_h": 5000.,  # Material property
    "swift_n": 0.1,
    "swift_k": 400.,
    "swift_eps0": 0.001
}


def charging(t, dt):
    # Charging strain with time
    if t <= 0.3:
        eps11 = t  # * 0.3 # 1 correspond to 0.3
        deps11 = dt  # * 0.3 # increments of time corresponds to increments on load
    elif t > 0.3:
        eps11 = 0.3 - (t - 0.3)  # * 0.3
        deps11 = -1. * dt  # * (-0.3) # inversion
    return eps11, deps11


def isoHardening(epcum, constants):
    drdp = 0
    r_iso = constants["swift_k"] * (epcum + constants["swift_eps0"]) ** constants["swift_n"]
    if epcum > 0: drdp = constants["swift_n"] * constants["swift_k"] * epcum ** (constants["swift_n"] - 1.)
    return r_iso, drdp


# Define the derivative function based on grandF
def grandF(t, y):
    global last_time  # Store the last time step here
    if last_time is None:
        dt = 0  # Initial call, set increment to zero
    else:
        dt = t - last_time  # Calculate the time increment
    last_time = t  # Update last_time for the next call

    # Unpack y values into variables for readability
    # epcum, epl11, alf11, sig11  = y
    sig11, epl11 = y  # State variables: stress and plastic strain
    # Charging strain with time
    eps11, deps11 = charging(t, dt)
    # Determine sig based on charging in xx direction
    sig11 = constants["young"] * (eps11 - epl11)
    # determining hardening
    ris, drdp = isoHardening(epl11, constants)
    critp = abs(sig11) - ris
    flow = deps11 * sig11

    if critp >= 0. and deps11 * sig11 >= 0.:
        depl11 = constants["young"] / (constants["young"] + drdp)  # using book
    else:
        depl11 = 0.

    dsig11 = np.sign(deps11) * constants["young"] * (1. - depl11)  # dsig11 = dsig11/desp11
    return [dsig11, depl11]


# Initial conditions for solve_ivp
# y0 = [0., 0., 0.] #, 0.]  # Initial values of the state variables
y0 = [0., 0.]

# Time span for integration
t_span = (0, 0.5)
last_time = None  # Initialize to store the last time

# Perform the integration
result = solve_ivp(lambda t, y: grandF(t, y), t_span, y0, method='RK23', max_step=0.001)

eps11 = np.zeros_like(result.t)
deps11 = np.zeros_like(result.t)
# Calculate eps11 based on the results
for i, t in enumerate(result.t):
    eps11[i], deps11[i] = charging(t, 0.)
    # print(i,"t=",t,result.t[i], eps11[i])

sig11 = constants["young"] * (eps11 - result.y[1])  # Recalculate sig11

# Plotting the results
plt.figure(figsize=(8, 7))

# Subplot 1: Epcum
plt.subplot(4, 1, 1)
plt.plot(eps11, result.y[0], label='sigma', color='b')
plt.title('Evolution of stress-strain')
plt.xlabel('strain eps11, time')
plt.ylabel('sig11')
plt.grid()
plt.legend()

# Subplot 2: Depl11
plt.subplot(4, 1, 2)
plt.plot(result.t, result.y[1], label='epl11', color='g')
plt.title('Evolution of epl11')
plt.xlabel('strain eps11, time')
plt.ylabel('epl 11')
plt.grid()
plt.legend()

# Subplot 3: Dalf11
plt.subplot(4, 1, 3)
plt.plot(result.t, eps11, label='eps11', color='r')
plt.title('Evolution of eps11')
plt.xlabel('time')
plt.ylabel('strain eps11')
plt.grid()
plt.legend()

# Subplot 4: Sig11 vs Eps11
plt.subplot(4, 1, 4)
plt.plot(eps11, sig11, label='Sig11', color='m')  # result.y[3]
plt.title('Sig11 vs Eps11')
plt.xlabel('straon eps11')
plt.ylabel('sig11 calculated outside')
plt.grid()
plt.legend()

plt.tight_layout()
plt.show()
