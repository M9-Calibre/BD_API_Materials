import requests

URL = 'http://afonsocampos100.pythonanywhere.com'

# files = {'1' : open("./data/1.txt", "r"), '2' : open("./data/2.txt", "rb"), '3' : open("./data/3.txt", "rb")}

# requests.post(f"{URL}/tests/3/upload", files=files)

x = requests.delete(f"{URL}/materials/8/", auth=("afonso","1234"))

print(x.status_code, x.reason)
