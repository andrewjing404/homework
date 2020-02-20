from pymongo import MongoClient
from pprint import pprint
import os
import json
from bson.code import Code

"""
- Creates a MongoDB database called "amazon".
- Reads "reviews_electronics.16.json" and uploads each review as a separate document to the collection "reviews" in the database "amazon".
- Uses MongoDB's map reduce function to build a new collection "avg_scores" that averages review scores by product ("asin"). 
- Print the first 100 entries of "avg_scores" to screen.
- Uses MongoDB's map reduce function to build a new collection "weighted_avg_scores" that averages review scores by product ("asin"),
- weighted by the number of helpful votes (The base weight is 1 and for every additional helpful vote add 1 to weight.
- e.g. a "[3, 5]" value on "helpful" column should use 3 + 1 = 4 as weight, 3 being the additional votes and 1 being the base weight). 
- Print the first 100 entries of "weighted_avg_scores" to screen.
"""

# read review json file into a dictionary called "reviews"
os.chdir("/Users/xiongma/Documents/Sync/PYJY")
reviews = []
with open("reviews_electronics.16.json") as f:
    for review in f:
        reviews.append(json.loads(review))

# create a database called amazon and a collection called review
client = MongoClient()
db = client['amazon']
collection = db['review']

# insert all reviews into the review collection
for review in reviews:
    collection.insert_one(review)

# create and execute map reduction, calculate the average rating of each asin item
collection = db['review']
map = Code("function () {emit(this.asin, this.overall)}")
reduce = Code("function (asin, score) {return Array.avg(score)}")
cursor = collection.map_reduce(map, reduce, "avg_scores")

# create a collection called "avg_scores" and store the result of MapReduction to it
collection = db['avg_scores']
for item in cursor.find():
    try:
        asin = {"asin": item['_id'], "avg_scores": item['value']}
        collection.insert_one(asin)
    except:
        pass

# print the first 100 entries of "avg_scores"
collection = db['avg_scores']
result = collection.find().limit(100)
for item in result:
    pprint(item)

# create a MapReduction function to calculate weighted_avg_scores
collection = db['review']
map = Code("function () {emit(this.asin, this.overall * (this.helpful[0] + 1))}")
reduce = Code("function (asin, weighted_score) {return Array.avg(weighted_score)}")
cursor = collection.map_reduce(map, reduce, "weighted_avg_scores")

# create a collection called "weighted_avg_scores" and store the result of MapREduction to it
collection = db['weighted_avg_scores']
for item in cursor.find():
    try:
        asin = {"asin": item['_id'], "weighted_avg_scores": item['value']}
        collection.insert_one(asin)
    except:
        pass

# print the first 100 entries of "weighted_avg_scores"
collection = db['weighted_avg_scores']
result = collection.find().limit(100)
for item in result:
    pprint(item)