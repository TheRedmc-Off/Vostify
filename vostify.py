# coding:utf-8

# Credits:

# Original software: ani-cli by pystardust: https://github.com/pystardust/ani-cli
# Fork of the original software: ani-cli by KrishenK0: https://github.com/KrishenK0/ani-cli
# This project was build with KrishenK0's ani-cli as a base, and adapted to run on windows.
# The name "Vostify" was chosen by me, and like i said earlier, i didn't create this program from scratch.
# Author: TheRedmc-Off

# Other informations:

# License: MIT License
# Version: 1.2
# Description: Script permitting to watch animes in VOSTFR (Using Mavanimes.cc)
# Usage: python vostify.py or run the compiled file

# Début du script

import click
import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
import time
import html
import tempfile
import shutil
import pkg_resources

# Initialisation

os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]
temp_dir = tempfile.mkdtemp()

base_url = 'http://mavanimes.cc'
headers = {"x-requested-with": "XMLHttpRequest"}

# Extraction des extensions

with open(os.path.join(temp_dir, 'ublock_origin.crx'), 'wb') as f:
    f.write(pkg_resources.resource_string(__name__, 'ublock_origin.crx'))
with open(os.path.join(temp_dir, 'redirect_blocker.crx'), 'wb') as f:
    f.write(pkg_resources.resource_string(__name__, 'redirect_blocker.crx'))

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKYELLOW = '\033[93m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    FAIT = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'

# Bannière

banner = f"""{bcolors.END}
 ___ ___               __   __   ___        
|   |   |.-----.-----.|  |_|__|.'  _|.--.--.
|   |   ||  _  |__ --||   _|  ||   _||  |  |
 \_____/ |_____|_____||____|__||__|  |___  |
                ---V1.2---           |_____|
"""

# Fonctions principales

def openAnime(anime_url, browser='firefox'):
    if browser == 'chrome':
        from selenium.webdriver import Chrome, ChromeOptions
        options = ChromeOptions()
        options.add_argument('log-level=3')  # Montre les logs importants
        options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Désactiver les avertissements webtools
        options.headless = True

        driver = Chrome(options=options)
    else:
        from selenium.webdriver import Firefox, FirefoxOptions
        options = FirefoxOptions()
        options.add_argument('log-level=3')  # Montrer les logs importants
        options.headless = True

        driver = Firefox(options=options)

    driver.get(base_url + anime_url)

    print(f"{bcolors.OKGREEN}[+] Recherche de l'url...{bcolors.END}")
    
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-robot'))).click()
    
    id = None
    iframes = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="iframe-container"]/iframe')))
    for iframe in iframes:
        url = re.search('^https?:\/\/.*d0000d\.com.*\/e\/(.*)$', iframe.get_attribute('src'))
        print(f"HTML Element: {url}")
        if url:
            id = url.group(1)
            print(f"URL: {url.group(0)}")
            print(f"ID: {id}")
            print(f"{bcolors.OKGREEN}[+] URL Trouvée{bcolors.END}")
            url_to_open = f"https://d0000d.com/e/{id}"
            chrome_options = Options()
            chrome_options.add_argument("--window-size=1920x1080")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--verbose')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--kiosk')
            chrome_options.add_extension(os.path.join(temp_dir, 'ublock_origin.crx'))
            chrome_options.add_extension(os.path.join(temp_dir, 'redirect_blocker.crx'))


            print(f"{bcolors.OKGREEN}[+] Chargement du stream...{bcolors.END}")
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            print(f"{bcolors.OKGREEN}[+] Chargement des extensions...{bcolors.END}")
            time.sleep(10)
            print(f"{bcolors.OKGREEN}[+] Ouverture de l'url...{bcolors.END}")
            driver.get(url_to_open)
            input(f"{bcolors.OKGREEN}[+] Appuyez sur la touche Entrée pour fermer le programme. \n{bcolors.END}")
            print(f"{bcolors.OKGREEN}[X] Fermeture du programme en cours, veuillez patienter...{bcolors.END}")
            shutil.rmtree(temp_dir)
            driver.quit()
            sys.exit()
        
    print(f"{bcolors.OKGREEN}[X] Closed{bcolors.END}")
    shutil.rmtree(temp_dir)
    driver.quit()
    sys.exit()


def reqAnimeList(anime):
    r = requests.get(base_url + '/tous-les-animes-en-vostfr')
    html_content = html.unescape(r.text) # Unescape le contenu HTML pour éviter les caractères spéciaux
    animeList = re.findall(f"^<a href=\"(.*)\">({''.join([f'(?:{i}).*' for i in anime.split(' ')])})</a>$", html_content, flags=re.I+re.M)
    if r.status_code != 200 or animeList == []:
        return False
    else:
        return animeList
    

def episode_exist(id, episodes):
    if id == 'l' or id == 'list':
        print(f"{bcolors.OKBLUE}Episodes: {', '.join(str(x['id']) for x in episodes[::-1])}{bcolors.END}")
        return False
    elif id.replace('.', '', 1).isdigit():
        id = int(id) if id.isdigit() else float(id)
        for episode in episodes:
            if episode['id'] == id:
                return episode['url']
    return False


def episode_list(anime):
    r = requests.get(base_url + anime)
    soup = BeautifulSoup(r.text, 'html.parser')
    tempEpisodes = list(map(lambda x: x.a.get('href'), soup.find_all('article', 'episode')))
    episodes = []
    count = {'i': 0, 'f': 0}
    for episode in tempEpisodes:
        regex = re.search(r'(-([0-9.]+-[0-9])-)vostfr|(-([0-9.]+)-)vostfr', episode)
        if regex.group(2) is not None:
            episodes.append({'id': float(regex.group(2).replace('-', '.')), 'url': episode})
            count['f'] += 1
        else:
            id = int(regex.group(4))
            episodes.append({'id': id, 'url': episode})
            if id > count['i']: count['i'] = id

    episodes.sort(key=lambda x: x['id'], reverse=True)

    print(f"{bcolors.HEADER + bcolors.BOLD}Veuillez choisir l'épisode (1-{count['i']} / {count['f']} filler)\n'list' ou 'l' pour les afficher{bcolors.END}")
    url = episode_exist(input(f'{bcolors.OKCYAN}>>> {bcolors.END}'), episodes)
    while url is False:
        url = episode_exist(input(f'{bcolors.OKCYAN}>>> {bcolors.END}'), episodes)

    return url


def anime_list(animes):
    print(f"{bcolors.HEADER + bcolors.BOLD}Veuillez choisir l'anime (>> 0){bcolors.END}")
    for i, anime in enumerate(animes):
        print(f"{bcolors.ITALIC}{bcolors.OKGREEN if i % 2 == 0 else bcolors.OKYELLOW} {i} - {anime[1]}{bcolors.END}")

    id = int(input(f'{bcolors.OKCYAN}>> {bcolors.END}'))
    while id < 0 or id > len(animes):
        id = int(input(f'{bcolors.OKCYAN}>> {bcolors.END}'))

    return (f'/{animes[id][0]}')


def menu():
    print(f"{bcolors.HEADER + bcolors.BOLD}Veuillez rentrer le titre de l'anime.{bcolors.END}")
    animes = reqAnimeList(input(f'{bcolors.OKCYAN}> {bcolors.END}'))
    while animes is False:
        print(f"{bcolors.HEADER}Anime introuvable, veuillez ressayer avec un autre titre.")
        animes = reqAnimeList(input(f'{bcolors.OKCYAN}> {bcolors.END}'))

    return animes

# Execution de tout le programme

@click.command()
def main():
    os.system('cls')
    print(banner)
    animes = menu()
    os.system('cls')
    print(banner)
    animeUrl = anime_list(animes)
    os.system('cls')
    print(banner)
    episodeUrl = episode_list(animeUrl)
    os.system('cls')
    print(banner)
    openAnime(episodeUrl)


if __name__ == '__main__':
    main()