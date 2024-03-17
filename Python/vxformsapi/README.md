![VxForms Logo](https://lh3.googleusercontent.com/proxy/k5_JT4Bb1BHN5EJPBTft36rfyjiKCfTAQ70QqRI0VQwdY9lUq13lbcr5pNS_k2uAK-ZYGFSNTpqO9Coo_N2O881ZPM535YFpAKKm15YPJ270yzdw8dZkm5GVxhybjjU "VxFormsLogo")

**vxformsapi** is a Python library to enable a high-level interaction with the VxForms Material's [API](http://193.137.84.5/api/swagger/) without the need of the VXForms Materials's [Website](http://193.137.84.5).

The project is being developed in association with University of Aveiro - Portugal, and it is currently mantained by the research grant team.

# Installation
## Dependencies
vxformsapi automatically installs the following dependencies:
- pandas
- requests

## User Installation
```
pip install vxformsapi
```

# Documentation
## Authentication
Some methods will require the `login_token` argument to allow for permissions or uploads. There are 2 ways to obtain the token:
```python
from vxformsapi.API import *
login_token = authenticate("username_value", "password_value") 
# Uses hardcoded information. 
# Not recommended if the script is associated with a repository for security reasons.

login_token_json = authenticate_from_json("json_filename.json")
# Recommended approach for security.
# Uses information provided in the json file that follows the following structure:
# {
#   username: "username_value",
#   password: "password_value"
# }

```
The login_token can now be used in any necessary method passing it as an argument.

## Examples

### Create Material
```python
from vxformsapi.API import *

token = authenticate_from_json("secrets.json")

# Creating a material

thermal_expansion_coef = {
    "20": 1.15,
    "200": 1.27,
    "300": 1.32
}

specific_heat_capacity = {
    "20": 430,
    "200": 499,
    "300": 517
}

thermal_conductivity = {
    "20": 34.9,
    "200": 38,
    "300": 37.8
}

tp = ThermalProperties(thermal_expansion_coef=thermal_expansion_coef, specific_heat_capacity=specific_heat_capacity, 
                       thermal_conductivity=thermal_conductivity)

elastic_modulus = {
    "-100": 217,
    "20": 214,
    "200": 202,
    "300": 192
}

poissons_ratio = {
    "20": 0.283,
    "200": 0.292,
    "300": 0.294
}

shear_modulus = {
    "20": 82.8,
    "200": 77.9,
    "300": 74.9
}

yield_strength = {
    "20": 280,
    "200": 224,
    "300": 221
}

mp = MechanicalProperties(tensile_strength=500, thermal_conductivity=46.8, reduction_of_area=41.4, cyclic_yield_strength=250, 
                          elastic_modulus=elastic_modulus, poissons_ratio=poissons_ratio, shear_modulus=shear_modulus,
                          yield_strength=yield_strength)

chemical_composition = {
    "C": 0.105,
    "Si": 0.24,
    "Mn": 0.43,
    "P": 0.012,
    "S": 0.014,
    "Cr": 2.29,
    "Mo": 1.004,
    "Ni": 0.16,
    "Cu": 0.9,
    "Ti": 0.03,
    "V": 0.02,
    "Al": 0.02
}

pp = PhysicalProperties(chemical_composition=chemical_composition)

category = get_category_by_name("Alloy Steel")

material = Material(name="EN 10028-2 Grade 10CrMo9-10 normalized and tempered (+NT)", category=category,
                    source="Boller C, Seeger T. Materials data for cyclic loading, Part B. Amsterdam: Elsevier; 1987",
                    designation="DIN 10 CrMo 9 10", heat_treatment="Normalized & tempered, 950°C/30min air, 750°C/2h air", 
                    thermal_properties=tp, mechanical_properties=mp, physical_properties=pp)
material.register(token)

# Fetching the stored materials

for material in get_materials():
    print(material.id, material.name, material.submitted_by, material.date, material.user)
```

### Create Test
```python
from vxformsapi.API import *

token = authenticate_from_json("secrets.json")

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
test = Test(material, "Test Name", metadata)
test.register(token)

# Fetch all tests
for test in get_tests():
    print(test.id, test.name)
```

### Upload DIC Files
```python
from vxformsapi.API import *
import os

token = authenticate_from_json("secrets.json")

# Directory where the DIC files and load data are stored, consult the user manual for formatting and naming of the files
dir = "DIC_files\\" 

# ID of the test we wish to populate
test_id = 3

f = []
for (dirpath, dirnames, filenames) in os.walk(dir):
    f.extend(filenames)
    break

file_mappings = {name : open(dir+name, "rb") for name in f}

test = get_test(test_id)

# Upload the data
test.upload_test_data(token, file_mappings, file_format=UploadFileFormat.MatchId, _3d=False)

# Download the data as a ZIP file
test.download_test_data()

# Download the data as a pandas dataframe
stages_df = test.load_test_data()

print(stages_df.keys())
print(stages_df[2])
```

## API Methods
### Materials
`get_materials`: Retrieve a page of materials.
```
Parameters
----------
page (optional) : int
    Page number
page_size (optional) : int
    Number of materials per page
ordering (optional) : MaterialOrderings
    Ordering of the material list (available orderings: id, date, name, upper/middle/lower_category)
ascending (optional) : bool
    Defines ordering direction
search (optional) : str
    Filters materials by inclusion of the specified string in the material name or description
```

`get_material`: Retrieve a material by id.
```
Parameters
----------
material_id : int
    The id of the material to be fetched
```

`register_material`: Save a material to the database.
```
Parameters
----------
material : Material
    The material to be saved (name must be unique)
login_token : str
    The log-in token that can be retrieved from the authenticate function
```
### Categories
`get_categories`: Retrieve all categories.
```
Parameters
----------
mode (optional) : CategoriesDisplayModes
    Either return the categories in a tree-like object or return three lists for each type of category (upper, middle, lower)
```

`get_category`: Retrieve a category by id.
```
Parameters
----------
category_id : int
    The id of the category to be fetched
level (optional) : CategoryLevel
    The level of the category to be fetched (by default, lower)
```

`get_category_by_name`: Retrieve a category by name.
```
Parameters
----------
category_name : str
    The name of the category to be fetched
level (optional) : CategoryLevel
    The level of the category to be fetched (by default, lower)
```

`register_category`: Save a category to the database.
```
Parameters
----------
admin_token : str
    The log-in token that can be retrieved from the authenticate function (must be admin)
category : Category
    The category to be saved 
```

### Tests
`register_test`: Save a test to the database.
```
Parameters
----------
login_token : str
    The log-in token that can be retrieved from the authenticate function
test : Test
    The test to be saved (name must be unique within the material's tests)
```

`get_tests`: Retrieve a page of tests.
```
Parameters
----------
page (optional) : int
    Page number
page_size (optional) : int
    Number of tests per page
material (optional) : int
    Filter by material (id)
submitted_by (optional) : int
    Filter by user (id)  
```

`get_test`: Retrieve a test by id.
```
Parameters
----------
test_id : int
    The id of the test to be fetched
```

### Models
`get_model`: Retrieve a model by id.
```
Parameters
----------
model_id : int
    The id of the model to be fetched
```

`register_model`: Save a model to the database.
```
Parameters
----------
admin_token : str
    The log-in token that can be retrieved from the authenticate function (must be admin)
model : Model
    The model to be saved 
```

### ModelParams
`get_model_params`: Retrieve model parameters by id.
```
Parameters
----------
modelp_id : int
    The id of the model parameters to be fetched
```

`register_model_params`: Save model parameters to the database.
```
Parameters
----------
login_token : str
    The log-in token that can be retrieved from the authenticate function
modelp : ModelParams
    The model parameters to be saved 
```

## API Enums
- `MaterialOrderings(Id, Date, Name, UpperC, MiddleC, LowerC)`
- `CategoriesDisplayModes(Tree, List)`
- `CategoryLevel(Upper, Middle, Lower)`
- `UploadFileFormat(MatchId, Aramis)`