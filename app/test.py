import requests

url = "http://localhost:5000/upvote/1"
data = {'username': 'pb'}

response = requests.post(url, data=data)
print("x")
print(response)