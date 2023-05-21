from API import *
from random import choice

token = authenticate("afonso", "1234")

material = choice(get_materials())

metadata = {
    "param1": "Some value",
    "param2": 10.4,
    "param3": 5
}

test = Test(material, "Test Name 7", metadata)

test = register_test(token, test)

for test in get_tests():
    print(test.id, test.name)


