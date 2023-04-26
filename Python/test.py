from API import *
import os
import pandas as pd

# dir = "./90deg/"

# test_id = 4

username_teresa = "teresa123"
password_teresa = "aseret321_"
first_name = "Teresa"
last_name = "Matos"
email = "teresa@example.pt"

# f = []
# for (dirpath, dirnames, filenames) in os.walk(dir):
#     f.extend(filenames)
#     break

# files = {f : open(f"{dir}{f}", "rb") for k, f in enumerate(f)}

# x = upload_test_data(username_teresa, password_teresa, test_id, files, open("stage_metadata.csv", "rb"), "matchid", False, True)
# print(f"Teresa submits test data: {x.status_code}")

# dir = "./Test0deg/"

# test_id = 1

# username_bob = "Bob123"
# password_bob = "Bobby321_"
# first_name = "Bob"
# last_name = "Bobby"
# email = "bob@example.pt"

# f = []
# for (dirpath, dirnames, filenames) in os.walk(dir):
#     f.extend(filenames)
#     break

# files = {f : open(f"{dir}{f}", "rb") for k, f in enumerate(f)}

# x = upload_test_data(username_bob, password_bob, test_id, files, open("stage_metadata.csv", "rb"), "aramis", True, False)
# print(f"Teresa submits test data: {x.status_code}")

print(login_user(username_teresa, password_teresa))
