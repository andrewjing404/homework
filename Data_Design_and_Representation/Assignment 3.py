from bs4 import BeautifulSoup
import requests
import re
import os

"""
The codes do a few things:
a) Connect to https://www.thyssenkrupp-elevator.com/kr/products/multi/;
b) Save the webpage to a local htm file, use UTF-8 to encode;
c) Open the htm file as plain text;
d) Create a single search-and-replace RegEx that strips all <tag>s + run it;
e) Create a single search-and-replace RegEx that grabs the Korean character that occurs right before ".";
f) Count the most frequent Korean character
"""

URL = "https://www.thyssenkrupp-elevator.com/kr/products/multi/"
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.113 Safari/537.36'}
save_directory = os.getcwd() + "/HW3/" #Create a folder and save all the files to it

# save URL to local htm file
def save_htm():
    print("Begin scrapping.\n")
    os.mkdir(save_directory)
    get_page = requests.get(url=URL, headers=headers)
    save_name = "elevator.htm"
    saved_to = save_directory + save_name
    with open(saved_to, mode='w', encoding='UTF-8', errors='strict', buffering=1) as f:
            f.write(get_page.text)
    print(f"Scrap finished. Saved to {saved_to}.\n\n")
    return(saved_to)

# strip all the tags
def strip_tags():
    txt = open(save_htm(), mode='r', encoding='UTF-8')
    txt = txt.read()
    pattern = re.compile(r"<.+?>")
    page_content = re.sub(pattern, "", txt)
    pattern2 = re.compile(r'\t')
    page_content = re.sub(pattern2, "", page_content)
    pattern3 = re.compile(r'\n')
    page_content = re.sub(pattern3, "", page_content)
    save_name = "page_content.txt"
    saved_to = save_directory + save_name
    with open(saved_to, mode="w", encoding="UTF-8") as f:
        f.write(str(page_content))
    print("Tags were stripped. Saved to ", save_directory, "page_content.txt\n")
    print(f"After removing the tags, the outcome is:\n{page_content}\n\n")
    return(saved_to)

# get every Korean character that meets the criteria
def get_korean():
    with open(strip_tags(), mode='r', encoding='UTF-8') as f:
        full_text = f.read()
    pattern = re.compile(r"([\u3131-\uD79D])\.")
    korean_characters = re.findall(pattern, full_text)
    save_name = "Korean_char.txt"
    saved_to = save_directory + save_name
    with open(saved_to, "w", encoding="UTF-8") as f:
        for character in korean_characters:
            f.write("%s\n" % character)
    print(f"Text file saved to {saved_to}.\n")
    print(f"All Korean characters before a . are:\n{korean_characters}\n\n")
    return(korean_characters)

# count the most occured Korean character
def most_occured_korean():
    korean_characters = get_korean()
    #count maximum occurance
    max = 0
    for character in korean_characters:
        if korean_characters.count(character) > max:
            max = korean_characters.count(character)
    #see how many characters have max occurance
    frequent_korean = []
    for character in korean_characters:
        if character not in frequent_korean:
            frequent_korean.append(character)
    print(f"Most common Korean characters are {', '.join(frequent_korean)}. They occured {max} times.")


most_occured_korean()