import numpy as np
from typing import Any
from math import pi
from API_Materials.models_scripts.points_generation_functions import *


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
def calculate_yield(func_name: str, **kwargs) -> dict:
    dic = {}
    if func_name in YIELD_FUNCTIONS_3D:
        dic["3d"] = YIELD_FUNCTIONS_3D[func_name](**kwargs)
    if func_name in YIELD_FUNCTIONS:
        dic["2d"] = YIELD_FUNCTIONS[func_name](**kwargs)
    return dic


# ------------- Elastic functions -------------
def calculate_elastic(func_name: str, **kwargs) -> np.ndarray:
    return ELASTIC_FUNCTIONS[func_name](**kwargs)


def calculate_sample_elastic(**kwargs) -> np.ndarray:
    # This uses "kwargs" instead because "Young Modulus" cannot be a valid variable name
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
    "YLD2000": calculate_yield_2000_3d,
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