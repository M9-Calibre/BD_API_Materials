from vxformsapi.vxformsapi.API import *

token = authenticate_from_json("secret_login.json")
print(token)


institutions = [
    ("Universidade de Aveiro", "Portugal"),
    ("Université Bretagne Sud", "France"),
    ("Katholieke Universiteit Leuven", "Belgium"),
    ("Università Politecnica delle Marche", "Italy"),
    ("MatchID", "Belgium"),
    ("OCAS", "Belgium"),
    ("Other", "No Country"),
]

for inst in institutions:
    print("Registering institution: ", inst)
    institution = Institution(inst[0], inst[1])
    register_institution(token, institution)