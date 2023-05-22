from API import *

token = authenticate("afonso", "1234")

yld2000 = get_model(2)
yld2004 = get_model(4)
yield_locus = get_model(6)

test = get_test(8)

yld_params = {"alpha1": 1.011, "alpha2": 0.964, "alpha3": 1.191, "alpha4": 0.995, "alpha5": 1.010, "alpha6": 1.018, "alpha7": 0.977,
              "alpha8": 0.935, "a": 6}
params1 = ModelParams(test, yld2000, yld_params)
#params2 = ModelParams(test, yld2004, yld_params)
locus_params = {"F": 0.3748, "H": 0.4709, "N": 1.1125, "K": 979.46, "eps0": 0.00535, "n_swift": 0.194}
params3 = ModelParams(test, yield_locus, locus_params)

params1 = register_model_params(token, params1)
#params2 = register_model_params(token, params2)
params3 = register_model_params(token, params3)

#params1.get_graph()
#params2.get_graph()
#params3.get_graph()