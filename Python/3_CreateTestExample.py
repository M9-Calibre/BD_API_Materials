from API import *
from random import choice

token = authenticate("afonso", "1234")

material = get_material(1)

metadata = {
    "param1": "Some value",
    "param2": 10.4,
    "param3": 5,
    "xyz": 34.6
}

# No need to be the material owner
test = Test(material, "Test Name", metadata).register(token)

for test in get_tests():
    print(test.id, test.name)


