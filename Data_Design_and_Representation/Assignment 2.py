import os.path
import requests
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

"""
These codes do several things:
1. Go to https://www.ebay.com and search for "samsung tv";
2. Save the listings in the first 10 result pages into local htm files;
3. Loop through each saved htm files and identify sponsored listings using regular expression.
"""

## Sets parameters for the web scraping job
#header
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

#search key words
key_word = "samsung+TV" 

#how many pages of search result
max_page_number = 10 

#url template of the search result
URL = "https://www.ebay.com/sch/i.html?_nkw={}&_pgn={}" 

#naming slug when saving the search result
slug = "ebay_samsung_tv_<{}>.htm" 

#sleep time between scraping each page, in second
sleep_time = 10 

#save search result to which directory
os.chdir(os.getcwd())
save_path = os.getcwd()+"/"+scrap_time + "/"
scrap_time = str(datetime.now().strftime("%b-%d-%Y-%H%M%S"))


## scrapping function 
def scrap_web():
    os.makedirs(save_path)
    previous_path = os.getcwd()
    os.chdir(save_path)
    print("Scraped at time: ", scrap_time)
    print('files saved to directory: ', save_path+"/"+scrap_time + "/")
    for i in range(1, max_page_number+1):
        print("Getting page: ", i)
        link = URL.format(key_word, i)
        r = requests.get(link, headers=headers, timeout=5)
        if i < 10:
            page_num = str(0)+str(i)
        else:
            page_num = str(i)
        page_name = slug.format(page_num)
        with open(page_name, mode='w', encoding='UTF-8', errors='strict', buffering=1) as f:
            f.write(r.text)
        if i < max_page_number+1:
            time.sleep(sleep_time)
            print(f"Hibernate for {sleep_time} seconds. Don't poke the bear.")
    os.chdir(previous_path)
    print("Scrap finished.")
    print("Saved to: ", save_path)


## calls the scrap function
scrap_web()

## Sets info extraction rules and identify sponsored listings
pattern = re.compile(".*S.*P.*O.*N.*S.*O.*R.*")
sponsored = {}

for filename in os.listdir(save_path):
    with open(filename, 'r') as f:
        soup = BeautifulSoup(f)
    for item in soup.find_all('a', {'class': 's-item__link'}):
        if re.match(pattern, item.text):
            sponsored[item.h3.text] = item.attrs['href']

## print the result
print(sponsored)
print(f"Found {len(sponsored)} sponsored items.")