import requests


r = requests.get('http://127.0.0.1:5000')
data = r.json()

print(f'There are {data["people"]} people. {data["cats"]} of them have a cat, and {data["dogs"]} of them have dog.')
