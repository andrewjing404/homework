#Part 1, RegEx
"""
Read a CSV into plain text and extract information using regular expression:
    - email;
    - birthday, and convert it to the US format;
    - longitute and latitude, then seperate them into two columns;
"""

import pandas as pd
import os
import re

os.chdir("/Users/xiongma/Documents/Sync/PYJY")


#Part 1.1
# identify non-standard birthday format and convert it to US format
mock1 = open("mock_data.csv").read()

pattern = re.compile(r"([0-9]{2})\.([0-9]{2})\.([0-9]{4})") # identify non-standard birthday format and convert it to US format

print(re.sub(pattern, r"\2/\1/\3",mock1))


#Part 1.2
# select only the emails from the text
mock2 = open("mock_data.csv").read()

pattern2 = re.compile(r"..*\",(.+@.+?),.*") # select only the emails from the text
mock2 = re.sub(pattern2, r"\1", mock2)

pattern22 = re.compile(r".*(email).*")
print(re.sub(pattern22, "\1", mock2))


#Part 1.3
# concat name with birthday, seperate by tab
mock3 = open("mock_data.csv").read()

pattern3 = re.compile(r"([0-9]{2})\.([0-9]{2})\.([0-9]{4})")
mock33 = re.sub(pattern3, r"\2/\1/\3", mock3)

pattern33 = re.compile(r"([0-9]{2}/[0-9]{2}/[0-9]{4}).*?-[0-9]{4},(.*?),") # concat name with birthday, seperate by tab
mock333 = re.findall(pattern33, mock33)

text = "name\tbirthday\t"


for item in mock333:
    text += item[1]
    text += "\t"
    text += item[0]
    text += "\t"

print(text)

#Part 1.4
# split the lat-lon into two columns
mock4 = open("mock_data.csv").read()

pattern4 = re.compile(r'\"([-.0-9]*?), ([-.0-9]*?)\"') # split the lat-lon into two columns

mock44 = re.findall(pattern4, mock4)

text = "long\tlat\t"

for item in mock44:
    text += item[1]
    text += "\t"
    text += item[0]
    text += "\t"

print(text)


#Part 2
import requests
from bs4 import BeautifulSoup
import re

"""
Connect to US News, scrap the second top story. Extract the:
    - Title
    - URL
    - First three sentences
"""

URL = "https://www.usnews.com/"
headers = {"user-agent": 'Mozilla/5.0'}
strhtml = requests.get(URL, headers=headers)
soup = BeautifulSoup(strhtml.content, 'lxml')

table = soup.find('h2', text="Top Stories").parent.find_all('h3')

for item in table:
    title = item.text
    URL2 = item.a.attrs['href']
    
print("second top story title: ", title)
print("second top story URL: ", URL2)

strhtml2 = requests.get(URL2, headers=headers)

soup2 = BeautifulSoup(strhtml2.content, 'lxml')

print("header: ", soup2.h1.text)

soup3 = soup2.find_all('div', {"id": "ad-in-text-target"})

text = ""

for item in soup3:
    text += item.text

pattern = re.compile(r"^.{25,}?[\.].{25,}?[\.].{25,}?[\.]") # identify the first three sentences

print("first 3 sentences: ", pattern.findall(text))