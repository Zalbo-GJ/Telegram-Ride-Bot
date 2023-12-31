import json

try:
    with open('user_data.json', 'r') as file:
        users = json.load(file)
except FileNotFoundError:
    users = {}

try:
    with open('ongoing_rides.json', 'r') as file:
        ongoing_rides = json.load(file)
except FileNotFoundError:
    ongoing_rides = {}

try:
    with open('ride_history.json', 'r') as file:
        ride_history = json.load(file)
        print(ride_history)
except FileNotFoundError:
    ride_history = {}

drivers = set() 

user_ratings = {}
user_reviews = {}
