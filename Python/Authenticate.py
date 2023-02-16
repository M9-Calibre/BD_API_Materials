import requests

URL = 'http://127.0.0.1:8000'
DO_REGISTER = False

# Example User
username = "teresa123"
password = "aseret321_"
first_name = "Teresa"
last_name = "Matos"
email = "teresa@example.pt"

if DO_REGISTER:
    # Example Register
    json_req_body = {
        "username" : username,
        "password" : password,
        "first_name" : first_name,
        "last_name" : last_name,
        "email" : email
    }

    response = requests.post(f"{URL}/users/register/", json=json_req_body)

    print(response.status_code) # 201 if successful

# Example Login (Basic Auth for now)
response = requests.get(f"{URL}/users/login/", auth=(username,password))

print(response.status_code) # 200

# Wrong Password
response = requests.get(f"{URL}/users/login/", auth=(username,"aaaa"))

print(response.status_code) # 401 Unauthorized
