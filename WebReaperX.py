import asyncio
import pathlib
import sys
import time
import urllib.parse
import requests
import argparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from pywebcopy import save_website
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
                browser = player.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle")
                webData = BeautifulSoup(page.content(), 'html.parser')

                # Writing Website content in the 'content.txt' file
                with open(dir_path_l3 / "content.txt", "w", encoding="utf-8") as file_path_l3:
                    file_path_l3.write(str(webData.text.split()))

                # Cloning the website in the file 'clone.html' file
                with open(dir_path_l3 / "clone.html", "w", encoding="utf-8") as file_path_l3:
                    file_path_l3.write(webData.prettify())

                # Create Resources directory
                resources_path = dir_path_l3 / "Resources"
                resources_path.mkdir(parents=True, exist_ok=True)

                # Downloading image resources
                print("\n[*] Downloading images...")
                images = webData.find_all("img")
                for img in tqdm(images, desc="Images"):
                    src = img.get('src') or img.get('data-src')
                    if src:
                        try:
                            img_url = urllib.parse.urljoin(url, src)
                            filename = src.split('/')[-1].split('?')[0]
                            if filename:
                                response = page.request.get(img_url)
                                if response.ok:
                                    with open(resources_path / filename, "wb") as f:
                                        f.write(response.body())
                        except Exception as e:
                            print(f"Error downloading image {src}: {e}")

                # Downloading video resources
                print("\n[*] Downloading videos...")
                videos = webData.find_all("video")
                video_sources = webData.find_all("source")
                for video in tqdm(videos + video_sources, desc="Videos"):
                    src = video.get('src')
                    if src:
                        try:
                            video_url = urllib.parse.urljoin(url, src)
                            filename = src.split('/')[-1].split('?')[0]
                            if filename:
                                response = page.request.get(video_url)
                                if response.ok:
                                    with open(resources_path / filename, "wb") as f:
                                        f.write(response.body())
                        except Exception as e:
                            print(f"Error downloading video {src}: {e}")

                # Downloading audio resources
                print("\n[*] Downloading audio...")
                audios = webData.find_all("audio")
                audio_sources = webData.find_all("source", {"type": lambda x: x and "audio" in x})
                for audio in tqdm(audios + audio_sources, desc="Audio"):
                    src = audio.get('src')
                    if src:
                        try:
                            audio_url = urllib.parse.urljoin(url, src)
                            filename = src.split('/')[-1].split('?')[0]
                            if filename:
                                response = page.request.get(audio_url)
                                if response.ok:
                                    with open(resources_path / filename, "wb") as f:
                                        f.write(response.body())
                        except Exception as e:
                            print(f"Error downloading audio {src}: {e}")

                # Downloading CSS stylesheets
                print("\n[*] Downloading stylesheets...")
                stylesheets = webData.find_all("link", {"rel": "stylesheet"})
                for css in tqdm(stylesheets, desc="CSS"):
                    href = css.get('href')
                    if href:
                        try:
                            css_url = urllib.parse.urljoin(url, href)
                            filename = href.split('/')[-1].split('?')[0]
                            if filename:
                                response = page.request.get(css_url)
                                if response.ok:
                                    with open(resources_path / filename, "wb") as f:
                                        f.write(response.body())
                        except Exception as e:
                            print(f"Error downloading stylesheet {href}: {e}")

                # Downloading JavaScript files
                print("\n[*] Downloading scripts...")
                scripts = webData.find_all("script", src=True)
                for script in tqdm(scripts, desc="Scripts"):
                    src = script.get('src')
                    if src:
                        try:
                            script_url = urllib.parse.urljoin(url, src)
                            filename = src.split('/')[-1].split('?')[0]
                            if filename:
                                response = page.request.get(script_url)
                                if response.ok:
                                    with open(resources_path / filename, "wb") as f:
                                        f.write(response.body())
                        except Exception as e:
                            print(f"Error downloading script {src}: {e}")

                # Downloading fonts and other linked resources
                print("\n[*] Downloading fonts and other resources...")
                links = webData.find_all("link", href=True)
                for link in tqdm(links, desc="Other"):
                    rel = link.get('rel', [])
                    if 'icon' in rel or 'font' in str(rel).lower():
                        href = link.get('href')
                        if href:
                            try:
                                resource_url = urllib.parse.urljoin(url, href)
                                filename = href.split('/')[-1].split('?')[0]
                                if filename:
                                    response = page.request.get(resource_url)
                                    if response.ok:
                                        with open(resources_path / filename, "wb") as f:
                                            f.write(response.body())
                            except Exception as e:
                                print(f"Error downloading resource {href}: {e}")

                print(f"\n[+] Scraping complete! Resources saved to: {resources_path}")
                browser.close()



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