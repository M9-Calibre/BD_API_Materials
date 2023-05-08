import requests

URL = 'http://127.0.0.1:8000'

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

class MiddleCategory():
    def __init__(self, upper : UpperCategory, name : str) -> None:
        self.id = None
        self.upper = upper
        self.name = name

class LowerCategory():
    def __init__(self, middle : MiddleCategory, name : str) -> None:
        self.id = None
        self.middle = middle
        self.name = name

class ThermalProperties():
    def __init__(self, thermal_expansion_coef : dict = None, specific_heat_capacity : dict = None, thermal_conductivity_tp : dict = None) -> None:
        self.thermal_expansion_coef = thermal_expansion_coef
        self.specific_heat_capacity = specific_heat_capacity
        self.thermal_conductivity_tp = thermal_conductivity_tp

class MechanicalProperties():
    def __init__(self, tensile_strength : int = None, thermal_conductivity_mp : float = None, reduction_of_area : float = None, 
                 cyclic_yield_strength : int = None, elastic_modulus : dict = None, poissons_ratio : dict = None, shear_modulus : dict = None, 
                 yield_strength : dict = None) -> None:
        self.tensile_strength = tensile_strength
        self.thermal_conductivity_mp = thermal_conductivity_mp
        self.reduction_of_area = reduction_of_area
        self.cyclic_yield_strength = cyclic_yield_strength
        self.elastic_modulus = elastic_modulus
        self.poissons_ratio = poissons_ratio
        self.shear_modulus = shear_modulus
        self.yield_strength = yield_strength

class PhysicalProperties():
    def __init__(self, chemical_composition : dict = None) -> None:
        self.chemical_composition = chemical_composition

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

def authenticate(username : str, password : str) -> str:
    json_req_body = {
        "username" : username,
        "password" : password
    }
    login = requests.post(f"{URL}/users/login/", json=json_req_body)

    if login.status_code != 200:
        raise APIFailedRequest(login)
    
    token = login.json()["token"]

    return token



def register_user(username : str, password : str, first_name : str, last_name : str, email : str) -> str:
    """A function to register a new user on the MaterialAPI.

    Parameters
    ----------
    username : str
        The username of the new user, must not have been previously registered
    password : str
        The password of the new user, used for future logins
    first_name : str
        The first name of the new user
    first_name : str
        The last name of the new user
    email : str
        The email of the new user, must not have been previously registered
    
    """
    json_req_body = {
        "username" : username,
        "password" : password,
        "first_name" : first_name,
        "last_name" : last_name,
        "email" : email
    }

    req = requests.post(f"{URL}/users/register/", json=json_req_body)

    if req.status_code != 200:
        raise 
    
    return f"Registration of user {username} successful!"

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
