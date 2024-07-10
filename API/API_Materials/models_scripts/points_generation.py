import numpy as np
from typing import Any
from math import pi
from API_Materials.models_scripts.points_generation_utils import *


def generate_all_points(hardening_args: dict[str, Any], yield_args: dict[str, float], elastic_args: dict[str, float],
                        hardening_func: str, yield_func: str, elastic_func: str,
                        minimum=0, maximum=1, step=0.01, min_elastic=0, max_elastic=0.02, step_elastic=0.001) -> \
        tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Given the arguments for each function, it will generate the points for each one and return them as a tuple"""
    hardening_inpt = np.arange(minimum, maximum, step)
    elastic_inpt = np.arange(min_elastic, max_elastic, step_elastic)
    hardening_args["inpt"] = hardening_inpt
    elastic_args["inpt"] = elastic_inpt

    # Calculating Hardening law
    hardening_points = calculate_hardening(hardening_func, **hardening_args)

    # Calculating Yield locus
    yield_points = calculate_yield(yield_func, **yield_args)

    # Calculating Elastic locus
    elastic_points = calculate_elastic(elastic_func, **elastic_args)

    # TODO: Merge points to get final graph (i don't know if it is just a merge for instance)
    ...

    return hardening_points, yield_points, elastic_points, hardening_inpt, elastic_inpt


def generate_points(function_type: str, args: [dict[str, Any]], function: str, minimum=0, maximum=1, step=0.01,
                    min_elastic=0, max_elastic=0.02, step_elastic=0.001):
    """Given the arguments for one function, it will generate the points for and return them"""

    # Create input scalar for hardening or elastic function
    inpt = None

    match function_type:
        case "hardening":
            inpt = np.arange(minimum, maximum, step)
            args["inpt"] = inpt
            points = calculate_hardening(function, **args)
        case "yield":
            points = calculate_yield(function, **args)
        case "elastic":
            inpt = np.arange(min_elastic, max_elastic, step_elastic)
            args["inpt"] = inpt
            points = calculate_elastic(function, **args)
        case _:
            raise ValueError("Invalid function type")

    return points, inpt


# ------------- Hardening functions ----------------
def calculate_hardening(func_name: str, **kwargs) -> np.ndarray:
    return HARDENING_FUNCTIONS[func_name](**kwargs)


def calculate_swift_hardening(k: float, eps0: float, swift_n: float, inpt: np.ndarray) -> np.ndarray:
    # Defined at the end of file in SETUP area (check for "HARDENING_FUNCTIONS")
    return k * ((eps0 + inpt) ** swift_n)


# ------------- Yield functions -------------
def calculate_yield(func_name: str, **kwargs) -> np.ndarray:
    dic = {}
    dic["3d"] = YIELD_FUNCTIONS_3D[func_name](**kwargs)
    dic["2d"] = YIELD_FUNCTIONS[func_name](**kwargs)

    return dic


def calculate_yield_48_3d(h: float, g: float, f: float, n: float) -> dict:
    # TODO: Not sure if this beginning setup is exclusive to this function or not
    # Creating mesh points for populating the equations
    print(f"h: {h}, g: {g}, f: {f}, n: {n}")
    x_min = -2
    x_max = 2
    y_min = -2
    y_max = 2
    z_min = -2
    z_max = 2
    step = 0.1
    shear_step = 0.005 #0.01

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
    print(f'{sAngles=}')
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


# ------------- Elastic functions -------------
def calculate_elastic(func_name: str, **kwargs) -> np.ndarray:
    return ELASTIC_FUNCTIONS[func_name](**kwargs)


def calculate_sample_elastic(**kwargs) -> np.ndarray:
    # This uses "kwargs" instead because "Young Modulus" cannot be a valid variable name
    # young_modulus = kwargs["multiplier"]
    young_modulus = kwargs["Young Modulus"]
    inpt = kwargs["inpt"]
    return np.arange(0, len(inpt) * young_modulus, 1 * young_modulus)


# ------------- SETUP ----------------
# Here you can add new functions to the dictionaries.

# Hardening Functions
HARDENING_FUNCTIONS = {
    "swift": calculate_swift_hardening,
}

# Yield Functions
YIELD_FUNCTIONS_3D = {
    "sample": calculate_yield_48_3d,
}

YIELD_FUNCTIONS = {
    "sample": calculate_yield_48
}

# Elastic Functions
ELASTIC_FUNCTIONS = {
    "sample": calculate_sample_elastic,
}

# ------------- MAIN (for tests) ----------------
if __name__ == '__main__':
    # Test the process function with custom example arguments

    # Set up arguments for each function
    hard_args = {
        "k": 979.46,
        "eps0": 0.00535,
        "swift_n": 0.194,
    }
    yld_args = {
        "h": 0.4709,
        "g": 1 - 0.4709,
        "f": 0.3748,
        "n": 1.1125,
        "shear": 1,
    }
    elstc_args = {
    }

    # Set up functions to be used
    hard_func = "swift"
    yld_func = "sample"
    elstc_func = "sample"

    # Set up range of values for the input to be used
    minimum_value = 0
    maximum_value = 1
    step_value = 0.01

    # Generate points
    hard_points, yld_points, elstc_points = generate_points(hard_args, yld_args, elstc_args,
                                                            hard_func, yld_func, elstc_func,
                                                            minimum_value, maximum_value, step_value)

    # Print Output
    # print(hard_points)
    # print(yld_points)
    # print(elstc_points)
