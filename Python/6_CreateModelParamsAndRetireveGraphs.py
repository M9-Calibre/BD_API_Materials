from vxformsapi.vxformsapi.API import *

token = authenticate_from_json("secret_login.json")

# Material Parameter Fields
material_param_name = "New Material Parameter"
extra_information = "More information."
source_url = "https://www.ua.pt"
inverse_method = get_inverse_method(1)
private = False
user_groups = get_user_groups(token)

material = get_material(1)

yield_locus = get_model(1)
hard = get_model(2)
elastic = get_model(4)

locus_params = {"f": 0.3748, "h": 0.4709, "g": 1 - 0.4709, "n": 1.1125}
yield_model = ModelParams(yield_locus, locus_params)

hard_params = {"k": 979.46, "eps0": 0.00535, "swift_n": 0.194}
hard_model = ModelParams(hard, hard_params)

elastic_params = {"Young Modulus": 1.0}
elastic_model = ModelParams(elastic, elastic_params)

material_param = MaterialParam(name=material_param_name, material=material, extra_information=extra_information, source_url=source_url, inverse_method=inverse_method, private=private, edit_groups=user_groups, read_groups=user_groups, delete_groups=user_groups, hardening_model_params=hard_model, yield_model_params=yield_model, elastic_model_params=elastic_model)

register_material_param(token, material_param)




