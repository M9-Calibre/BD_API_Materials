from vxformsapi.vxformsapi.API import *
import numpy as np

token = authenticate_from_json("secret_login.json")

# Obtain the corresponding Material Parameter
material_param = get_material_param(15, token)

# Obtain the params
hardening_model_params = material_param.hardening_model_params
hardening_params = hardening_model_params.params # {'k': 979.46, 'eps0': 0.00535, 'swift_n': 0.194}. Can be edited to calculate the function with different values
hardening_function = hardening_model_params.model.function_name # Swift Hardening

# Get points and plot the result
points = get_points(FunctionTypes.Hardening, hardening_function, hardening_params)

x = np.array(points["x"])
y = np.array(points["points"])

