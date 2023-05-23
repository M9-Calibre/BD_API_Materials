from API import *
import os

token = authenticate("afonso", "1234")

dir = "0deg_matchid_2d\\"

f = []
for (dirpath, dirnames, filenames) in os.walk(dir):
    f.extend(filenames)
    break

file_mappings = {name : open(dir+name, "rb") for name in f}

test = get_test(1)

test.upload_test_data(token, file_mappings, file_format=UploadFileFormat.MatchId, _3d=False)

test.download_test_data()

stages_df = test.load_test_data()

print(stages_df.keys())
print(stages_df[2])
