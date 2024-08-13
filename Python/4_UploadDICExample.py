from vxformsapi.vxformsapi.API import *
import os

token = authenticate_from_json("secret_login.json")
print(token)

# # Directory where the DIC files and load data are stored, consult the user manual for formatting and naming of the files
dir = "leuvren-test\\" 

# # ID of the test we wish to populate
TEST_ID = 22

test = get_test(TEST_ID)
print(f"{test=}")

f = []
for (dirpath, dirnames, filenames) in os.walk(dir):
    f.extend(filenames)
    break

file_mappings = {name : open(dir+name, "rb") for name in f}

test = get_test(TEST_ID)

## Upload the data
file_identifiers = {
    "Displacement": {
        "x": 2,
        "y": 3,
        "xy": 4,
        "displacement_x": 5,
        "displacement_y": 6,
        "displacement_xy": 7
    },
    "Strain": {
        "strain_x": 2,
        "strain_y": 3,
        "strain_xy": 4
    }
}

test.upload_test_data(token, file_mappings, file_format=UploadFileFormat.MatchId, file_identifiers=file_identifiers, _3d=False)

# Download the data as a ZIP file
# test.download_test_data()

# Download the data as a pandas dataframe
stages_df = test.load_test_data()

print(stages_df.keys())
print(stages_df[2])
