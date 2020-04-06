import requests
import json
import os
import time
import re
import mysql.connector
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import random


############ Briefing of the Code ############
# The whole .py file contains multiple functions and do multiple things.
# Required python packages: bs4, mysql.connector, pandas, requests.
# Codes do these things:
#   1. Take keywords you defined and scrap the search result from eBay. Search result will be stored as htm file locally.
#   2. Identify key information of each listing item, including sponsorship, price, shipping policy, etc.
#   3. Pump those information into MySQL.
#   4. Query the database and get some basic descriptive analysis.
# It take quite a while for these codes to run, so be patient.
############    End of Briefing    ############


######### Parameters of the eBay scrap.

# Headers submit to GET.
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

# Search keyword. Use "+" to represent space.
key_word = "playstation+4+slim"  

# Items per search result page.
item_per_page = "100"

# Number of search result pages to go into.
max_page_number = 10 

# URL of the search page.
URL = "https://www.ebay.com/sch/i.html?_nkw={}&_ipg={}&_pgn={}" 

# Sleep time between each web scrap.
sleep_time = 4

# Connection information of the MySQL database
host = "127.0.0.1"
port = 3306
user = "root"
password = ""

# This is just for fun. Ignore it.
hibernation = ["wood frog", "Gila monster", "snail", "box turtle", "snake", "American black bear", "bee", "groundhog", "hummingbird", "bat", "skunk", "ladybug", "hedgehog", "common poorwills", "fat-tailed dwarf lemur", "marmot", "chipmunk", "deer mice", "prairie dog", "ground squirrel", "European hedgehog", "mouse lemur", "dormouse", "woodchuck", "Arctic ground squirrel", "sleeping student", "Asiatic black bear", "brown bear", "polar bear", "Draconians affected by Raistlin's sleep spell", "sleeping beauty", "mummy", "Ysera", "Malfurion", "Dom Cobb", "hibernation pod in Alien", "hibernation pod in 2001", "Smaug", "Dracula", "Caramon affected by Raistlin's sleep spell", "Snow White", "Simba's dad", "Snorlax"]

######### End of Parameters.




### Part 1 of the Codes 
"""
scrap_ebay() will create a folder with timpstamp in your current working directory and store all the following files in it.
Then the function will look into search result pages defined by the parameters (mainly keywords and depth of pages to look into).
When scraping each search result page, the function will retry two times after an failure before giving up.
Then, the function will identify sponsored and non-sponsored listing items.
Links to pponsored and non-sponsored listings will be stored in sponsored.txt and non_sponsored.txt, respectively.
"""

def scrap_ebay():
    scrap_time = str(datetime.now().strftime("%b-%d-%Y-%H%M"))  # create a timestamp for naming the folder
    print(f"Search keywords: {key_word}\nItem per page: {item_per_page}\nFirst {max_page_number} pages will be scrapped.\nSleep time between each scrap is {sleep_time} seconds.\n\n")
    print(f"A new folder called \"eBay_{scrap_time}\" will be created under \"{os.getcwd()}\", and results from Part 2 will be stored in it.\n")
    input("Press ENTER to continue.")
    print("Start to gather sponsor and non sponsor links.")
    os.mkdir("eBay_"+scrap_time)
    os.chdir("eBay_"+scrap_time)  
    sponsored = []
    non_sponsored = []
    for page in range(1, max_page_number+1):
        temp_URL = URL.format(key_word, item_per_page, page)
        try:
            temp_respond = requests.get(temp_URL, headers=headers, timeout=5)
            try:
                temp_respond = requests.get(temp_URL, headers=headers, timeout=5)
            except:
                temp_respond = requests.get(temp_URL, headers=headers, timeout=5)
        except requests.exceptions.Timeout:
            print(f"Timeout, skipping page {page}.")  # skip the timeout page after two retries.
            pass
        soup = BeautifulSoup(temp_respond.content, "lxml")
        pattern = re.compile(".*S.*P.*O.*N.*S.*O.*R.*")  #create a pattern used to identify sponsorship
        for item in soup.find_all("a", {'class': 's-item__link'}):  # identify sponsorship using regex
            if re.match(pattern, item.text):
                sponsored.append(item.attrs['href'])  # if sponsored, append the link to sponsored list
            else:
                non_sponsored.append(item.attrs['href'])  # if non-sponsored, append the link to non_sponsored list
        print(f"Page {page}/{max_page_number} done.")
        if page < max_page_number:
            print(f"Hibernating for {sleep_time}s, don't poke the {random.choice(hibernation)}.")
            time.sleep(sleep_time)
        elif page == max_page_number:
            with open("sponsored.txt", "w") as f:
                for item in sponsored:
                    f.write("%s\n" % item)
            with open("non_sponsored.txt", "w") as f:
                for item in non_sponsored:
                    f.write("%s\n" % item)
            print("Sponsorship identification complete.")
            print("Links to sponsored item are stored in \"sponsored.txt\";\nlinks to non-sponsored item are stored in \"non_sponsored.txt.\n")

scrap_ebay()

        
### Part 2 of the Codes
"""
download_ebay() will open the text file and store all the links in a list.
Then, it will create a folder and navigate into it.
Then, it will call download_ebay_each_page() and pass through the list of links.
Inside the newly created folder, download_ebay_each_page() does several things:
1. It identifies the item id from the link and use it to name the htm file;
2. It will try to download the listing pages using the list of links;
3. If some download failed, the failed link will be skipped and store into a new list;
4. After all rest of the links were downloaded, download_ebay_each_page() will call itself and pass through the list of previous failed link;
5. download_ebay_each_page() will retry 5 times before give up.

download_ebay() will be called twice to scrap sponsored and non_sponsored htm files.
"""

def download_ebay(txt, dir):
    link_list = []
    link_list = [line.rstrip('\n') for line in open(txt)]
    sleep_time = 2
    link_total = len(link_list)
    print(f"Will open \"{txt}\", scrap and download {link_total} files and save to \"{os.getcwd()}/{dir}\".\nSleep time between each scrap is {sleep_time} seconds.")
    input("Press ENTER to continue.")
    os.mkdir(dir)
    os.chdir(dir)
    download_ebay_each_page(link_list, sleep_time)  # call the function to download the htm files
    os.chdir("../")

def download_ebay_each_page(link_list, sleep_time, retry = 1):
    link_total = len(link_list)
    pattern = re.compile("/([0-9]+)\?")  # pattern used to identify the item id
    count = 1
    retry_list = []
    while True:  
        link = link_list.pop()
        filename = re.search(pattern, link).group(1)
        try:
            htm = requests.get(link, headers=headers, timeout=5)  
            with open(filename+".htm", "w") as f:
                f.write(htm.text)
            print(f"Link {count}/{link_total} scapped and saved.")
        except requests.exceptions.Timeout:
            print(f"Link {count} wasn't scrapped. Will retry later automatically.")
            retry_list.append(link)  # if download timeout, store the link into a retry list
            retry += 1  # keep track of how many tries have been made
            pass
        if count < link_total:
            print(f"Hibernate for {sleep_time}s. Don't poke the {random.choice(hibernation)}.")
            count += 1
            time.sleep(sleep_time)
            continue
        elif len(link_list) == 0 and len(retry_list) == 0:  # if all links were downloaded and no link in the retry list, break
            print(f"Link {count}/{link_total} scapped and saved. Phew!\nAll htm files saved to \"{os.getcwd()}\".\n")
            break
        elif retry in range (1, 6):  # if some link in the retry list, call itself but pass through the retry list
            print(f"Retrying the {retry} time to scrap the remaining {len(link_list)} pages.")
            download_ebay_each_page(retry_list, sleep_time, retry)
        elif retry > 5:  # give up after 5 tries, and spit out an error
            raise ImportError("Retried 5 times but still unable to download all the pages. Retry later, or change the network environment, or change the header.")

download_ebay("sponsored.txt", "sponsored")
download_ebay("non_sponsored.txt", "non_sponsored")
print("Done")


## Part 3 of the codes.
"""
loop_through_htm() takes multiple folders and will loop through each htm files in them, and call selector().
selector() will try to identify the needed information from the htm file, store them in a dictionary and pass it back to loop_through_htm().
Finally, loop_through_htm() will return all the information in a list (each element is a dictionary, representing an htm file).
Detailed explanation of how to extract the information will be commented in between selector().
"""

def selector(htm_file):
    with open(htm_file, "r") as f:
        soup = BeautifulSoup(f, "lxml")
    # obtain item_id from the file name
    item_id = htm_file.strip(".htm")
    """
    obtain seller_name:
    Most of the seller_name can be obtained from the span with class: "mbg-nw".
    Some extreme cases (like when eBay shows you "we also found similar seller"...)
    We need to look into the div with class: "seller-persona" and extract the seller_name.
    If all the approaches fail, return None.
    """
    try:
        seller_name = soup.find("span", {"class": "mbg-nw"}).text
    except:
        try:
            seller_name = soup.find("div", {"class": "seller-persona"}).find("a").attrs["title"]
        except:
            seller_name = None
    """
    obtain seller_score:
    Most of the seller_name can be obtained from the span with class: "mbg-l".
    Some extreme cases (like when eBay shows you "we also found similar seller"...)
    We need to look into the div with class: "seller-persona" and extract the seller_score.
    If all the approaches fail, return None.
    """
    try:
        seller_score = soup.find("span", {"class": "mbg-l"}).a.text
    except:
        try:
            seller_score = soup.find("div", {"class": "seller-persona"}).find("a").find_next_sibling("a").attrs["title"]
        except:
            seller_score = None
    """
    obtain currency
    Most of the currency can be obtained from the span with itemprop: "priceCurrency".
    If not found, will try a second approach: grab the text of the price and see if there are any hints of the currency unit.
    In the second approach, I only identify USD, AUD, and CAD.
    """
    try:
        currency = soup.find("span", {"itemprop": "priceCurrency"}).attrs["content"]
    except:
        currency = None
    if currency is None:
        try:
            temp_item_price = soup.find("span", {"id": "prcIsum"}).text
        except:
            try:
                temp_item_price = soup.find("span", {"class": "notranslate"}).text
            except:
                pass
        try:
            if "US" in temp_item_price:
                currency = "USD"
            elif "AU" in temp_item_price:
                currency = "AUD"
            elif "C" in temp_item_price:
                currency = "CAD"
        except:
            pass
    """
    obtain item_price
    Listing price will be stored in US cents.
    For non-bid item, most of the price can be found under id "prcIsum".
    For bidding item, most of the price can be found under id "prcIsum_bidPrice".
    For some discounted item or other cases, the best guess would be a certain h2 and a certain span.
    Additionally, if eBay offers a converted price in USD, will overide the previous prices with the converted price.
    Finally, all prices will be converted to US cents using some regex.
    Return None is no price can be found.
    """
    try:
        item_price = soup.find("span", {"class": "notranslate"}).text
    except:
        try:
            item_price = soup.find("span", {"id": "prcIsum"}).text
        except:
            try:
                item_price = soup.find("span", {"id": "prcIsum_bidPrice"}).text
            except:
                try:
                    item_price = soup.find("h2", {"class": "display-price"}).text
                except:
                    item_price = None   
    try:
        item_price = soup.find(id="convbinPrice").text
    except:
        try:
            item_price = soup.find(id="convbidPrice").text
        except:
            pass
    if item_price is not None:
        item_price = re.sub("[^0-9.]", "", item_price)  # only extract numbers and decimal point from the price
        item_price = int(round(float(item_price), 2)*100)  # convert the price into float, round it to two digit, times 100, and truncate to integer
    """
    obtain num_items_sold
    Most of the num_items_sold can be obtained from the a with class: "vi-txt-underline".
    Store the information as a number.
    Return None if not found.
    """
    try:
        num_items_sold = int(soup.find("a", {"class": "vi-txt-underline"}).text.strip(" sold"))
    except:
        num_items_sold = None
    """
    obtain best_offer_available
    If "Best Offer" is in the text of a tag whose id is "boBtn_btn", then seller accepts offers.
    """
    try:
        if "Make Offer" in soup.find(id="boBtn_btn").text:
            best_offer_available = 1
    except:
            best_offer_available = 0
    """
    obtain returns_allowed
    Most of them can be found in id "vi-ret-accrd-txt".
    For some rare cases, I need to look into the li whose class is "item-highlight".
    It's a special no return case, that eBay will pay you if the good is bad.
    Return None if no information.  
    """
    returns_allowed = None
    try:
        returns_allowed = soup.find("span", {"id": "vi-ret-accrd-txt"}).text
    except:
        try:
            temp_soup = soup.find_all("li", {"class": "item-highlight"})
            for i in temp_soup:
                if "No returns, but backed by eBay Money back guarantee" in i.text:
                    returns_allowed = "No returns, but backed by eBay Money back guarantee"
                    break
                else:
                    returns_allowed = None
        except:
            returns_allowed = None
    """
    obtain shipping_price
    Most of the shipping_price can be found in the span under id "shSummary".
    Will try to obtain a numerical shipping in US cents (through some regex).
    Return None if not found.
    """
    try:
        shipping_price = soup.find(id="shSummary").findChild("span").text.replace("\n", "").replace("\t", "")  # clean out the text
        try:
            shipping_price = re.search("([.0-9]+)\)", shipping_price).group(1)  # if shipping cost not in USD, match with this regex
        except:
            try:
                shipping_price = re.search("\$([.0-9]+)", shipping_price).group(1)  # if shipping cost in USD, match with this regex
            except:
                pass
        try:    
            shipping_price = float(shipping_price)
            shipping_price = int(round(shipping_price, 2)*100)
        except:
            pass
    except:
        shipping_price = None
    """
    obtain item_condition
    Most of the item_condition can be found in the div with itemprop: "itemCondition".
    In some rare cases, I need to look into id "hero-item", and loop through its contents.
    Return None if not found any information.
    """
    try:
        item_condition = soup.find("div", {"itemprop": "itemCondition"}).text
    except:
        try:
            temp_soup = soup.find("id" == "hero-item").find_all("span", {"class": "cc-ts-BOLD"})
            for i in temp_soup:
                if i.text == "New":
                    item_condition = "New"
                    break
                else:
                    item_condition = None
        except:
            item_condition = None
    info = dict(
        item_id=item_id, seller_name=seller_name, 
        seller_score=seller_score, item_price=item_price, 
        currency=currency, num_items_sold=num_items_sold, 
        best_offer_available=best_offer_available, returns_allowed=returns_allowed, 
        shipping_price=shipping_price, item_condition=item_condition)
    return(info)  # All information will be stored into a dictionary and be passed back to the previous function

def loop_through_htm(*folders):
    print(f"Will extract htm files in {folders} folders.")
    input("Press ENTER to continue.\n")
    result = []
    for folder in folders:
        print(f"Start processing all htm files in {folder} folder...")
        os.chdir(folder)
        """
        obtain sponsor_status
        Sponsorship information will be identified from the folder name.
        """
        sponsor_status = {"sponsor_status": str(folder)}  
        for each_file in os.listdir():  # loop through each file in the folder and call selector() to gather information
            temp_result = selector(each_file)
            temp_result.update(sponsor_status)
            result.append(temp_result)
        os.chdir("../")
        print(f"{folder} folder complete.\n")
    print("All folders complete.")
    return(result)

grand_result = loop_through_htm("sponsored", "non_sponsored")  # the result will be stored in the global environment for later use


## Part 4 of the codes.
"""
Nothing too much to talk about, create a database and table. Except:
-1. I use MySQL
0. Running my code will drop existing database named "eBay"!
1. Maximum length of item_id should be 19, but eBay recommend 38 for redundency;
2. Item_id can't be used as the primary key. They have duplication;
3. maximum length of seller_name is 128;
4. It seems that eBay allow you to write length return policy and item condition. 
5. Establish a connection with the database until the end of the code.

This part will call prepare_db() to create database and table.
Then will call write_db() to write the grand_result from Part 2-d into the table.
"""

try:
    connection.close()
except:
    pass
connection = mysql.connector.connect(
    host=host,
    port=port,
    user=user,
    password=password)
cursor = connection.cursor()

def prepare_db():
    print("Will drop (if exist) and create a database called \"eBay\".")
    print("Will create a table called \"eBay_items\".")
    print(f"Databse: MySQL, host = {host}, port = {port}, user = {user}, password = {password}.")
    input("Press ENTER to continue.")
    cursor = connection.cursor()
    cursor.execute("DROP DATABASE IF EXISTS eBay;")
    cursor.execute("CREATE DATABASE eBay;")
    cursor.execute("USE eBay;")
    cursor.execute("""
                   CREATE TABLE eBay_items 
                   (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                   item_id VARCHAR(38), 
                   seller_name VARCHAR(128), 
                   seller_score INT, 
                   item_price INT, 
                   currency VARCHAR(6), 
                   num_items_sold INT, 
                   best_offer_available INT, 
                   returns_allowed VARCHAR(100), 
                   shipping_price VARCHAR(100), 
                   item_condition VARCHAR(1000),
                   sponsor_status VARCHAR(20));""")
    print("Done. Database and table are created.\n\n")

def write_db(data):
    print("Writing database.")
    query = "INSERT INTO eBay_items (item_id, seller_name, seller_score, item_price, currency, num_items_sold, best_offer_available, returns_allowed, shipping_price, item_condition, sponsor_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = connection.cursor()
    for item in data:
        val = (item["item_id"], item["seller_name"], item["seller_score"], item["item_price"], item["currency"], item["num_items_sold"], item["best_offer_available"], item["returns_allowed"], item["shipping_price"], item["item_condition"], item["sponsor_status"])
        cursor.execute(query, val)
        connection.commit()
    print("Complete.")

prepare_db()
write_db(grand_result)


## Part 5 of the codes.
"""
Will display the query I wrote:
0. Need a WIDE screen. Please stretch your window wide atleast.
1. The table has been transposed before displaying.
2. Grouped by item condition and sponsorship, looked into:
    a. how many listing under each grouping;
    b. basic stats of the pricel;
    c. basic stats of the seller score (and yes, it can be negative);
    d. basic stats of number of items sold;
    e. counts of item accept and not accept offer;
    f. number of return_allowed;
    g. basic stats of shipping price (for those non-categorical shipping prices)
    h. counts of some other shipping methods
3. Close the connection with the database.
"""
def print_query():
    print("Printing the result of the query.\nYou will need a >>WIDE<< screen.")
    input("Press ENTER to confirm WIDE screen.\n")
    cursor = connection.cursor()
    cursor.execute("use eBay;")
    query = """select sponsor_status, item_condition, count(*) as Item_Count, count(distinct seller_name) as Num_of_Distinct_Sellers, round(max(item_price)/100, 2) as Max_Price_in_USD, round(min(item_price)/100, 2) as Min_Price_in_USD, round(avg(item_price)/100, 2) as Mean_Price_in_USD, max(seller_score) as Max_Seller_Score, min(seller_score) as Min_Seller_Score, round(avg(seller_score)) as Mean_Seller_Score, max(num_items_sold) as Max_Num_Items_Sold, min(num_items_sold) as Min_Num_Items_Sold, round(avg(num_items_sold)) as Mean_Num_Items_Sold, sum(best_offer_available) as Accept_Offer, sum(if(best_offer_available = 0, 1, 0)) as Not_Accept_Offer, sum(if(returns_allowed like "%does not accept%", 0, 1)) as Returns_Allowed, round(max(cast(if(shipping_price like BINARY "%FREE%", 0, shipping_price) AS unsigned))/100, 2) as Max_Shipping_Price_in_USD, round(MIN(cast(if(shipping_price like BINARY "%FREE%", 0, shipping_price) AS unsigned))/100, 2) as Min_Shipping_Price_in_USD, round(AVG(cast(if(shipping_price like BINARY "%FREE%", 0, shipping_price) AS unsigned))/100, 2) as Mean_Shipping_Price_in_USD, SUM(if(shipping_price = "FAST 'N FREE", 1, 0)) as FAST_N_FREE_Shipping_Count, SUM(if(shipping_price = "Free Local Pickup", 1, 0)) as Free_Local_Pickup_Count, SUM(if(shipping_price = "Local pick-up offered.", 1, 0)) as Local_Pickup_Offered_Count, SUM(if(shipping_price = "Varies based on location and shipping method", 1, 0)) as Shipping_Price_Depends_on_Location_Count from eBay_items group by sponsor_status, item_condition"""
    cursor.execute(query)
    columns = cursor.column_names
    result = cursor.fetchall()
    result = pd.DataFrame(result, columns=columns).transpose()
    pd.set_option("display.expand_frame_repr", False)
    print(result)
    print("\nNot WIDE enought? Readjust the window and enter \"1\" to print the result one more time.\n")
    response = input("Enter \"1\" to re-print. Enter anything else to continue.\n>>")
    if response == "1":
        print_query()
    else:
        pass

print_query()
connection.close()
print("End.")