from API import *

params1 = get_model_params(2)
params2 = get_model_params(4)
params3 = get_model_params(6)

params1.get_graph()
# params2.get_graph() -> not working, dif params
params3.get_graph()