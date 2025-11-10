import asyncio
import pathlib
import sys
import time
import urllib.parse
import requests
import argparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from tqdm import tqdm

class WebScrapper:

    def __init__(self, url, level=1):
        self.url = url
        self.level = level
        self.main(url, level)

    def main(self,url,level):
        if level == 1:
            response = requests.get(url,timeout=None)
            if response.status_code == 200:
                webData = BeautifulSoup(response.text, "html.parser")

                #Writing Website content in the 'content.txt' file
                with open(dir_path_l1 / "content.txt" ,'w', encoding='utf-8') as file_path_l1:
                    file_path_l1.write(str(webData.text.split()))

                #Cloning the website in the file 'clone.html' file
                with open(dir_path_l1 / "clone.html",'w', encoding='utf-8') as file_path_l1:
                    file_path_l1.write(webData.prettify())

                #Downloading image resource in the directory "Resources"
                resources_path = dir_path_l1 / "Resources"
                resources_path.mkdir(parents=True, exist_ok=True)
                resources_data = list(map(lambda a: urllib.parse.urljoin(url,a.get('src')),webData.find_all("img")))
                for i in range(len(resources_data)):
                    try:
                        with open(resources_path / f"{resources_data[i].split('/')[-1]}",
                                  "wb") as file_path_l1:
                            print(resources_data[i])
                            file_path_l1.write(requests.get(resources_data[i]).content)
                    except PermissionError as e:
                        print("Permission Error: "+str(e))

                # Downloading video resource in the directory "Resources"
                resources_data = list(
                    map(lambda a: urllib.parse.urljoin(url, a.get('src')), webData.find_all("source")))
                for i in range(len(resources_data)):
                    try:
                        with open(resources_path / f"{resources_data[i].split('/')[-1]}",
                                  "wb") as file_path_l1:
                            print(resources_data[i])
                            file_path_l1.write(requests.get(resources_data[i]).content)
                    except PermissionError as e:
                        print("Permission Error: " + str(e))

        elif level == 2:
            pass
        elif level == 3:
            with sync_playwright() as player:
                browser = player.chromium.launch(headless=False)
                page = browser.new_page()
                page.goto(url)
                soup = BeautifulSoup(page.content(),'html.parse')
                with open(dir_path_l2 / "content.txt","w",encoding="utf-8") as file_path_l1:
                    file_path_l1.writelines(soup.text.split())
                with open("clone.html","w",encoding="utf-8") as file_path_l1:
                    file_path_l1.write(soup.prettify())



        else:
            raise argparse.ArgumentTypeError("Level must be between 1 and 3")

#Initialize the parser
parser = argparse.ArgumentParser(
    description="A command-line tool for performing web-scraping"
)

#Adding Positional Arguments
parser.add_argument(
    'url',
    metavar='URL',
    type=str,
    help='The URL of the webpage to scrape (www.domainname.com)'
)

parser.add_argument(
    "-l",
    "--level",
    metavar='L',
    type=int,
    default=1,
    help="The depth level for scraping (default: 1)"
)

try:
    #Parsing the arguments
    arguments = parser.parse_args()
except SystemExit:
    sys.exit()

base_path = pathlib.Path.cwd()
dir_path_l1 = base_path / f"{str(arguments.url).split(r"://")[1]}"/"level_1"
dir_path_l2 = base_path / f"{str(arguments.url).split(r"://")[1]}"/"level_2"
dir_path_l3 = base_path / f"{str(arguments.url).split(r"://")[1]}"/"level_3"

try:
    dir_path_l1.mkdir(parents=True, exist_ok=True)
    dir_path_l2.mkdir(parents=True, exist_ok=True)
    dir_path_l3.mkdir(parents=True, exist_ok=True)
except OSError:
    print("Error in File Creation")

WebScrapper(arguments.url,arguments.level)
sys.exit()