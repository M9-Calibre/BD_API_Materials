from API import *
import json
import os
import time

# superuser must be created as indicated in README.md, change variables to your liking
username_staff = "afonso"
password_staff = "1234"

# Create some users

username_teresa = "teresa123"
password_teresa = "aseret321_"
first_name = "Teresa"
last_name = "Matos"
email = "teresa@example.pt"


username_bob = "Bob123"
password_bob = "Bobby321_"
first_name = "Bob"
last_name = "Bobby"
email = "bob@example.pt"

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
 
# x = create_test(username_bob, password_bob, "5555", 1, dic_params_example, None)
# print(f"Bob submits a test: {x.status_code}, {x.reason}")
# test_id = x.json()['id']
# print(test_id)
# print(f"Test -> ID: {test_id}, Owner: {x.json()['submitted_by']}, Material: {x.json()['material']}")

# test_id = 14

# f = []
# for (dirpath, dirnames, filenames) in os.walk("./90deg"):
#     f.extend(filenames)
#     break

# files = {str(k) : open(f"./90deg/{f}", "rb") for k, f in enumerate(f)}

# print(files)

# tik = time.time()

# x = upload_test_data(username_bob, password_bob, test_id, files, open("stage_metadata.csv", "rb"), "aramis", True, False)
# print(f"Bob submits test data: {x.status_code} {x.json()}")

