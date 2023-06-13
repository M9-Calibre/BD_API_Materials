import numpy as np
from typing import Any


# TODO: One single endpoint, but with 3 arguments section (Hardening, Yield and Elastic)

def generate_points(hardening_args: dict[str, Any], yield_args: dict[str, float], elastic_args: dict[str, float],
                    hardening_func: str, yield_func: str, elastic_func: str,
                    minimum=0, maximum=1, step=0.01) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    inpt = np.arange(minimum, maximum, step)
    hardening_args["inpt"] = inpt
    elastic_args["inpt"] = inpt

    # Calculating Hardening law
    hardening_points = calculate_hardening(hardening_func, **hardening_args)

    # Calculating Yield locus
    yield_points = calculate_yield(yield_func, **yield_args)

    # Calculating Elastic locus
    elastic_points = calculate_elastic(elastic_func, **elastic_args)

    # TODO: Merge points to get final graph (i don't know if it is just a merge for instance)
    ...

    return hardening_points, yield_points, elastic_points


# ------------- Hardening functions ----------------
def calculate_hardening(func_name: str, **kwargs) -> np.ndarray:
    return HARDENING_FUNCTIONS[func_name](**kwargs)


def calculate_swift_hardening(k: float, eps0: float, swift_n: float, inpt: np.ndarray) -> np.ndarray:
    # Defined at the ent of file in SETUP area (check for "HARDENING_FUNCTIONS")
    return k * ((eps0 + inpt) ** swift_n)


# ------------- Yield functions -------------
def calculate_yield(func_name: str, **kwargs) -> np.ndarray:
    return YIELD_FUNCTIONS[func_name](**kwargs)


def calculate_sample_yield(h: float, g: float, f: float, n: float, shear: float) -> np.ndarray:
    # TODO: Not sure if this beginning setup is exclusive to this function or not
    # Creating mesh points for populating the equations
    x_min = -10
    x_max = 10
    y_min = -10
    y_max = 10

    x1, x2 = np.meshgrid(np.arange(x_min, x_max, 0.1), np.arange(y_min, y_max, 0.1))

    return h * (x1 - x2) ** 2 + g * (x1 ** 2) + f * (x2 ** 2) + 2 * n * (shear ** 2)


# ------------- Elastic functions -------------
def calculate_elastic(func_name: str, **kwargs) -> np.ndarray:
    return ELASTIC_FUNCTIONS[func_name](**kwargs)


def calculate_sample_elastic(inpt: np.ndarray) -> np.ndarray:
    return np.array([x for x in range(len(inpt)) if inpt[x] == 0])


# ------------- SETUP ----------------
# Here you can add new functions to the dictionaries.

# Hardening Functions
HARDENING_FUNCTIONS = {
    "swift": calculate_swift_hardening,
}

# Yield Functions
YIELD_FUNCTIONS = {
    "sample": calculate_sample_yield,
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

    # print(hard_points)
    # print(yld_points)
    # print(elstc_points)
