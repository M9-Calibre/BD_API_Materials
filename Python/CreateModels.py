from API import *

token = authenticate("afonso", "1234")

yld2000 = Model("Yield Code 2000", "YLD2000", ["alpha1", "alpha2", "alpha3", "alpha4", "alpha5", "alpha6", "alpha7", "alpha8", "a"])
#yld2004 = Model("Yield Code 2004", "YLD2004", ["alpha1", "alpha2", "alpha3", "alpha4", "alpha5", "alpha6", "alpha7", "alpha8", "a"]) # wrong input params
yield_locus = Model("Yeild Locus", "YLDLOC", ["F", "H", "N", "K", "eps0", "n_swift"])

yld2000 = register_model(token, yld2000)
#yld2004 = register_model(token, yld2004)
yield_locus = register_model(token, yield_locus)

print(yld2000.tag, yld2000.input, yld2000.id)
#print(yld2004.tag, yld2004.input, yld2004.id)
print(yield_locus.tag, yield_locus.input, yield_locus.id)