from API import *

token = authenticate("afonso", "1234")

yield_locus = get_model(7)
hard = get_model(8)
elastic = get_model(9)

test = get_test(1)

locus_params = {"f": 0.3748, "h": 0.4709, "g": 1 - 0.4709, "n": 1.1125}
params3 = ModelParams(test, yield_locus, locus_params)

hard_params = {"k": 979.46, "eps0": 0.00535, "swift_n": 0.194}
params4 = ModelParams(test, hard, hard_params)

elastic_params = {}
params5 = ModelParams(test, elastic, elastic_params)

params3 = register_model_params(token, params3)
params4 = register_model_params(token, params4)
params5 = register_model_params(token, params5)