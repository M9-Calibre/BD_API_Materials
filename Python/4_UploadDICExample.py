from vxformsapi.vxformsapi.API import *
import os

token = authenticate("afonso", "1234")

# # Directory where the DIC files and load data are stored, consult the user manual for formatting and naming of the files
# dir = "test\\" 

# # ID of the test we wish to populate
test_id = 2

# f = []
# for (dirpath, dirnames, filenames) in os.walk(dir):
#     f.extend(filenames)
#     break

# file_mappings = {name : open(dir+name, "rb") for name in f}

test = get_test(test_id)

# # Upload the data
# test.upload_test_data(token, file_mappings, file_format=UploadFileFormat.MatchId, _3d=False)

# Download the data as a ZIP file
test.download_test_data()

# Download the data as a pandas dataframe
stages_df = test.load_test_data()

print(stages_df.keys())
print(stages_df[2])
