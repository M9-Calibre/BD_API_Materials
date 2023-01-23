import requests

URL = 'http://127.0.0.1:8000'

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
    return requests.post(f"{URL}/categories/upper/", auth=(username,password), json={"category":category_name})

# Can only be performed by a superuser
# An upper category must already be created to link to
def create_middle_category(username, password, upper_category, category_name):
    return requests.post(f"{URL}/categories/middle/", auth=(username,password), json={"category":category_name,"upper_category":upper_category})

# Can only be performed by a superuser
# A middle category must already be created to link to
def create_lower_category(username, password, upper_category, category_name):
    return requests.post(f"{URL}/categories/lower/", auth=(username,password), json={"category":category_name,"upper_category":upper_category})

def get_category_tree():
    return requests.get(f"{URL}/categories/upper/")

# Example material in material.json
# Can only be performed by an authenticated user
# "category" parameter must be the id (primary key) of a lower category object (which can be checked at GET /categories/upper/)
def create_material(username, password, material_json):
    return requests.post(f"{URL}/materials/", auth=(username,password), json=material_json)

