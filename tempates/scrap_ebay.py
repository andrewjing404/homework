import requests
import os
import time
from datetime import datetime
from bs4 import BeautifulSoup



def scrap_ebay():
    scrap_time = str(datetime.now().strftime("%b-%d-%Y-%H%M"))
    print(f"Search keywords: {key_word}\nItem per page: {item_per_page}\nFirst {max_page_number} pages will be scrapped.\nSleep time between each scrap is {sleep_time} seconds.\n\n")
    print(f"A new folder called \"eBay_scrap{scrap_time}\" will be created under \"{os.getcwd()}\", and results from Part 2 will be stored in it.\n")
    input("Is it ok? Press ENTER to continue.")
    print("Start to gather sponsor and non sponsor links.")
    os.mkdir("eBay_scrap"+scrap_time)
    os.chdir("eBay_scrap"+scrap_time)
    sponsored = []
    non_sponsored = []
    pattern = re.compile(".*S.*P.*O.*N.*S.*O.*R.*")
    for page in range(1, max_page_number+1):
        temp_URL = URL.format(key_word, item_per_page, page)
        try:
            temp_respond = requests.get(temp_URL, headers=headers, timeout=5)
            try:
                temp_respond = requests.get(temp_URL, headers=headers, timeout=5)
            except:
                temp_respond = requests.get(temp_URL, headers=headers, timeout=5)
        except requests.exceptions.Timeout:
            print(f"Timeout, skipping page {page}.")
            pass
        soup = BeautifulSoup(temp_respond.content, "lxml")
        for item in soup.find_all("a", {'class': 's-item__link'}):
            if re.match(pattern, item.text):
                sponsored.append(item.attrs['href'])
            else:
                non_sponsored.append(item.attrs['href'])
        print(f"Page {page}/{max_page_number} done.")
        if page < max_page_number:
            print(f"Hibernating for {sleep_time}s.")
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