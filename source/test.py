import requests
from flask import jsonify

BASE = "http://127.0.0.1:5000/"

user1 = {
    "name": "Ana",
    "surname": "Jakovljevic",
    "email": "ana@banana.com",
    "username": "anccikaba",
    "password1": "123456",
    "password2": "123456",
    "desired_type": "admin"
}

user2 = {
    "name": "Ceca",
    "surname": "Bicanin",
    "email": "ceca@pereca.com",
    "username": "pereca123",
    "password1": "12345678",
    "password2": "12345678",
    "desired_type": "guide"
}

user3 = {
    "name": "Velja",
    "surname": "Bicanin",
    "email": "velja@selja.com",
    "username": "veljaselja",
    "password1": "www123",
    "password2": "www123",
    "desired_type": "tourist"
}

user4 = {
    "name": "Ceca",
    "surname": "Bicanin",
    "email": "ceca@pereca.com",
    "username": "anccikaba",
    "password1": "12345678",
    "password2": "12345678",
    "desired_type": "guide"
}
response1 = requests.post(BASE + 'signin', user1)
print(response1)

input()

response2 = requests.post(BASE + 'signin', user2)
print(response2.status_code)

input()

response3 = requests.post(BASE + 'signin', user3)
print(response3)

input()

response4 = requests.post(BASE + 'signin', user4)
print(response4)

input()

admin = {
    "name": "Kruso",
    "surname": "Robinson",
    "email": "kruso777@rob.com",
    "username": "admin",
    "password1": "admin",
    "password2": "admin",
    "desired_type": "admin"
}

response_admin = requests.post(BASE + 'signin', admin)
print(response_admin)
'''
login1 = {
    "username": "anccikaba",
    "password": "123456",
}

response_login = requests.post(BASE + 'login', login1)
print(response_login)

input()

arangement = {
    "start": "2021-11-11",
    "end": "2021-11-21",
    "description": "Travel to Serbia",
    "destination": "Serbia, Aleksandrovac",
    "number_of_seats": 30,
    "price": 100.26
}

response_admin = requests.post(BASE + 'add_arangement', arangement)
print(response_admin)

input()

response_logout = requests.post(BASE + 'logout')
print(response_logout)
'''