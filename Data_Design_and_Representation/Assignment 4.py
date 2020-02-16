import requests
import json
import mysql.connector
from fractions import Fraction

"""
The codes do a few things:
1. Lookup movie information from OMDb using its API;
2. Extract information and store them in MySQL.
"""


## Part 1 (a)
# search any movie with keyword "blade" and store the result in global environment - api_call
URL = "http://www.omdbapi.com/?apikey=6f8f781d{}{}"
search_type = "&s=" #use API to search
keyword = "blade"
api_request = URL.format(search_type, keyword) #search keyword "blade"
api_call = requests.get(api_request)
print(f"URL string that would search for all the movies containing the word \"blade\" is: \n{api_request}")
#http://www.omdbapi.com/?apikey=6f8f781d&s=blade <- the URL string used to search


## Part 1 (b)
# create a function to print json nicely
def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)
    
print("The search result is:")
jprint(api_call.json())


## Part 1 (c)
# print the search result of "blade" in a nicer way
result = json.loads(api_call.content) # parse the json
print(f"Search result of \"{keyword}\":\n")

# iterate through every movie that has "blade" in its name
for item in result["Search"]:
    print("ID: ", item["imdbID"])
    print("Title: ", item["Title"])
    print("Year: ", item["Year"], "\n")


## Part 2 (a)
# Done


## Part 2 (b)
#Reasons behind designing the database
"""
imdb_id would be varchar(20). varchar(10) might be fine, but want some redundency;
title would be varchar(200). It's determined by the longest movie name (https://www.imdb.com/title/tt0475343/?ref_=ttls_li_tt);
year will be year. We want year to be ordinal, so that we can do some filter or calculation on it.
"""


## Part 2 (c)
"""
We don't need to create an additional column as a primark key.
imdb_id can serve as the primary key.
"""


## Part 2 (d)
# crate connection with mysql
connection = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="")
cursor = connection.cursor()

#create the database and table
cursor.execute("CREATE DATABASE ucdavis;")
cursor.execute("USE ucdavis")
cursor.execute("CREATE TABLE omdb_test (imdb_id VARCHAR(20) PRIMARY KEY, title VARCHAR(200), year YEAR)")

# close the connection
cursor.close()
connection.close()


## Part 3 (a)
# my top 10 movies
top10 = ["The Lion King", "Arrival", "The Martian", "The Wandering Earth", "Taxi Driver", "Nausicaä of the+Valley of the Wind", "To Live", "Ghost In the Shell&y=1995", "Neon Genesis Evangelion%3A The End of Evangelion", "Up"]
top10_id = [] #create a list to store the IDs of my top 10 movies

# define a function to lookup movies using titles, and print their titles and IDs
def movie_title_lookup(movie_title):
    URL = "http://www.omdbapi.com/?apikey=6f8f781d{}{}"
    search_type = "&t="
    api_request = URL.format(search_type, movie_title)
    api_call = requests.get(api_request)
    result = json.loads(api_call.content)
    title = result["Title"]
    imdbID = result["imdbID"]
    top10_id.append(imdbID) #append the IMDB ID to top10_id list
    print(f"Movie Title: {title}")
    print(f"IMDB ID: {imdbID}\n")

# iterate through my top 10 list and call movie_title_lookup()
for movie in top10:
    movie_title_lookup(movie)


## Part 3 (b)
# define a function to lookup movies using IMDB IDs, and print their IMDB IDs and titles.
def movie_id_lookup(imdbID):
    URL = "http://www.omdbapi.com/?apikey=6f8f781d{}{}"
    search_type = "&i="
    api_request = URL.format(search_type, imdbID)
    api_call = requests.get(api_request)
    result = json.loads(api_call.content)
    print(f"IMDB ID: {imdbID}")
    print("Title: ", result['Title'], "\n")

# Iterate through my top_10_id list I created before and call movie_id_lookup() 
for id in top10_id:
    movie_id_lookup(id)


## Part 3 (c)
#connect to ucdavis database
connection = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="",
    database="ucdavis")
cursor = connection.cursor()

#create omdb table
create_table = """
CREATE TABLE omdb (
title VARCHAR(200) PRIMARY KEY,
year YEAR,
genre VARCHAR(200),
director VARCHAR(200),
imdb_rating INT,
rotten_tomatoes INT,
metacritic INT,
plot VARCHAR(1000),
box_office VARCHAR(30));"""
cursor.execute(create_table)

# define a function to write the information of a movie to omdb table
def movie_insert_db(movie_title):
    URL = "http://www.omdbapi.com/?apikey=6f8f781d{}{}"
    search_type = "&plot=full&t="   #full plot, and match movie title
    api_request = URL.format(search_type, movie_title)
    api_call = requests.get(api_request)
    result = json.loads(api_call.content)
    title = result["Title"]
    year = result["Year"]
    genre = result["Genre"]
    director = result["Director"]
    imdb_rating = int(float(result["imdbRating"])*10)   #unify the IMDB rating
    for item in result["Ratings"]:  #unify the Rotten Tomatoes rating
        if item["Source"] == "Rotten Tomatoes":
            rotten_tomatoes = item["Value"].strip("%")
            break
        else:
            rotten_tomatoes = None
    for item in result["Ratings"]:  #unify the Metacritic rating
        if item["Source"] == "Metacritic":
            metacritic = int(Fraction(item["Value"])*100)
            break
        else:
            metacritic = None
    plot = result["Plot"]
    box_office = result["BoxOffice"]
    sql = "INSERT INTO omdb (title, year, genre, director, imdb_rating, rotten_tomatoes, metacritic, plot, box_office) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (title, year, genre, director, imdb_rating, rotten_tomatoes, metacritic, plot, box_office)
    cursor.execute(sql, val)
    connection.commit()

#iterate through my top 10 list and call movie_insert_db()
for movie in top10:
    movie_insert_db(movie)

#close the connection with database
connection.close()