import requests

URL = 'http://afonsocampos100.pythonanywhere.com'
#URL = 'http://127.0.0.1:8000'

# Usernames and emails must be unique
def register_user(username, password, first_name, last_name, email):
    json_req_body = {
        "username" : username,
        "password" : password,
        "first_name" : first_name,
        "last_name" : last_name,
        "email" : email
    }

    return requests.post(f"{URL}/users/register/", json=json_req_body)

# Can only be performed by a superuser
# Steps to create superuser in the README.md
def get_user_list(username, password):
    return requests.get(f"{URL}/users/?format=json", auth=(username,password)).json()

# Can only be performed by a superuser
# Steps to create superuser in the README.md
def create_upper_category(username, password, category_name):
    return requests.post(f"{URL}/categories/upper", auth=(username,password), json={"category":category_name})

# Can only be performed by a superuser
# An upper category must already be created to link to
def create_middle_category(username, password, upper_category, category_name):
    upper_category_id = get_upper_category_id(username, password, upper_category)
    return requests.post(f"{URL}/categories/middle", auth=(username,password), json={"category":category_name,"upper_category":upper_category_id})

# Can only be performed by a superuser
# A middle category must already be created to link to
def create_lower_category(username, password, upper_category, middle_category, category_name):
    middle_category_id = get_middle_category_id(username, password, upper_category, middle_category)
    return requests.post(f"{URL}/categories/lower", auth=(username,password), json={"category":category_name,"upper_category":middle_category_id})

def get_category_tree(username, password):
    return requests.get(f"{URL}/categories/upper?format=json", auth=(username,password)).json()['results']

def get_upper_category_id(username, password, upper_category):
    results = requests.get(f"{URL}/categories/upper?upper_category={upper_category}&format=json", 
                            auth=(username,password)).json()['results']
    if len(results) != 1:
        return None
    return results[0]['id']

def get_middle_category_id(username, password, upper_category, middle_category):
    results = requests.get(f"{URL}/categories/middle?upper_category={upper_category}&middle_category={middle_category}&format=json", 
                            auth=(username,password)).json()['results']
    if len(results) != 1:
        return None
    return results[0]['id']

def get_lower_category_id(username, password, upper_category, middle_category, category):
    results = requests.get(f"{URL}/categories/lower?upper_category={upper_category}&middle_category={middle_category}&category={category}&format=json",
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

def upload_test_data(username, password, test_id, files):
    return requests.post(f"{URL}/tests/{test_id}/upload", files=files, auth=(username,password))
    
