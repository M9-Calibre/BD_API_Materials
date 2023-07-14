import requests
import shutil
import json
import pandas as pd
import zipfile
import io
from enum import Enum
from typing import Union, Any
from copy import deepcopy
from time import time

URL = 'http://127.0.0.1:8000'

class APIFailedRequest(Exception):
    def __init__(self, response : requests.Response) -> None:
        self.status_code = response.status_code
        self.reason = response.reason
        try:
            self.json_body = response.json()
        except:
            self.json_body = None
        self.message = f'Invalid request. (Status Code {self.status_code}: {self.reason})'
        if self.json_body: self.message += "\n"+json.dumps(self.json_body, indent=2)
        super().__init__(self.message)

class MaterialOrderings(Enum):
    Id = "id"
    Date = "entry_date"
    Name = "name"
    UpperC = "upper_category"
    MiddleC = "middle_category"
    LowerC = "lower_category"

class CategoriesDisplayModes(Enum):
    Tree = "tree"
    List = "list"

class CategoryLevel(Enum):
    Upper = "upper"
    Middle = "middle"
    Lower = "lower"

class UploadFileFormat(Enum):
    MatchId = "matchid"
    Aramis = "aramis"

class Category():
    def __init__(self, name : str) -> None:
        self.id = None
        self.name = name

    def register(self, admin_token : str):
        self = register_category(admin_token, self)
        return self

class UpperCategory(Category):
    def __init__(self, name : str) -> None:
        self.id = None
        self.name = name

    def __str__(self) -> str:
        return f"Upper Category {self.id}: {self.name}"

class MiddleCategory(Category):
    def __init__(self, upper : UpperCategory, name : str) -> None:
        self.id = None
        self.upper = upper
        self.name = name

    def __str__(self) -> str:
        return f"Middle Category {self.id}: {self.name}"

class LowerCategory(Category):
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
        json_data = deepcopy(self.__dict__)
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
    def __init__(self, tensile_strength : float = None, thermal_conductivity : float = None, reduction_of_area : float = None, 
                 cyclic_yield_strength : float = None, elastic_modulus : dict[str, float] = None, poissons_ratio : dict[str, float] = None, shear_modulus : dict[str, float] = None, 
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
        json_data = deepcopy(self.__dict__)
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
        return deepcopy(self.__dict__)

    @classmethod
    def load_json(cls, physical_properties_json : dict):
        physical_properties = PhysicalProperties()
        physical_properties.chemical_composition = physical_properties_json.get("chemical_composition", None)
        return physical_properties

class Material():
    def __init__(self, name : str, category : LowerCategory, source : str, designation : str, heat_treatment : str, 
                 description : str = None, thermal_properties : ThermalProperties = None, mechanical_properties : MechanicalProperties = None, 
                 physical_properties : PhysicalProperties = None) -> None:
        self.id = None
        self.submitted_by = None
        self.user = None
        self.date = None
        self.name = name
        self.category = category
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
        material_json = deepcopy(self.__dict__)
        material_json["category"] = self.category.id

        if self.thermal_properties:
            material_json["thermal_properties"] = self.thermal_properties.to_dict()
        else:
            material_json.pop("thermal_properties")

        if self.mechanical_properties:
            material_json["mechanical_properties"] = self.mechanical_properties.to_dict()
        else:
            material_json.pop("mechanical_properties")

        if self.physical_properties:
            material_json["physical_properties"] = self.physical_properties.to_dict()
        else:
            material_json.pop("physical_properties")

        return material_json
    
    def register(self, login_token : str):
        self = register_material(login_token, self)
        return self

    @classmethod
    def load_json(cls, material_json : dict):
        name = material_json["name"]
        upper_category = UpperCategory(material_json["upper_category"])
        upper_category.id = material_json["upper_category_id"]
        middle_category = MiddleCategory(upper_category, material_json["middle_category"])
        middle_category.id = material_json["middle_category_id"]
        category = LowerCategory(middle_category, material_json["lower_category"])
        category.id = material_json["category"]
        source = material_json["source"]
        designation = material_json["designation"]
        heat_treatment = material_json["heat_treatment"]
        description = material_json.get("description", None)
        thermal_properties = ThermalProperties.load_json(material_json["thermal_properties"]) if "thermal_properties" in material_json and material_json["thermal_properties"] else None
        physical_properties = PhysicalProperties.load_json(material_json["physical_properties"]) if "physical_properties" in material_json and material_json["physical_properties"] else None
        mechanical_properties = MechanicalProperties.load_json(material_json["mechanical_properties"]) if "mechanical_properties" in material_json and material_json["mechanical_properties"] else None
        
        material = Material(name, category, source, designation, heat_treatment, description, thermal_properties, mechanical_properties, physical_properties)
        material.id = material_json.get("id", None)
        material.submitted_by = material_json.get("submitted_by", None)
        material.user = material_json.get("user", None)
        material.date = material_json.get("entry_date", None)
        return material
    
class Test():
    def __init__(self, material : Material, name : str, metadata : dict[str, Union[str, int, float]]) -> None:
        self.material = material
        self.name = name
        self.metadata = metadata
        self.id = None
        self.submitted_by = None

    def upload_test_data(self, login_token : str, file_mapping : dict[str, Any], file_format : UploadFileFormat = UploadFileFormat.MatchId, _3d : bool = False, override : bool = False):
        """Upload experimental data (as DIC files) to this test.

        Parameters
        ----------
        login_token : str
            The log-in token that can be retrieved from the authenticate function (must be test creator)
        file_mapping : dict[str, File]
            A dictionary with the file names as keys and file contents as values
            A "stage_metadata" file must be uploaded in order to specify stage's load and timestamp
            Consult the upload manual to verify file naming and content formatting
        file_format : UploadFileFormat
            Specifies the file's formatting (matchid or aramis)
            Consult the upload manual to verify file naming and content formatting
        _3d : bool
            Specifies the dimensionality of the DIC files being uploaded, if false 2-dimensional files are assumed
            Consult the upload manual to verify file naming and content formatting
        override : bool
            If set to true the uploaded data will override any existing db data if there is overlap
            Consult the upload manual to verify file naming and content formatting
        
        """
        
        if not self.id:
            print("upload_test_data: Object not yet registered.")
            return
        
        headers = {"Authorization": f"Token {login_token}"}
        
        url = f"{URL}/tests/{self.id}/upload/?3d={_3d}&file_format={file_format.value}&override={override}"

        tik = time()

        if override:
            response = requests.put(url, files=file_mapping, headers=headers)
        else:
            response = requests.post(url, files=file_mapping, headers=headers)

        tok = time()

        if response.status_code != 200:
            raise APIFailedRequest(response)
        
        created_stages = response.json()["created_stages"]
        overridden_stages = response.json().get("overriden_stages", None)
        skipped_files = response.json()["skipped_files"]
        
        print(f"upload_test_data: Data successfully uploaded. Elapsed time: {round(tok-tik,2)}")
        print(f"upload_test_data: Created stages {created_stages}")
        print(f"upload_test_data: Overriden stages {overridden_stages}")
        print(f"upload_test_data: Skipped files {skipped_files}")

    def load_test_data(self, _3d : bool = False):
        """
        Loads the test's experimental data into a dictionary of pandas' dataframes.

        Parameters
        ----------
        _3d : bool
            Specifies the dimensionality of the DIC files being downloaded, if false 2-dimensional files are assumed
        """

        if not self.id:
            print("load_test_data: Object not yet registered.")
            return
        
        url = f"{URL}/tests/{self.id}/download/?3d={_3d}"

        tik = time()

        response = requests.get(url, stream=True)

        tok = time()

        if response.status_code != 200:
            raise APIFailedRequest(response)
        
        data = dict()
        with zipfile.ZipFile(io.BytesIO(response.content), "r") as zip:
            for name in zip.namelist():
                file = io.BytesIO(zip.read(name))
                if name == "stage_metadata.csv":
                    data["metadata"] = pd.read_csv(file)
                else:
                    stage = int(name.replace("stage_","").replace(".csv",""))
                    data[stage] = pd.read_csv(file)

        print(f"load_test_data: Data successfully loaded. Elapsed time: {round(tok-tik,2)}") 

        return data

    def download_test_data(self, _3d : bool = False):
        """
        Downloads the test's experimental data as a zip of DIC files.

        Parameters
        ----------
        _3d : bool
            Specifies the dimensionality of the DIC files being downloaded, if false 2-dimensional files are assumed
        """

        if not self.id:
            print("download_test_data: Object not yet registered.")
            return
        
        url = f"{URL}/tests/{self.id}/download/?3d={_3d}"

        tik = time()

        response = requests.get(url, stream=True)

        tok = time()

        if response.status_code != 200:
            raise APIFailedRequest(response)
        
        with open(f"test_{self.id}_data.zip", "wb") as f:
            shutil.copyfileobj(response.raw, f)

        print(f"download_test_data: Data successfully downloaded. Elapsed time: {round(tok-tik,2)}")   

    def delete_test_data(self, login_token : str):
        """Clears existing experimental data from this test.

        Parameters
        ----------
        login_token : str
            The log-in token that can be retrieved from the authenticate function (must be test creator)
        
        """

        if not self.id:
            print("delete_test_data: Object not yet registered.")
            return

        headers = {"Authorization": f"Token {login_token}"}
        url = f"{URL}/tests/{self.id}/delete/"

        response = requests.delete(url, headers=headers)

        if response.status_code != 204:
            raise APIFailedRequest(response)
        
        print("delete_test_data: Data successfully deleted.")

    def to_json(self):
        test_json = deepcopy(self.__dict__)
        test_json["material"] = self.material.id
        test_json["DIC_params"] = test_json.pop("metadata")
        return test_json
    
    def register(self, login_token : str):
        self = register_test(login_token, self)
        return self
    
    @classmethod
    def load_json(cls, test_json):
        material = get_material(test_json["material"])
        name = test_json["name"]
        metadata = test_json["DIC_params"]
        test = Test(material, name, metadata)
        test.id = test_json.get("id", None)
        test.submitted_by = test_json.get("submitted_by", None)
        return test

class Model():
    def __init__(self, name : str, tag : str, function_name: str, input : list, category: str) -> None:
        self.id = None
        self.name = name
        self.tag = tag
        self.function_name = function_name
        self.input = input
        self.category = category

    def to_json(self):
        return deepcopy(self.__dict__)
    
    @classmethod
    def load_json(cls, model_json : dict):
        model = Model(model_json["name"], model_json["tag"], model_json["function_name"], model_json["input"], model_json["category"])
        model.id = model_json.get('id', None)
        return model
    
class ModelParams():
    def __init__(self, test : Test, model : Model, params : dict) -> None:
        self.id = None
        self.submitted_by = None
        self.user = None
        self.test = test
        self.model = model
        self.params = params

    def to_json(self):
        modelp_json = deepcopy(self.__dict__)
        modelp_json["test"] = self.test.id
        modelp_json["model"] = self.model.id
        return modelp_json
    
    def get_graph(self):
        """Get an image graph of the results of applying the parameters to the behavior model"""
        
        if not self.id:
            print("get_graph: object not yet registered.")
            return

        url = f"{URL}/modelparams/{self.id}/graph/"

        response = requests.get(url)

        if response.status_code != 200:
            raise APIFailedRequest(response)
        
        with open(f"{self.model.tag}_{self.test.name}_results.png", "wb") as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)
    
    @classmethod
    def load_json(cls, modelp_json : dict):
        modelp = ModelParams(get_test(modelp_json["test"]), get_model(modelp_json["model"]), modelp_json["params"])
        modelp.id = modelp_json.get('id', None)
        modelp.user = modelp_json.get('user', None)
        modelp.submitted_by = modelp_json.get('submitted_by', None)
        return modelp

# Authentication
    
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

def authenticate_from_json(file_path : str) -> str:
    """Login with existing user credentials and retrieve an authentication token.

    Parameters
    ----------
    username : str
        The username of the user
    password : str
        The password of the user
    
    """

    with open(file_path, "r") as f:
        json_req_body = json.loads(f.read())

    login = requests.post(f"{URL}/users/login/", json=json_req_body)

    if login.status_code != 200:
        raise APIFailedRequest(login)
    
    token = login.json()["token"]

    print("authenticate: Authentication successful.")

    return token

# Materials   

def get_materials(page : int = 1, page_size : int = 10, ordering : MaterialOrderings = MaterialOrderings.Id, ascending : bool = True, search : str = None) -> list[Material]:
    """Retrieve a page of materials.

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

def get_material(material_id : int) -> Material:
    """Retrieve a material by id.
    
    Parameters
    ----------
    material_id : int
        The id of the material to be fetched
    """

    url = f"{URL}/materials/{material_id}/"

    response = requests.get(url)

    if response.status_code != 200:
        raise APIFailedRequest(response)
    
    material_data = response.json()
    material = Material.load_json(material_data)

    print(f"get_material: Successfully fetched material {material.name} with id {material.id}.")

    return material

def register_material(login_token : str, material : Material):
    """Save a material to the database.

    Parameters
    ----------
    material : Material
        The material to be saved (name must be unique)
    login_token : str
        The log-in token that can be retrieved from the authenticate function
    
    """

    headers = {"Authorization": f"Token {login_token}"}

    response = requests.post(f"{URL}/materials/", headers=headers, json=material.to_json())

    if response.status_code != 201:
        raise APIFailedRequest(response)
    
    material.id = response.json()["id"]
    material.submitted_by = response.json()["submitted_by"]
    material.user = response.json()["user"]
    material.date = response.json()["entry_date"]
    print(f"register_material: Material {material.name} successfully registered with id {material.id}.")
    return material

# Categories

def get_categories(mode : CategoriesDisplayModes = CategoriesDisplayModes.List):
    """Retrieve all categories.
    
    Parameters
    ----------
    mode (optional) : CategoriesDisplayModes
        Either return the categories in a tree-like object or return three lists for each type of category (upper, middle, lower)

    """

    first_call = requests.get(f"{URL}/categories/upper/")

    if first_call.status_code != 200:
        raise APIFailedRequest(first_call)
    
    count = first_call.json()["count"]

    response = requests.get(f"{URL}/categories/upper/?page_size={count}")

    if response.status_code != 200:
        raise APIFailedRequest(response)
    
    json_data = response.json()["results"]

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
                count += 1
                id = middle_category["id"]
                name = middle_category["category"]
                mid_category = MiddleCategory(up_category, name)
                mid_category.id = id
                result["middle"].append(mid_category)
                for lower_category in middle_category["lower_categories"]:
                    count += 1
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
                count += 1
                id = middle_category["id"]
                name = middle_category["category"]
                mid_category = MiddleCategory(up_category, name)
                mid_category.id = id
                result[up_category][mid_category] = list()
                for lower_category in middle_category["lower_categories"]:
                    count += 1
                    id = lower_category["id"]
                    name = lower_category["category"]
                    low_category = LowerCategory(mid_category, name)
                    low_category.id = id
                    result[up_category][mid_category].append(low_category)

    print(f"get_categories: Successfully fetched {count} categories. Format {mode.value}.")

    return result

def get_category(category_id : int, level : CategoryLevel = CategoryLevel.Lower):
    """Retrieve a category by id.
    
    Parameters
    ----------
    category_id : int
        The id of the category to be fetched
    level (optional) : CategoryLevel
        The level of the category to be fetched (by default, lower)
    """

    url = f"{URL}/categories/{level.value}/{category_id}/"

    response = requests.get(url)

    if response.status_code != 200:
        raise APIFailedRequest(response)
    
    category_data = response.json()

    if level == CategoryLevel.Lower:
        upper_id = category_data["upper_category"]
        upper_name = category_data["upper_name"]
        upper = UpperCategory(upper_name)
        upper.id = upper_id
        middle_id = category_data["middle_category"]
        middle_name = category_data["middle_name"]
        middle = MiddleCategory(upper, middle_name)
        middle.id = middle_id
        lower_id = category_data["id"]
        lower_name = category_data["category"]
        lower = LowerCategory(middle, lower_name)
        lower.id = lower_id
        print(f"get_category: Successfully fetched lower category {lower.name} with id {lower.id}.")
        return lower
    elif level == CategoryLevel.Middle:
        upper_id = category_data["upper_category"]
        upper_name = category_data["upper_name"]
        upper = UpperCategory(upper_name)
        upper.id = upper_id
        middle_id = category_data["id"]
        middle_name = category_data["category"]
        middle = MiddleCategory(upper, middle_name)
        middle.id = middle_id
        print(f"get_category: Successfully fetched middle category {middle.name} with id {middle.id}.")
        return middle
    elif level == CategoryLevel.Upper:
        upper_id = category_data["id"]
        upper_name = category_data["category"]
        upper = UpperCategory(upper_name)
        upper.id = upper_id
        print(f"get_category: Successfully fetched upper category {upper.name} with id {upper.id}.")
        return upper
    
def get_category_by_name(category_name : str, level : CategoryLevel = CategoryLevel.Lower):
    """Retrieve a category by name.
    
    Parameters
    ----------
    category_name : str
        The name of the category to be fetched
    level (optional) : CategoryLevel
        The level of the category to be fetched (by default, lower)
    """

    search_field = f"{level.value}_" if level != CategoryLevel.Lower else ""

    url = f"{URL}/categories/{level.value}/?{search_field}category={category_name}"

    response = requests.get(url)

    if response.status_code != 200:
        raise APIFailedRequest(response)
    
    category_data = response.json()["results"]

    if len(category_data) > 1 or len(category_data) == 0:
        return

    category_data = category_data[0]

    if level == CategoryLevel.Lower:
        upper_id = category_data["upper_category"]
        upper_name = category_data["upper_name"]
        upper = UpperCategory(upper_name)
        upper.id = upper_id
        middle_id = category_data["middle_category"]
        middle_name = category_data["middle_name"]
        middle = MiddleCategory(upper, middle_name)
        middle.id = middle_id
        lower_id = category_data["id"]
        lower_name = category_data["category"]
        lower = LowerCategory(middle, lower_name)
        lower.id = lower_id
        print(f"get_category_by_name: Successfully fetched lower category {lower.name} with id {lower.id}.")
        return lower
    elif level == CategoryLevel.Middle:
        upper_id = category_data["upper_category"]
        upper_name = category_data["upper_name"]
        upper = UpperCategory(upper_name)
        upper.id = upper_id
        middle_id = category_data["id"]
        middle_name = category_data["category"]
        middle = MiddleCategory(upper, middle_name)
        middle.id = middle_id
        print(f"get_category_by_name: Successfully fetched middle category {middle.name} with id {middle.id}.")
        return middle
    elif level == CategoryLevel.Upper:
        upper_id = category_data["id"]
        upper_name = category_data["category"]
        upper = UpperCategory(upper_name)
        upper.id = upper_id
        print(f"get_category_by_name: Successfully fetched upper category {upper.name} with id {upper.id}.")
        return upper

def register_category(admin_token : str, category : Category):
    """Save a category to the database.

    Parameters
    ----------
    admin_token : str
        The log-in token that can be retrieved from the authenticate function (must be admin)
    category : Category
        The category to be saved 
    
    """

    headers = {"Authorization": f"Token {admin_token}"}

    if isinstance(category, UpperCategory):
        url = f"{URL}/categories/upper/"
        body = {"category": category.name}
        response = requests.post(url, json=body, headers=headers)

        if response.status_code != 201:
            raise APIFailedRequest(response)
        else:
            category.id = response.json()["id"]
            print(f"register_category: Upper category {category.name} succesfully registered with id {category.id}.")
            return category
    elif isinstance(category, MiddleCategory):
        if not category.upper.id:
            try:
                upper = get_category_by_name(category.upper.name, CategoryLevel.Upper)
            except APIFailedRequest:
                category.upper = register_category(admin_token, category.upper)
            else:
                if upper: category.upper = upper
                else: category.upper = register_category(admin_token, category.upper)
        
        url = f"{URL}/categories/middle/"
        body = {"category": category.name, "upper_category": category.upper.id}
        response = requests.post(url, json=body, headers=headers)

        if response.status_code != 201:
            raise APIFailedRequest(response)
        else:
            category.id = response.json()["id"]
            print(f"register_category: Middle category {category.name} succesfully registered with id {category.id}.")
            return category
    elif isinstance(category, LowerCategory):
        if not category.middle.id:
            try:
                middle = get_category_by_name(category.middle.name, CategoryLevel.Middle)
            except APIFailedRequest:
                category.middle = register_category(admin_token, category.middle)
            else:
                if middle: category.middle = middle
                else: category.middle = register_category(admin_token, category.middle)

        url = f"{URL}/categories/lower/"
        body = {"category": category.name, "middle_category": category.middle.id}
        response = requests.post(url, json=body, headers=headers)

        if response.status_code != 201:
            raise APIFailedRequest(response)
        else:
            category.id = response.json()["id"]
            print(f"register_category: Lower category {category.name} succesfully registered with id {category.id}.")
            return category
    else:
        print("register_category: Must specify category level (upper/middle/lower).")
        return
    
# Tests

def register_test(login_token : str, test : Test):
    """Save a test to the database.

    Parameters
    ----------
    login_token : str
        The log-in token that can be retrieved from the authenticate function
    test : Test
        The test to be saved (name must be unique within the material's tests)
    
    """

    headers = {"Authorization": f"Token {login_token}"}

    response = requests.post(f"{URL}/tests/", headers=headers, json=test.to_json())

    if response.status_code != 201:
        raise APIFailedRequest(response)
    
    test.id = response.json()["id"]
    test.submitted_by = response.json()["submitted_by"]
    
    print(f"register_test: Successfully registered test {test.name} with id {test.id}.")

    return test

def get_tests(page : int = 1, page_size : int = 10, material : int = None, submitted_by : int = None) -> list[Test]:
    """Retrieve a page of tests.

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
    
    """
    
    url = f"{URL}/tests/?page={page}&page_size={page_size}{'&material='+material if material else ''}{'&submitted_by='+submitted_by if submitted_by else ''}"

    response = requests.get(url)

    if response.status_code != 200:
        raise APIFailedRequest(response)
    
    results = response.json()["results"]

    test = list[Test]()
    for test_json in results:
        test.append(Test.load_json(test_json))

    print(f"get_tests: Successfully retrieved {len(test)} tests.")

    return test

def get_test(test_id : int):
    """Retrieve a test by id.
    
    Parameters
    ----------
    test_id : int
        The id of the test to be fetched
    """

    url = f"{URL}/tests/{test_id}/"

    response = requests.get(url)

    if response.status_code != 200:
        raise APIFailedRequest(response)
    
    test_data = response.json()
    test = Test.load_json(test_data)

    print(f"get_test: Successfully fetched test {test.name} with id {test.id}.")

    return test

# Models

def get_model(model_id : int):
    """Retrieve a model by id.
    
    Parameters
    ----------
    model_id : int
        The id of the model to be fetched
    """

    url = f"{URL}/models/{model_id}/"

    response = requests.get(url)

    if response.status_code != 200:
        raise APIFailedRequest(response)
    
    model_data = response.json()

    return Model.load_json(model_data)

def register_model(admin_token : str, model : Model):
    """Save a model to the database.

    Parameters
    ----------
    admin_token : str
        The log-in token that can be retrieved from the authenticate function (must be admin)
    model : Model
        The model to be saved 
    
    """

    headers = {"Authorization": f"Token {admin_token}"}

    url = f"{URL}/models/"
    body = model.to_json()
    response = requests.post(url, json=body, headers=headers)

    if response.status_code != 201:
        raise APIFailedRequest(response)
    else:
        model.id = response.json()["id"]
        return model
    
# ModelParams

def get_model_params(modelp_id : int):
    """Retrieve model parameters by id.
    
    Parameters
    ----------
    modelp_id : int
        The id of the model parameters to be fetched
    """

    url = f"{URL}/modelparams/{modelp_id}/"

    response = requests.get(url)

    if response.status_code != 200:
        raise APIFailedRequest(response)
    
    modelp_data = response.json()

    return ModelParams.load_json(modelp_data)

def register_model_params(login_token : str, modelp : ModelParams):
    """Save model parameters to the database.

    Parameters
    ----------
    login_token : str
        The log-in token that can be retrieved from the authenticate function
    modelp : ModelParams
        The model parameters to be saved 
    
    """

    headers = {"Authorization": f"Token {login_token}"}

    url = f"{URL}/modelparams/"
    body = modelp.to_json()
    response = requests.post(url, json=body, headers=headers)

    if response.status_code != 201:
        raise APIFailedRequest(response)
    else:
        modelp.id = response.json()["id"]
        modelp.submitted_by = response.json()["submitted_by"]
        return modelp


