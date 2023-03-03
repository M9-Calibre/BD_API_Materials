import requests

URL = 'http://127.0.0.1:8000'

files = {'1' : open("./data/1.txt", "r"), '2' : open("./data/2.txt", "rb"), '3' : open("./data/3.txt", "rb")}

requests.post(f"{URL}/tests/3/upload", files=files)
