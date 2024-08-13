from vxformsapi.vxformsapi.API import *

token = authenticate_from_json("secret_login.json")

material = get_material(2)

material_parameter = MaterialParam("Material Parameter Name", material)
register_material_param(token, material_parameter)



