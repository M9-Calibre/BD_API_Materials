import numpy as np

from API_Materials.models_scripts.new_yield_calculation_methods import get_yield_result, get_non_matrix_equation

def calculate_yield_2000_3d(**kwargs):

    # Add 'alpha1', 'alpha2', ..., 'alpha8' variables
    variables = {
        "a": kwargs["alpha"]
    }

    for i in range(1, 9):
        variables[f"a{i}"] = kwargs[f"alpha{i}"]

    # T Matrix
    Tmatrix = np.array([[2, -1, 0], [-1, 2, 0], [0, 0, 3]])  # Not utilized because Lmatrixes exist

    # L Matrixes
    Lmatrix1 = np.array([["2 * a1", "-1 * a1", 0], ["-1 * a2", "2 * a2", 0], [0, 0, "3 * a7"]])

    Lmatrix2 = np.array([["8 * a5 - 2 * a3 - 2 * a6 + 2 * a4", "4 * a6 - 4 * a4 - 4 * a5 + a3", 0],
                         ["4 * a3 - 4 * a5 - 4 * a4 + a6", "8 * a4 - 2 * a6 - 2 * a3 + 2 * a5", 0], [0, 0, "9 * a8"]])

    # Equation
    eq1 = "| x11 - x12 | ** a"
    eq2 = "| 2 * x22 + x21 | ** a + | 2 * x21 + x22 | ** a"
    equation = f"{eq1} + {eq2}"

    sigma_min = -1000
    sigma_max = 1000
    sigma_step = 75

    division_ration = 5e28

    result = get_yield_result(variables, equation, Lmatrix1=Lmatrix1, Lmatrix1_multiplier=1 / 3, Lmatrix2=Lmatrix2,
                              Lmatrix2_multipler=1 / 9, sigma_min_range=sigma_min, sigma_max_range=sigma_max,
                              sigma_step=sigma_step, division_ration=division_ration)

    return result



def swift():
    equation = "k * ((eps0 + inpt) ** N)"
    variables = {
        "k": 979.46,
        "eps0": 0.0053,
        "N": 0.194
    }

    result = get_non_matrix_equation(variables=variables, equation=equation)


def calculate_yield_2004_3d():
    var = {
        "c'12": 1,
        "c'13": 1,
        "c'21": 1,
        "c'23": 1,
        "c'31": 1,
        "c'32": 1,
        "c'44": 1,
        "c'55": 1,
        "c'66": 1,
        "c''12": 1,
        "c''13": 1,
        "c''21": 1,
        "c''23": 1,
        "c''31": 1,
        "c''32": 1,
        "c''44": 1,
        "c''55": 1,
        "c''66": 1,
        "a": 6
    }

    eq = "| x11 - x21 | ** a + | x11 - x22 | ** a + | x11 - x23 | ** a + | x12 - x21 | ** a + | x12 - x22 | ** a + | x12 - x23 | ** a + | x13 - x21 | ** a + | x13 - x22 | ** a + | x13 - x23 | ** a"

    c_mat1 = np.array([
        [0, "-1 * c'12", "-1 * c'13", 0, 0, 0],
        ["-1 * c'21", 0, "-1 * c'23", 0, 0, 0],
        ["-1 * c'31", "-1 * c'32", 0, 0, 0, 0],
        [0, 0, 0, "c'44", 0, 0],
        [0, 0, 0, 0, "c'55", 0],
        [0, 0, 0, 0, 0, "c'66"]
    ])

    c_mat2 = np.array([
        [0, "-1 * c''12", "-1 * c''13", 0, 0, 0],
        ["-1 * c''21", 0, "-1 * c''23", 0, 0, 0],
        ["-1 * c''31", "-1 * c''32", 0, 0, 0, 0],
        [0, 0, 0, "c''44", 0, 0],
        [0, 0, 0, 0, "c''55", 0],
        [0, 0, 0, 0, 0, "c''66"]
    ])

    T_mat = np.array([
        [2, -1, -1, 0, 0, 0],
        [-1, 2, -1, 0, 0, 0],
        [-1, -1, 2, 0, 0, 0],
        [0, 0, 0, 3, 0, 0],
        [0, 0, 0, 0, 3, 0],
        [0, 0, 0, 0, 0, 3]
    ])

    result = get_yield_result(var, eq, Tmatrix=T_mat, Tmatrix_multipler=1 / 3, Cmatrix1=c_mat1, Cmatrix2=c_mat2,
                              sigma_min_range=-2000, sigma_max_range=2000, sigma_step=200)

    fig = go.Figure(data=go.Isosurface(
        x=result["x"],
        y=result["y"],
        z=result["z0"],
        value=result["value"],
        isomin=2,
        isomax=6,
    ))

    fig.show()
