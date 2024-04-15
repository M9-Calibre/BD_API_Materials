from vxformsapi.vxformsapi.API import *

token = authenticate("afonso", "1234")
print(token)


institutions = [
    # ("Université Bretagne Sud", "France"),
    # ("Katholieke Universiteit Leuven", "Belgium"),
    # ("Università Politecnica delle Marche", "Italy"),
    # ("MatchID", "Belgium"),
    # ("OCAS", "Belgium"),
    # ("Other", "No Country"),
]

for inst in institutions:
    institution = Institution(inst[0], inst[1])
    register_institution(token, institution)

# institution = Institution("Universidade de Aveiro", "Portugal")
# print(register_institution(token, institution))
