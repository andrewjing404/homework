import json
import twint
import urllib.request
import csv
import os

### set parameters ###
resume_dir = "" # create a document to track the progress of image scraping
output_dest = "" # create a csv file to store the scraped info
store_dest = "" # define which place to store the scraped images
user_name = "" # scrape which twitter user

c = twint.Config()
c.Username = user_name
#c.Limit = 20
#c.Resume = resume_dir
c.Store_csv = True
c.Output = output_dest
c.Images = True
### end ###

twint.run.Search(c)

# extract links to images
photo_links = []
with open(output_dest, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        links = row['photos'].replace("'", "").strip('][').split(', ')
        for link in links:
                photo_links.append(link)

# download and save images
for url in photo_links:
    img_name = os.path.join(store_dest, os.path.basename(url))
    try:
        urllib.request.urlretrieve(url, img_name)
    except:
        print(url, "redownload")
        pass