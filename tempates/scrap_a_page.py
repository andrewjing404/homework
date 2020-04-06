import requests
import os
from datetime import datetime

# Takes user defined URL, header, save directory, timeout, and naming rule.
# Scrap the webpage and save the file as .htm.

def get_htm(URL = None, headers = None, save_dir = os.getcwd(), timeout = 10, naming = "URL"+str(datetime.now().strftime("%b-%d-%Y-%H%M"))+".htm"):
    try:
        htm = requests.get(URL, headers=headers, tiemout=timeout)
    except:
        print(f"Timeout after {timeout} seconds, URL \"{URL}\" not scrapped.")
        break
    with open(naming, "w") as f:
        f.write(htm.text)