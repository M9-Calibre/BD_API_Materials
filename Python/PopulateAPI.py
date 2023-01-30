from API import *
import json

# superuser must be created as indicated in README.md, change variables to your liking
username_staff = "afonso"
password_staff = "1234"

# Create some users

username_teresa = "teresa123"
password_teresa = "aseret321_"
first_name = "Teresa"
last_name = "Matos"
email = "teresa@example.pt"

x = register_user(username_teresa, password_teresa, first_name, last_name, email)
print(f"Register Teresa: {x.status_code}")

username_bob = "Bob123"
password_bob = "Bobby321_"
first_name = "Bob"
last_name = "Bobby"
email = "bob@example.pt"

x = register_user(username_bob, password_bob, first_name, last_name, email)
print(f"Register Bob: {x.status_code}")

# Get user list (should have 3 users)

user_list = get_user_list(username_staff,password_staff)
print(json.dumps(user_list, indent=3))

# Create come categories as superuser

# Upper
x = create_upper_category(username_staff, password_staff, "Metal")
print(f"Create upper category Metal: {x.status_code}")

x = create_upper_category(username_staff, password_staff, "Glass")
print(f"Create upper category Glass: {x.status_code}")

x = create_upper_category(username_staff, password_staff, "Other")
print(f"Create upper category Other: {x.status_code}")

# Middle
x = create_middle_category(username_staff, password_staff, "Metal", "Steel")
print(f"Create middle category Metal->Steel: {x.status_code}")

x = create_middle_category(username_staff, password_staff, "Metal", "Aluminium")
print(f"Create middle category Metal->Aluminium: {x.status_code}")

x = create_middle_category(username_staff, password_staff, "Metal", "Other")
print(f"Create middle category Metal->Other: {x.status_code}")

x = create_middle_category(username_staff, password_staff, "Glass", "Laminated Glass")
print(f"Create middle category Glass->Laminated Glass: {x.status_code}")

x = create_middle_category(username_staff, password_staff, "Glass", "Other")
print(f"Create middle category Glass->Other: {x.status_code}")

x = create_middle_category(username_staff, password_staff, "Other", "Other")
print(f"Create middle category Other->Other: {x.status_code}")

# Lower
x = create_lower_category(username_staff, password_staff, "Metal", "Steel", "Alloy Steel")
print(f"Create lower category Metal->Steel->Alloy Steel: {x.status_code}")

x = create_lower_category(username_staff, password_staff, "Metal", "Aluminium", "Aluminium 1100")
print(f"Create lower category Metal->Aluminium->Aluminium 1100: {x.status_code}")

x = create_lower_category(username_staff, password_staff, "Glass", "Laminated Glass", "EVA")
print(f"Create lower category Glass->Laminated Glass->EVA: {x.status_code}")

x = create_lower_category(username_staff, password_staff, "Other", "Other", "Other")
print(f"Create middle category Other->Other->Other: {x.status_code}")

# Check category trees

category_tree = get_category_tree(username_staff, password_staff)
print(json.dumps(category_tree, indent=3))

# Create some materials

with open("material.json", "rb") as f:
    material1 = json.load(f)

with open("material2.json", "rb") as f:
    material2 = json.load(f)

# Teresa submits a material
x = create_material(username_teresa, password_teresa, material1, upper_cat="Metal", middle_cat="Steel", cat="Alloy Steel")
print(f"Teresa creates a material: {x.status_code}")
material1_id = x.json()['id']
print(f"Material -> ID: {material1_id}, Owner: {x.json()['submitted_by']}")

# Bob submits a material
x = create_material(username_bob, password_bob, material2, upper_cat="Glass", middle_cat="Laminated Glass", cat="EVA")
print(f"Bob creates a material: {x.status_code}")
material2_id = x.json()['id']
print(f"Material -> ID: {material2_id}, Owner: {x.json()['submitted_by']}")

# Bob attempts to submit a material with the same name as Teresa's material
# This should fail
x = create_material(username_bob, password_bob, material1, upper_cat="Glass", middle_cat="Laminated Glass", cat="EVA")
print(f"Bob attempts to create a material (should fail): {x.status_code}, {x.reason}")

materials = get_material_list()
print(f"Number of materials: {len(materials)}")

# Test Creation
# Bob creates test for Teresas Alloy Steel material

dic_params_example = {
    "Camera": "FlirBackflyBFS-U3-51S5M-C",
    "Focal length": 12.5,
    "Image resolution": "2448x2048 px2",
    "Camera noise": "0.48% ofrange",
    "Working distance": "251 nm",
    "Image conversion factor": "0.05039 mm/px",
    "Average speckle size": "3px",
    "Subject size": "21 px",
    "Step size": "5px"
}
 
x = create_test(username_bob, password_bob, "Test A", material1_id, dic_params_example, None)
print(f"Bob submits a test: {x.status_code}, {x.reason}, {x.content}")
test_id = x.json()['id']
print(f"Test -> ID: {test_id}, Owner: {x.json()['submitted_by']}, Material: {x.json()['material']}")
