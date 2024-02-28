from VxFormsAPI.VxFormsAPI.API import *

token = authenticate("afonso", "1234")
print(token)

institution = Institution("Universidade de Aveiro", "Portugal")
print(register_institution(token, institution))
