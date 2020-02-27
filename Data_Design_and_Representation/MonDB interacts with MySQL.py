from pymongo import MongoClient
from pprint import pprint
import os
import json
import mysql.connector
import datetime
from beautifultable import BeautifulTable


"""
a) Create a collection called “electronics” in “amazon” that contains each line of “reviews_electronics.16.json” as an individual document.
   Write code that reads all documents in “electronics”, and prints the first 25 documents to screen.
   Ignore the field “reviewText” for all subsequent questions.
b) Using Python or Java: Create a SQL database named “amazon_SQL”.
  In this database, create a SQL table named “electronics_SQL” that can hold each document from “electronics”.
c) Develop code (in Python or Java) that:
    (1) Reads all documents from “electronics” in MongoDB.
    (2) Writes that content to “electronics_SQL” in SQL. 
    (3) Print the first 25 documents to the screen. 
"""


### Part 2.a
# Read each line in "reviews_electronics.16.json" into a dictionary, and store all dictionaries into a list calledd "reviews".
os.chdir("/Users/xiongma/Documents/Sync/PYJY")
reviews = []
with open("reviews_electronics.16.json") as lines:
    for line in lines:
        review = json.loads(line.rstrip())
        del review["reviewText"]
        reviews.append(review)

# create a database called amazon and within it, a collection called review.
client = MongoClient()
db = client['amazon']
collection = db['eletronics']
print("DB in MongoDB created.\n\n")

# add the review data into the MongoDB.
print("Inserting documents into MongoDB...")
for review in reviews:
    collection.insert_one(review)

# print the first 25 documents in the electronics collection
collection = db['eletronics']
result = collection.find().limit(25)
print("Done. Printing the first 25 documents in MongoDB:\n\n")
for item in result:
    pprint(item)


### Part 2.b
# In MySQL, setup connection parameter
connection = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="")
cursor = connection.cursor()

# create a databse called "amazon_SQL".
cursor.execute("CREATE DATABASE amazon_SQL;")
cursor.execute("USE amazon_SQL")

#create the "electronics" table
create_table = """
CREATE TABLE electronics (
reviewerID VARCHAR(21),
asin VARCHAR(10),
reviewerName VARCHAR(200),
helpful_1 INT,
helpful_2 INT,
overall INT,
summary VARCHAR(200),
unixReviewTime INT(10),
reviewTime DATE,
ObjectID VARCHAR(25) PRIMARY KEY);"""
cursor.execute(create_table)


### Part 2.c
# Query all documents from MongoDB and store the result in a dictionary called "reviews"
client = MongoClient()
db = client['amazon']
collection = db['eletronics']
reviews = collection.find()


# Create a function to write one record to MySQL
def insert_review(review):
    reviewerID = review['reviewerID']
    asin = review['asin']
    try:    reviewerName = str(review['reviewerName'])
    except:    reviewerName = None
    helpful_1 = review['helpful'][0]
    helpful_2 = review['helpful'][1]
    overall = int(review['overall'])
    summary = review['summary']
    unixReviewTime = review['unixReviewTime']
    reviewTime = datetime.datetime.strptime(review['reviewTime'], "%m %d, %Y")
    reviewTime = reviewTime.strftime('%Y-%m-%d')
    ObjectID = str(review['_id'])
    sql = "INSERT INTO electronics (reviewerID, asin, reviewerName, helpful_1, helpful_2, overall, summary, unixReviewTime, reviewTime, ObjectID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (reviewerID, asin, reviewerName, helpful_1, helpful_2, overall, summary, unixReviewTime, reviewTime, ObjectID)
    cursor.execute(sql, val)
    connection.commit()

# write the query result from MongoDB to MySQL
print("Adding rows to MySQL...\n\n")
for review in reviews:
    insert_review(review)

# print the first 25 rows in MySQL
connection = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="",
    database="amazon_SQL")

cursor = connection.cursor()
sql = "select * from electronics limit 25"
cursor.execute(sql)
results = cursor.fetchall()

table = BeautifulTable(max_width=160)
table.column_headers = ["reviewerID", "asin", "reviewerName", "helpful_1", "helpful_2", "overall", "summary", "unixReviewTime", "reviewTime", "ObjectID"]
for result in results:
    table.append_row(result)
print("Done. Printing the first 25 rows in MySQL:\n\n")
print(table)