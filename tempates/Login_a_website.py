import os
import requests
from bs4 import BeautifulSoup

# defines the url and the headers
URL = "https://www.allrecipes.com/account/signin/"
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}


# defines a function to get the token that will be used to log in
def get_token():
    allrecipes = requests.get(URL, headers=headers, timeout=5).content
    soup = BeautifulSoup(allrecipes, 'lxml')
    return(soup.find('input', attrs={'id': 'SocialCsrfToken'})['value'])


# log in, and return the parsed logged in page
def log_in():
    session = requests.Session()
    log_in_info = {
        "ReferringType": "",
        "ReferringUrl": "https://www.allrecipes.com/",
        "ReferringAction": "",
        "ReferringParams": "",
        "AuthLayoutMode": "Standard",
        "txtUserNameOrEmail": "login_username",
        "password": "password",
        "rememberMe": "on"}
    log_in_info["SocialCsrfToken"] = get_token()
    jar = requests.cookies.RequestsCookieJar()
    session.cookies = jar
    allrecipes = session.post(URL, data=log_in_info, headers=headers, timeout=5)
    soup = BeautifulSoup(allrecipes.content, 'lxml')
    return(soup)


# don't forget to check login status