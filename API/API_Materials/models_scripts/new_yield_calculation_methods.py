import numpy as np
from numpy import linalg as LA
import ast
import operator as op
import re

# ---------------- Resolve the expression (TODO: Move to a new file) ----------------
operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}


def preprocess_abs(expr):
    # Uses regex to convert |x| to abs(x)
    return re.sub(r'\|(.+?)\|', r'abs(\1)', expr)


def eval_expr(expr):
    """
    >>> eval_expr('2^6')
    4
    >>> eval_expr('2**6')
    64
    >>> eval_expr('1 + 2*3**(4^5) / (6 + -7)')
    -5.0
    """
    preprocessed_expr = preprocess_abs(expr)
    val = eval_(ast.parse(preprocessed_expr, mode='eval').body)

    return val


def eval_(node):
    match node:
        case ast.Constant(value) if isinstance(value, (int, float, complex)):
            return value  # number
        case ast.BinOp(left, op, right):
            return operators[type(op)](eval_(left), eval_(right))
        case ast.UnaryOp(op, operand):  # e.g., -1
            return operators[type(op)](eval_(operand))
        case ast.Call(func, args, keywords) if func.id == 'abs':  # abs(x)
            return abs(eval_(args[0]))
        case _:
            raise TypeError(node)


def convert_expression(expression: str, variables: dict) -> float:
    for key, value in variables.items():
        expression = expression.replace(key, str(value))
    # print(f"{expression=}")
    return eval_expr(expression)


def convert_mat_expression(expression_mat: np.ndarray, variables: dict) -> np.ndarray:
    """Gets an expression containing variables and returns the result of the expression.

    Args:
        expression_mat (np.ndarray): Matrix composed by math expressions with variables (from the vars dictionary). Example: [["2 * 3 + 4", "var1 * var2", "| 3 * var1 |"], [...]].
        variables (dict): Variables used in the code that follow the structure "name": value.

    Returns:
        float: Result of the expression in the same, modified array.
    """
    for i in range(expression_mat.shape[0]):
        for j in range(expression_mat.shape[1]):
            str_expr = expression_mat[i, j]

            # Calculate the expression
            for key, value in variables.items():
                # If numerical array, force string
                if type(str_expr) != str:
                    str_expr = str(str_expr)
                # print(f"{str_expr=}")
                str_expr = str_expr.replace(key, str(value))
            str_expr = eval_expr(str_expr)
            # Save the result in the original matrix
            expression_mat[i, j] = str_expr

    # Convert the matrix from string to float (if it is not already)
    expression_mat = expression_mat.astype(float)
    return expression_mat


def create_l_matrix(Cmatrix: np.ndarray, Tmatrix: np.ndarray, variables: dict, Cmatrix_multiplier: float = 1,
                    Tmatrix_multiplier: float = 1) -> np.ndarray:
    """Given Cmatrix, Tmatrix and the variables dictionary, generate Lmatrix by multiplying C * T.

    Args:
        Cmatrix (np.ndarray)
        Tmatrix (np.ndarray)
        variables (dict)
        Cmatrix_multiplier (float): Constant float to multiply the Cmatrix.
        Tmatrix_multiplier (float): Constant float to multiply the Tmatrix.

    Returns:
        np.ndarray: The Lmatrix generated.
    """
    converted_C_matrix = convert_mat_expression(Cmatrix, variables) * Cmatrix_multiplier
    converted_T_matrix = convert_mat_expression(Tmatrix, variables) * Tmatrix_multiplier

    return converted_C_matrix * converted_T_matrix


def convert_to_3d_matrix(matrix: np.ndarray, force_3d: bool = True) -> np.ndarray:
    """Converts a matrix with shape (3, 3) to (6, 6). It does nothing to a matrix of shape (6, 6), and it raises a TypeError with a different shape matrix.

    Args:
        matrix (np.ndarray): A matrix with shape (3, 3) or (6, 6).
        force_3d (bool): if True, the program detects a 2D Lmatrix and converts automatically to 3D. If False, it raises a ValueError.

    Raises:
        TypeError: A matrix with different shape.

    Returns:
        new_matrix (np.ndarray): The new converted matrix.
    """

    # First check the dimensions if it is a valid input
    match matrix.shape:
        case (3, 3):
            if force_3d:
                # apply convertion
                new_matrix = np.array([[matrix[0, 0], matrix[0, 1], 0, 0, 0, 0],
                                       [matrix[0, 1], matrix[1, 1], 0, 0, 0, 0],
                                       [0, 0, 0, 0, 0, 0],
                                       [0, 0, 0, matrix[2, 2], 0, 0],
                                       [0, 0, 0, 0, 0, 0],
                                       [0, 0, 0, 0, 0, 0]])
            else:
                raise TypeError(
                    f"Matrix with shape (3, 3) tried to go to 3D with 'force_3d' False. Change its shape to (6, 6) or 'force_3d' to True.")
        case (6, 6):
            # do nothing, it is already fixed
            new_matrix = matrix
        case _:
            raise TypeError(f"Matrix with shape {matrix.shape} tried to go to 3D. It shape should be (3, 3) or (6, 6).")

    return new_matrix


def get_eigenvalues(matrix: np.ndarray) -> np.ndarray:
    """Given a sigma matrix (vector), return its eigenvalues.

    Args:
        matrix (np.ndarray): Sigma vector.

    Returns:
        np.ndarray: Eigen values array.
    """
    new_matrix = np.array([[matrix[0][0], matrix[1][0], 0, 0, 0, 0],
                           [matrix[1][0], matrix[3][0], 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0]], dtype=float)

    return LA.eigvals(new_matrix)


# ---------------- Yield Func ----------------

def get_yield_result(variables: dict, equation: str, Cmatrix1: np.ndarray = None, Cmatrix2: np.ndarray = None,
                     Tmatrix: np.ndarray = None, Tmatrix_multipler: float = 1, Lmatrix1: np.ndarray = None,
                     Lmatrix1_multiplier: float = 1, Lmatrix2: np.ndarray = None, Lmatrix2_multipler: float = 1,
                     sigma_min_range: float = -1000, sigma_max_range: float = 1000, sigma_step: float = 10,
                     shears: np.ndarray = None, shear_step: float = None, division_ration = 1,
                     force_3d: bool = True) -> np.ndarray:
    """_summary_
    
    Args:
        variables (dict): Variables used in the code that follow the structure "name": value.
        stress (float): _description_
        Xmatrix (np.ndarray): Every element is a string composed by the format: "[IDX1]_[IDX2]". Those are the indexes to be obtained from the Cmatrix.
        Cmatrix (np.ndarray) (optional): Values to be used in the Xmatrix. If Cmatrix is None, it should be calculated using the C = L/T formula (confirmar???).
        Lmatrix (np.ndarray) (optional): Values in string to be used in the Xmatrix if Cmatrix is not provided. Those values may be math expressions with variables (from the vars dictionary). Every element should be spaced out by a empty space. Examples: "2 * 3 + 4", "var1 * var2", "| 3 * var1 |".
        
        
        force_3d (bool): if True, the program detects a 2D Lmatrix and converts automatically to 3D. If False, it raises a ValueError.
    """

    # Output already in the desired format
    datapoints = {
        "x": [],
        "y": [],
        "z": [],
        "value": [],
        "shear_x": [],
        "shear_y": [],
        "shears": {}  # Dict of arrays of values. The key is the shear value.
    }

    # Default shears values equals % of the z value
    if shears is None:
        shears = np.array([0, 0.2, 0.4, 0.6]) * sigma_max_range
        shear_step = sigma_step

    # If not L, calculate L' = C' * T
    if Lmatrix1 is not None:
        Lmatrix1 = convert_mat_expression(Lmatrix1, variables) * Lmatrix1_multiplier
    if Lmatrix1 is None:
        if Cmatrix1 is None or Tmatrix is None: raise ValueError("L' is not defined, please define C' and T")
        Lmatrix1 = create_l_matrix(Cmatrix1, Tmatrix, variables, Tmatrix_multiplier=Tmatrix_multipler)

    # Same thing for L'' and C''
    if Lmatrix2 is not None:
        Lmatrix2 = convert_mat_expression(Lmatrix2, variables) * Lmatrix2_multipler
    if Lmatrix2 is None:
        if Cmatrix2 is None or Tmatrix is None: raise ValueError("L'' is not defined, please define C'' and T")
        Lmatrix2 = create_l_matrix(Cmatrix2, Tmatrix, variables, Tmatrix_multiplier=Tmatrix_multipler)

    # Verify if L matrixes are 2D, and then convert to 3D
    converted_Lmatrix1 = convert_to_3d_matrix(Lmatrix1, force_3d)
    converted_Lmatrix2 = convert_to_3d_matrix(Lmatrix2, force_3d)

    # Create Xs, Ys, Zs combination array
    xs, ys, zs = np.meshgrid(np.arange(sigma_min_range, sigma_max_range, sigma_step),
                             np.arange(sigma_min_range, sigma_max_range, sigma_step),
                             np.arange(sigma_min_range, sigma_max_range, sigma_step))

    # Prepare sigma vector
    for i in range(len(xs)):
        for j in range(len(ys)):
            for k in range(len(zs)):
                x = xs[i, j, k]
                y = ys[i, j, k]
                z = zs[i, j, k]

                # σ = [S11, S22, 0, S12, 0, 0]
                sigma_vector = np.array([x, y, 0, z, 0, 0]).reshape(6, 1)  # convert to be a vertical vector

                # Apply multiplication: X' = L' * Sigma, X'' = L'' * Sigma
                Xmatrix1 = np.matmul(converted_Lmatrix1, sigma_vector)
                Xmatrix2 = np.matmul(converted_Lmatrix2, sigma_vector)

                # Get Eigen Values
                eigen_values = [get_eigenvalues(Xmatrix1), get_eigenvalues(Xmatrix2)]

                # Create variables dict to calculate in the equation
                equation_variables = {}  # {"x11": val, "x12": val2, etc..} "x1" -> x', "x2" -> x''
                for x_type in range(1, 3):
                    for idx in range(1, 7):
                        equation_variables[f"x{x_type}{idx}"] = eigen_values[x_type - 1][idx - 1]

                # Merge variables with original variables
                equation_variables.update(variables)

                # Apply on the equation
                equation_result = convert_expression(equation, equation_variables)

                # Add points to the output dictionary
                datapoints["x"].append(x)
                datapoints["y"].append(y)
                datapoints["z"].append(z)
                datapoints["value"].append(equation_result / division_ration)

    # Prepare shears' axis
    shear_xs, shear_ys = np.meshgrid(np.arange(sigma_min_range, sigma_max_range, shear_step),
                                     np.arange(sigma_min_range, sigma_max_range, shear_step))

    datapoints["shear_x"] = shear_xs.ravel()
    datapoints["shear_y"] = shear_ys.ravel()

    # Calculate shears' values
    for k in range(len(shears)):
        z = shears[k]

        datapoints["shears"][z] = {
            "z": [],  # Used to avoid this repetition on the receiving end. Ex: [0, 0, 0, 0, ... // 0.2, 0.2, 0.2, ...]
            "value": []
        }

        for i in range(len(shear_xs)):
            for j in range(len(shear_ys)):
                x = shear_xs[i, j]
                y = shear_ys[i, j]

                # σ = [S11, S22, 0, S12, 0, 0]
                sigma_vector = np.array([x, y, 0, z, 0, 0]).reshape(6, 1)  # convert to be a vertical vector

                # Apply multiplication: X' = L' * Sigma, X'' = L'' * Sigma
                Xmatrix1 = np.matmul(converted_Lmatrix1, sigma_vector)
                Xmatrix2 = np.matmul(converted_Lmatrix2, sigma_vector)

                # Get Eigen Values
                eigen_values = [get_eigenvalues(Xmatrix1), get_eigenvalues(Xmatrix2)]

                # Create variables dict to calculate in the equation
                equation_variables = {}  # {"x11": val, "x12": val2, etc..} "x1" -> x', "x2" -> x''
                for x_type in range(1, 3):
                    for idx in range(1, 7):
                        equation_variables[f"x{x_type}{idx}"] = eigen_values[x_type - 1][idx - 1]

                # Merge variables with original variables
                equation_variables.update(variables)

                # Apply on the equation
                equation_result = convert_expression(equation, equation_variables)

                # Add points to the output dictionary
                datapoints["shears"][z]["value"].append(equation_result / division_ration / 1)

                # Add Z point do avoid repetition of shear from the other end
                datapoints["shears"][z]["z"].append(z)

    return datapoints


def get_non_matrix_equation(variables: dict, equation: str, input_min=0, input_max=1, input_step=0.01):
    datapoint = {
        "points": [],
        "x": []
    }

    input_arr = np.arange(input_min, input_max, input_step)

    for inpt in input_arr:
        datapoint["x"].append(inpt)
        variables["inpt"] = inpt

        equation_result = convert_expression(equation, variables)

        datapoint["points"].append(equation_result)

    return datapoint


# --------------------------


if __name__ == "__main__":
    main1()
