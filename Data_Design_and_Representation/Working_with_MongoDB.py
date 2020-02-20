from pymongo import MongoClient
from pprint import pprint

"""
- Connect to MongoDB;
- query and print all the Pokemon characters that have a candy_count of >=40.
"""

client = MongoClient()
db = client['samples_pokemon']
collection = db['samples_pokemon']
cursor = collection.find({"candy_count": {"$gte": 40}})

for pokemon in cursor:
    print(pokemon['name'])