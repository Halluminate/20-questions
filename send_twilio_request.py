#!/usr/bin/env python
import requests

url = "http://127.0.0.1:5000/sms"
data = {"Body": "hello"}

response = requests.post(url, data=data)
print(response.text)
