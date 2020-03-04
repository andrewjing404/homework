from selenium import webdriver
import re
import os
from datetime import datetime
import requests
import time
from bs4 import BeautifulSoup


### Settings
# Define the location of the webdriver
browser = webdriver.Chrome("/Users/xiongma/Downloads/chromedriver")
# Define the working directory
os.chdir("/Users/xiongma/Documents/Sync/UCD Stuff/Courses/BAX422 Data Design & Representation/Assignment")


### Main Function
""" 
What does scrape_tag() do:
    What each argument does:
    tag: what tag to scrape;
    scrape_interval: time interval (in seconds) between each scrape. Recommend to be 1800 (30min);
    scrape_repeat_times: for this tag, scrape how many times.

1) Create a folder to store all the results of the web scraping;
2) Based on the tag, scrape interval, and number of scrapes you defined, scrape the top posts on Instagram;
4) Gather the following information of the top posts:
    - download the image
    - get the description of the post
    - get the number of likes
    - get the profile name of whom posted the post
    - get the profile bio
    - get the number of the profile's follower 
5) Store all the information into a database
"""

def scrape_tag(tag, scrape_interval, scrape_repeat_times):
    count = 1
    while True:
        new_folder = "ScrapeIG_"+tag
        try:
            os.mkdir(new_folder)
            os.chdir(new_folder+"/")
        except:
            os.chdir(new_folder+"/")
        new_top_posts = get_top_posts_URLs(tag)
        profile_URLs, image_URLs, top_post_likes, top_post_description = get_post_info(new_top_posts, tag)
        profile_name, profile_bio, profile_follower = get_profile_info(profile_URLs)
        write_info(tag, image_URLs, top_post_likes, top_post_description, profile_name, profile_bio, profile_follower)
        count += 1
        if count <= scrape_repeat_times:
            print(f"Tag \"{tag}\" scraped {count}/{scrape_repeat_times} times. Sleep for {scrape_interval} seconds.")
            time.sleep(scrape_interval)
        else:
            print(f"\"{Tag}\" scrape finished. Saved to {os.getcwd()}.")
            os.chdir("../")
            break


"""
How get_top_posts_URLs(), existing_URLs(), and add_to_existing_URLs() work:
1) The main function - scrape_tag() will call get_top_posts_URLs();
2) get_top_posts_URLs() will get the URLs to the top posts of the tag you defined;
3) Then, get_top_posts_URLs() will call existing_URLs() to open a .txt file, which contains all the URLs we've scraped.
   The function will identify which URLs have never been scraped;
   (because you might see the same post in two scrapes and we don't want duplication)
4) get_top_posts_URLs() will then call add_to_existing_URLs() and add the new URLs to the .txt file mentioned in 3);
5) Download the search result page and name it "scrape time + tag + _search_result.htm";
6) Finally, get_top_posts_URLs() will return a list called "new_top_posts", which contains all the new URLs.
"""

def get_top_posts_URLs(tag):
    URL = "https://www.instagram.com/explore/tags/{}".format(tag)   # URL of the search result of a tag
    browser.get(URL)
    _new_top_posts = []
    new_top_posts = []
    _all_URLs = [a.get_attribute('href') for a in browser.find_elements_by_tag_name('a')]
    for URL in _all_URLs:
        if "/p/" in URL:   # identify the URL to a post
            _new_top_posts.append(URL)
    _new_top_posts = _new_top_posts[0:9]   # there are only 9 top posts on the search result
    try:
        for URL in _new_top_posts:
            if URL not in existing_URLs(tag, _new_top_posts):
                new_top_posts.append(URL)
        add_to_existing_URLs(tag, new_top_posts)
    except:
        pass
    content = browser.page_source
    scrape_time = str(datetime.now().strftime("%b-%d-%Y-%H%M%S"))
    with open(scrape_time+tag+"_search_result.htm", mode='w', encoding='UTF-8', errors='strict', buffering=1) as f:   # download the search result page
        f.write(content)
    return(new_top_posts)

def existing_URLs(tag, _new_top_posts):
    try:
        with open(tag+"_top_posts.txt", "r") as f:
            all_top_posts = [link.rstrip('\n') for link in f]
    except:
        all_top_posts = []
    return(all_top_posts)

def add_to_existing_URLs(tag, new_top_posts):
    with open(tag+"_top_posts.txt", "w") as f:   # this .txt file will contain all the scraped URLs of a tag
        for link in new_top_posts:
            f.write('%s\n' % link)


"""
How get_post_info(), download_image() work:
1) get_post_info() takes the list of URLs (top posts) generated from get_top_posts_URLs();
2) get_post_info() will identify the URL to the profile of whom posted the top post and store them into a list;
3) get_post_info() will call download_image() and download the image of each top post. 
   Image will be the highest resolution version and named as "tag + suffix of the Instagram URL.jpg". Videos will be ignored;
4) download_image() will download the page of the post and save it as "time + tag + webpage URL suffix + _post.htm".
   Then return a list of local URLs to the downloaded images;
5) Finally, get_post_info() will return four lists: profile_URLs, image_URLs, top_post_likes, top_post_description.
   They are URLs to the profiles, URLs to the downloaded images, number of likes of each top post, and the description of the top post.
   Elements in each list have the same order as "new_top_posts" generated from get_top_posts_URLs().
"""

def get_post_info(new_top_posts, tag):
    profile_URLs = []
    image_URLs = []
    top_post_likes = []
    top_post_description = []
    for URL in new_top_posts:
        browser.get(URL)
        _links = [a.get_attribute('href') for a in browser.find_elements_by_tag_name('a')]
        profile_URLs.append(_links[0])   # URL to the profile
        image_URLs.append(download_image(URL))   # pass URL to help naming the image
        time.sleep(10)
        # more codes to get likes and description
    return(profile_URLs, image_URLs, top_post_likes, top_post_description)

def download_image(URL, tag):
    try:
        img_links = [a.get_attribute('srcset') for a in browser.find_elements_by_tag_name('img')]
        _top_pic = img_links[1]
        _top_pic = re.findall(r"(https.*?) [0-9]+w", _top_pic)[-1]
        _top_pic = requests.get(_top_pic)
        naming = re.search(r"/p/(.*)/", URL).group(1)
        open(tag+naming+'.jpg', 'wb').write(_top_pic.content)
        content = browser.page_source
        scrape_time = str(datetime.now().strftime("%b-%d-%Y-%H%M%S"))
        with open(scrape_time+tag+naming+"_post.htm", mode='w', encoding='UTF-8', errors='strict', buffering=1) as f:   # download the page of the post
            f.write(content)
        return("ScrapeIG_"+tag+"/"+tag+naming+'.jpg')
    except:
        return("")


"""
How get_profile_info():
1) get_profile_info() will take profile_URLs, the list of profile URLs, and go into each URL;
2) get_profile_info() will download the webpage of the profile and store it as "time + name + _profile.htm";
2) get_profile_info() identify the name of the profile, the number of followers, and the profile bio, and 
   return them via three lists: profile_name, profile_follower, profile_bio. 
   Elements in each list have the same order as "new_top_posts" generated from get_top_posts_URLs(). 
"""

def get_profile_info(profile_URLs):
    profile_name = []
    profile_follower = []
    profile_bio = []
    for URL in profile_URLs:
        browser.get(URL)
        content = browser.page_source
        scrape_time = str(datetime.now().strftime("%b-%d-%Y-%H%M%S"))
        with open(scrape_time+name+"_profile.htm", mode='w', encoding='UTF-8', errors='strict', buffering=1) as f:   # download the page of the profile
            f.write(content)
        #scrape profile info
    return(profile_name, profile_bio, profile_follower)


"""
How write_info() works:
1) write_info() will take all the top post related information and store them into a database;
2) Image will be stored as a relative URL to the local machine.
"""
def write_info(tag, new_top_posts, top_post_likes, top_post_description, profile_name, profile_bio, profile_follower):
    # write into database