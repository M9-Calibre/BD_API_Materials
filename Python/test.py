import requests

URL = 'http://127.0.0.1:8000'

files = {'data' : open("data.zip", "rb")}

requests.post(f"{URL}/tests/1/upload", files=files)
