import requests

filename = "./testclouds/_1.jpg"

response = requests.post(
    'http://127.0.0.1:999/api/predict',
    files={'file':open(filename, 'rb')},
)

print(response.content)