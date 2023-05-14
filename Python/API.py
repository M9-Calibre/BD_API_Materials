import requests
import json
from enum import Enum

#URL = 'http://afonsocampos100.pythonanywhere.com/'
URL = 'http://127.0.0.1:8000'

class MaterialOrderings(Enum):
    Id = "id"
    Date = "entry_date"
    Mat_Id = "mat_id"
    Name = "name"

class CategoriesDisplayModes(Enum):
    Tree = "tree"
    List = "list"

class APIFailedRequest(Exception):
    def __init__(self, response : requests.Response) -> None:
        self.status_code = response.status_code
        self.reason = response.reason
        self.message = f'Invalid request. (Status Code {self.status_code}: {self.reason})'
        super().__init__(self.message)

class UpperCategory():
    def __init__(self, name : str) -> None:
        self.id = None
        self.name = name

    def __str__(self) -> str:
        return f"Upper Category {self.id}: {self.name}"

class MiddleCategory():
    def __init__(self, upper : UpperCategory, name : str) -> None:
        self.id = None
        self.upper = upper
        self.name = name

    def __str__(self) -> str:
        return f"Middle Category {self.id}: {self.name}"

class LowerCategory():
    def __init__(self, middle : MiddleCategory, name : str) -> None:
        self.id = None
        self.middle = middle
        self.name = name

    def __str__(self) -> str:
        return f"Lower Category {self.id}: {self.name}"

class ThermalProperties():
    def __init__(self, thermal_expansion_coef : dict[str, float] = None, specific_heat_capacity : dict[str, float] = None, thermal_conductivity : dict[str, float] = None) -> None:
        self.thermal_expansion_coef = thermal_expansion_coef
        self.specific_heat_capacity = specific_heat_capacity
        self.thermal_conductivity = thermal_conductivity

    def to_dict(self) -> dict:
        json_data = self.__dict__
        json_data["thermal_conductivity_tp"] = json_data.pop("thermal_conductivity")
        return json_data

    @classmethod
    def load_json(cls, thermal_properties_json : dict):
        thermal_properties = ThermalProperties()
        thermal_properties.thermal_expansion_coef = thermal_properties_json.get("thermal_expansion_coef", None)
        thermal_properties.specific_heat_capacity = thermal_properties_json.get("specific_heat_capacity", None)
        thermal_properties.thermal_conductivity = thermal_properties_json.get("thermal_conductivity_tp", None)
        return thermal_properties

class MechanicalProperties():
    def __init__(self, tensile_strength : int = None, thermal_conductivity : float = None, reduction_of_area : float = None, 
                 cyclic_yield_strength : int = None, elastic_modulus : dict[str, float] = None, poissons_ratio : dict[str, float] = None, shear_modulus : dict[str, float] = None, 
                 yield_strength : dict[str, float] = None) -> None:
        self.tensile_strength = tensile_strength
        self.thermal_conductivity = thermal_conductivity
        self.reduction_of_area = reduction_of_area
        self.cyclic_yield_strength = cyclic_yield_strength
        self.elastic_modulus = elastic_modulus
        self.poissons_ratio = poissons_ratio
        self.shear_modulus = shear_modulus
        self.yield_strength = yield_strength

    def to_dict(self) -> dict:
        json_data = self.__dict__
        json_data["thermal_conductivity_mp"] = json_data.pop("thermal_conductivity")
        return json_data

    @classmethod
    def load_json(cls, mechanical_properties_json : dict):
        mechanical_properties = MechanicalProperties()
        mechanical_properties.tensile_strength = mechanical_properties_json.get("tensile_strength", None)
        mechanical_properties.thermal_conductivity = mechanical_properties_json.get("thermal_conductivity_mp", None)
        mechanical_properties.reduction_of_area = mechanical_properties_json.get("reduction_of_area", None)
        mechanical_properties.cyclic_yield_strength = mechanical_properties_json.get("cyclic_yield_strength", None)
        mechanical_properties.elastic_modulus = mechanical_properties_json.get("elastic_modulus", None)
        mechanical_properties.poissons_ratio = mechanical_properties_json.get("poissons_ratio", None)
        mechanical_properties.shear_modulus = mechanical_properties_json.get("shear_modulus", None)
        mechanical_properties.yield_strength = mechanical_properties_json.get("yield_strength", None)
        return mechanical_properties

class PhysicalProperties():
    def __init__(self, chemical_composition : dict[str, float] = None) -> None:
        self.chemical_composition = chemical_composition

    def to_dict(self) -> dict:
        return self.__dict__

    @classmethod
    def load_json(cls, physical_properties_json : dict):
        physical_properties = PhysicalProperties()
        physical_properties.chemical_composition = physical_properties_json.get("chemical_composition", None)
        return physical_properties

class Material():
    def __init__(self, name : str, category : LowerCategory, mat_id : int, source : str, designation : str, heat_treatment : str, 
                 description : str = None, thermal_properties : ThermalProperties = None, mechanical_properties : MechanicalProperties = None, 
                 physical_properties : PhysicalProperties = None) -> None:
        self.id = None
        self.submitted_by = None
        self.date = None
        self.name = name
        self.category = category
        self.mat_id = mat_id
        self.source = source
        self.designation = designation
        self.heat_treatment = heat_treatment
        self.description = description
        self.thermal_properties = thermal_properties
        self.mechanical_properties = mechanical_properties
        self.physical_properties = physical_properties

    def __str__(self) -> str:
        return f"Material {self.id}: {self.name}"

    def to_json(self) -> str:
        material_json = self.__dict__
        material_json["category"] = self.category.id
        material_json["thermal_properties"] = self.thermal_properties.to_dict()
        material_json["mechanical_properties"] = self.mechanical_properties.to_dict()
        material_json["physical_properties"] = self.physical_properties.to_dict()
        return json.dumps(material_json, indent=2)

    @classmethod
    def load_json(cls, material_json : dict):
        id = material_json["id"]
        name = material_json["name"]
        upper_category = UpperCategory(material_json["upper_category"])
        upper_category.id = material_json["upper_category_id"]
        middle_category = MiddleCategory(upper_category, material_json["middle_category"])
        middle_category.id = material_json["middle_category_id"]
        category = LowerCategory(middle_category, material_json["lower_category"])
        category.id = material_json["category"]
        mat_id = material_json["mat_id"]
        source = material_json["source"]
        designation = material_json["designation"]
        heat_treatment = material_json["heat_treatment"]
        description = material_json.get("description", None)
        thermal_properties = ThermalProperties.load_json(material_json["thermal_properties"]) if "thermal_properties" in material_json else None
        physical_properties = PhysicalProperties.load_json(material_json["physical_properties"]) if "physical_properties" in material_json else None
        mechanical_properties = MechanicalProperties.load_json(material_json["mechanical_properties"]) if "mechanical_properties" in material_json else None
        
        material = Material(name, category, mat_id, source, designation, heat_treatment, description, thermal_properties, mechanical_properties, physical_properties)
        material.id = id
        return material
    
def authenticate(username : str, password : str) -> str:
    """Login with existing user credentials and retrieve an authentication token.

    Parameters
    ----------
    username : str
        The username of the user
    password : str
        The password of the user
    
    """

    json_req_body = {
        "username" : username,
        "password" : password
    }
    login = requests.post(f"{URL}/users/login/", json=json_req_body)

    if login.status_code != 200:
        raise APIFailedRequest(login)
    
    token = login.json()["token"]

    print("authenticate: Authentication successful.")

    return token

def get_materials(page : int = 1, page_size : int = 10, ordering : MaterialOrderings = MaterialOrderings.Id, ascending : bool = True, search : str = None) -> list[Material]:
    """Retrieve a page of materials.

    Parameters
    ----------
    page (optional) : int
        Page number
    page_size (optional) : int
        Number of materials per page
    ordering (optional) : MaterialOrderings
        Ordering of the material list (available orderings: id, date, mat_id, name)
    ascending (optional) : bool
        Defines ordering direction
    search (optional) : str
        Filters materials by inclusion of the specified string in the material name or description
    
    """
    
    url = f"{URL}/materials/?page={page}&page_size={page_size}&ordering={'' if ascending else '-'}{ordering.value}{'&search='+search if search else ''}"

    response = requests.get(url)

    if response.status_code != 200:
        raise APIFailedRequest(response)
    
    results = response.json()["results"]

    materials = list[Material]()
    for material_json in results:
        materials.append(Material.load_json(material_json))

    print(f"get_materials: Successfully retrieved {len(materials)} materials.")

    return materials

def get_categories(mode : CategoriesDisplayModes = CategoriesDisplayModes.List):
    """Retrieve all categories.
    
    Parameters
    ----------
    mod (optional) : CategoriesDisplayModes
        Either return the categories in a tree-like object or return three list for each type of category (upper, middle, lower)

    """

    response = requests.get(f"{URL}/categories/upper/")

    if response.status_code != 200:
        raise APIFailedRequest(response)
    
    json_data = response.json()

    if mode == CategoriesDisplayModes.List:
        result = dict()
        result["upper"] = list()
        result["middle"] = list()
        result["lower"] = list()
        for upper_category in json_data:
            id = upper_category["id"]
            name = upper_category["category"]
            up_category = UpperCategory(name)
            up_category.id = id
            result["upper"].append(up_category)
            for middle_category in upper_category["mid_categories"]:
                id = middle_category["id"]
                name = middle_category["category"]
                mid_category = MiddleCategory(up_category, name)
                mid_category.id = id
                result["middle"].append(mid_category)
                for lower_category in middle_category["lower_categories"]:
                    id = lower_category["id"]
                    name = lower_category["category"]
                    category = LowerCategory(mid_category, name)
                    category.id = id
                    result["lower"].append(category)
    elif mode == CategoriesDisplayModes.Tree:
        result = dict()
        for upper_category in json_data:
            id = upper_category["id"]
            name = upper_category["category"]
            up_category = UpperCategory(name)
            up_category.id = id
            result[up_category] = dict()
            for middle_category in upper_category["mid_categories"]:
                id = middle_category["id"]
                name = middle_category["category"]
                mid_category = MiddleCategory(up_category, name)
                mid_category.id = id
                result[up_category][mid_category] = list()
                for lower_category in middle_category["lower_categories"]:
                    id = lower_category["id"]
                    name = lower_category["category"]
                    low_category = LowerCategory(mid_category, name)
                    low_category.id = id
                    result[up_category][mid_category].append(low_category)

    return result

def register_material(login_token : str, material : Material):
    """Save a material to the database.

    Parameters
    ----------
    material : Material
        The material to be saved (name and mat_id must be unique)
    login_token : str
        The log-in token that can be retrieved from the authenticate function
    
    """

    response = requests.post(f"{URL}/materials/", headers={"Authentication": f"Token {login_token}"})

    if response.status_code != 201:
        raise APIFailedRequest(response)
    
    print(response.json())


def login_user(username, password):
    
    json_req_body = {
        "username" : username,
        "password" : password
    }

    return requests.post(f"{URL}/users/login/", json=json_req_body)

# Can only be performed by a superuser
# Steps to create superuser in the README.md
def get_user_list(username, password):
    return requests.get(f"{URL}/users/?format=json", auth=(username,password)).json()

# Can only be performed by a superuser
# Steps to create superuser in the README.md
def create_upper_category(username, password, category_name):
    return requests.post(f"{URL}/categories/upper/", auth=(username,password), json={"category":category_name})

# Can only be performed by a superuser
# An upper category must already be created to link to
def create_middle_category(username, password, upper_category, category_name):
    upper_category_id = get_upper_category_id(username, password, upper_category)
    return requests.post(f"{URL}/categories/middle/", auth=(username,password), json={"category":category_name,"upper_category":upper_category_id})

# Can only be performed by a superuser
# A middle category must already be created to link to
def create_lower_category(username, password, upper_category, middle_category, category_name):
    middle_category_id = get_middle_category_id(username, password, upper_category, middle_category)
    return requests.post(f"{URL}/categories/lower/", auth=(username,password), json={"category":category_name,"upper_category":middle_category_id})

def get_category_tree(username, password):
    return requests.get(f"{URL}/categories/upper/?format=json", auth=(username,password)).json()['results']

def get_upper_category_id(username, password, upper_category):
    results = requests.get(f"{URL}/categories/upper/?upper_category={upper_category}&format=json", 
                            auth=(username,password)).json()['results']
    if len(results) != 1:
        return None
    return results[0]['id']

def get_middle_category_id(username, password, upper_category, middle_category):
    results = requests.get(f"{URL}/categories/middle/?upper_category={upper_category}&middle_category={middle_category}&format=json", 
                            auth=(username,password)).json()['results']
    if len(results) != 1:
        return None
    return results[0]['id']

def get_lower_category_id(username, password, upper_category, middle_category, category):
    results = requests.get(f"{URL}/categories/lower/?upper_category={upper_category}&middle_category={middle_category}&category={category}&format=json",
                            auth=(username,password)).json()['results']
    if len(results) != 1:
        return None
    return results[0]['id']

# Example material in material.json
# Can only be performed by an authenticated user
# "category" parameter must be the id (primary key) of a lower category object (which can be checked at GET /categories/upper/)
def create_material(username, password, material_json : dict, upper_cat="Other", middle_cat="Other", cat="Other"):
    if not material_json.get("category"):
        lower_category_id = get_lower_category_id(username, password, upper_cat, middle_cat, cat)
        material_json["category"] = lower_category_id
    return requests.post(f"{URL}/materials/?format=json", auth=(username,password), json=material_json)

def get_material_list():
    return requests.get(f"{URL}/materials/?format=json").json()['results']

# Any authenticated user, does not need to be material owner
def create_test(username, password, test_name, material_id, DIC_params : dict, thermog_params : dict):
    test_json = {
        "material": material_id,
        "name": test_name,
        "DIC_params": DIC_params,
        "thermog_params": thermog_params
    }
    return requests.post(f"{URL}/tests/?format=json", auth=(username,password), json=test_json)

def upload_test_data(username, password, test_id, files, stage_metadata, format="aramis", _3d=False, override=False):
    files["stage_metadata.csv"] = stage_metadata
    return requests.post(f"{URL}/tests/{test_id}/upload/?file_format={format}&3d={_3d}&override={override}", files=files, auth=(username,password))

def get_profile(username, password):
    return requests.get(f"{URL}/users/profile/", auth=(username,password)).json()


# username_teresa = "teresa123"
# password_teresa = "aseret321_"

# x = create_test(username_teresa, password_teresa, "TESTTESTEST", 1, dict(), dict())
# print(x.status_code)

