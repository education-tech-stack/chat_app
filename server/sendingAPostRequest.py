import requests


data = {
    "pens": 12,
    "pencils": "Eight"
}

r = requests.post("http://127.0.0.1:5000/send_me_data", data=data)
print(r.text)
