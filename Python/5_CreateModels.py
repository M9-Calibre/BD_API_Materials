from VxFormsAPI.VxFormsAPI.API import *

token = authenticate("afonso", "1234")


yield_locus = Model("Yeild Locus", "YLDLOC", "sample", ["f", "h", "g", "n"], "yield")
hard = Model("Swift Hardening", "SWIFT", "swift", ["k", "eps0", "swift_n"], "hardening")
elastic = Model("Elastic", "ELASTIC", "sample", ["multiplier"], "elastic")


yield_locus = register_model(token, yield_locus)
hard = register_model(token, hard)
elastic = register_model(token, elastic)