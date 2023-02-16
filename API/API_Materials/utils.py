from zipfile import ZipFile


def process_test_data(zip_file):
    with ZipFile(zip_file, "r") as zip_file:
        for name in zip_file.namelist():
            print(name)
            with zip_file.open(name, "r") as dic_file:
                print(dic_file.readline())
    return
