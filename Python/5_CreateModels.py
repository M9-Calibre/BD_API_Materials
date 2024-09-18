from vxformsapi.vxformsapi.API import *

token = authenticate_from_json("secret_login.json")


# yield_locus = Model("Yld2000", "YLD2000", "YLD2000", ["alpha1", "alpha2", "alpha3", "alpha4", "alpha5", "alpha6", "alpha7", "alpha8", "alpha"], "yield")
yield_locus = Model("Yld2004-18p", "YLD200418p", "YLD200418p", ["c12", "cc12", "c13", "cc13", "c21", "cc21", "c23", "cc23", "c31", "cc31", "c32", "cc32", "c44", "cc44", "c55", "cc55", "c66", "cc66", "alpha"], "yield")
# hard = Model("Swift Hardening", "SWIFT", "swift", ["k", "eps0", "swift_n"], "hardening")
# elastic = Model("Elastic", "ELASTIC", "sample", ["Young Modulus"], "elastic")


yield_locus = register_model(token, yield_locus)
# hard = register_model(token, hard)
# elastic = register_model(token, elastic)