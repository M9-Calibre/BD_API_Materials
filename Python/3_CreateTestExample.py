from API import *
from random import choice

token = authenticate("tester", "secretPass1234")

# Creating a test

# ID of the material which the new test refers to
material = get_material(3)

# Test metadata
metadata = {
    "param1": "Some value",
    "param2": 10.4,
    "param3": 5,
    "xyz": 34.6
}

# No need to be the material owner
test = Test(material, "Test Name", metadata).register(token)

# Fetch all tests
for test in get_tests():
    print(test.id, test.name)


