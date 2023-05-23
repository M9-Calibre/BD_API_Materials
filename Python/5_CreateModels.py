from API import *

token = authenticate("afonso", "1234")

yld2000 = Model("Yield Code 2000", "YLD2000", ["alpha1", "alpha2", "alpha3", "alpha4", "alpha5", "alpha6", "alpha7", "alpha8", "a"])
yield_locus = Model("Yeild Locus", "YLDLOC", ["F", "H", "N", "K", "eps0", "n_swift"])

yld2000 = register_model(token, yld2000)
yield_locus = register_model(token, yield_locus)