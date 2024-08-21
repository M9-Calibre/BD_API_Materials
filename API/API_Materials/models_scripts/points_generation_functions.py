from API_Materials.models_scripts.points_generation_utils import *


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
    shear_step = 0.005  # 0.01

    x1, x2, x3 = np.meshgrid(np.arange(x_min, x_max, step), np.arange(y_min, y_max, step),
                             np.arange(z_min, z_max, step))

    z0 = h * (x1 - x2) ** 2 + g * (x1 ** 2) + f * (x2 ** 2) + 2 * n * (x3 ** 2)
    dic = {
        "z0": z0.ravel(),
        # "x": np.linspace(x_min, x_max, z0[0][0].size),
        # "y": np.linspace(y_min, y_max, z0[0][0].size),
        # "value": np.linspace(z_min, z_max, z0[0][0].size)
        "x": x1.ravel(),
        "y": x2.ravel(),
        "value": x3.ravel()
    }
    z0.ravel()

    x1_2d, x2_2d = np.meshgrid(np.arange(x_min, x_max, shear_step), np.arange(y_min, y_max, shear_step))
    dic["x2"] = x1_2d.ravel()
    dic["y2"] = x2_2d.ravel()
    for idx, val in enumerate(np.arange(0, 0.61, 0.2)):
        z = h * (x1_2d - x2_2d) ** 2 + g * (x1_2d ** 2) + f * (x2_2d ** 2) + 2 * n * (val ** 2)
        dic[f"z{idx + 1}"] = z.ravel()
        dic[f"shear{idx + 1}"] = val

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
