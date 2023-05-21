from API import *
import os

token = authenticate("afonso", "1234")

dir = "test\\"

f = []
for (dirpath, dirnames, filenames) in os.walk(dir):
    f.extend(filenames)
    break

file_mappings = {name : open(dir+name, "rb") for name in f}

test = get_test(5)

#test.upload_test_data(token, file_mappings)

test.download_test_data()
