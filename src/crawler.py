from selenium import webdriver
from browsermobproxy import Server
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from videoplayer.player_1 import playerOne
from videoplayer.player_2 import playerTwo
from videoplayer.player_3 import playerThree

import os
import time
import requests
import ast

def getPrincipalLinkVideo(url, recursion=False):
    videoLinks = ["vzaar", "livestream", "vimeo"]

    
    if not os.path.isdir("videoplayer/video") or not os.path.isdir("videoplayer/audio"):
        os.mkdir("videoplayer/video")
        os.mkdir("videoplayer/audio")

    players = [playerOne, playerTwo, playerThree]
    with open("actions.txt") as actions:
        #Mudar para json
        link, username, password = actions.read().split("\n")

    serverPort = {"port" : int(os.environ.get("PROXY", 3030))}
    serverNav = Server("browsermob/bmp/bin/browsermob-proxy", options=serverPort)
    serverNav.start()
    proxyServer = serverNav.create_proxy()

    chromeBinary = os.environ.get("GOOGLE_CHROME_BIN")
    chromeProfile = webdriver.ChromeOptions()
    chromeProfile.binary_location = chromeBinary
    chromeProfile.add_argument("--allow-running-insecure-content")
    chromeProfile.add_argument("--ignore-certificate-errors")
    chromeProfile.add_argument(f"--proxy-server={proxyServer.proxy}")
    chromeProfile.add_argument("--headless")
    chromeProfile.add_argument("--no-sandbox")
    chromeProfile.add_argument("--disable-gpu")
    chromeProfile.add_argument("--remote-debbung-port=9222")
    print("[CRAWLER] Inicializando Chrome")
    chrome = initLogin(chromeProfile, username, password, link)
    if chrome == False:
        serverNav.stop()
        return False
    proxyServer.new_har("video")
    chrome.get(url)
    print("[CRAWLER] Aguardando Frame")
    time.sleep(20)
    chrome.get_screenshot_as_file("statusAfterCleaning.png")
    print("[CRAWLER] Limpando Tela")
    try:
        cleanScreen(chrome)
    except Exception as error:
        print(error)
        serverNav.stop()
        chrome.quit()
        return False
    time.sleep(2)
    tries = 0
    print("[CRAWLER] Encontrando Vídeo")
    while tries <= 1:
        try:
            print(f"[CRAWLER] Url Atual:{chrome.current_url}")
            wait = WebDriverWait(chrome, 15).until(EC.element_to_be_clickable((By.TAG_NAME, "iframe")))
            break
        except:
            chrome.refresh()
            time.sleep(10)
            cleanScreen(chrome)
            tries += 1
    if tries >= 2:
        chrome.quit()
        serverNav.stop()
        return False
    part = chrome.find_element_by_id("childrenWrapper")
    frame = chrome.find_elements_by_tag_name("iframe")[0]
    title = part.find_elements_by_tag_name("h1")[0].text
    print(f"[CRAWLER] Título:{title}")
    print("[CRAWLER] Frame encontrado")
    src = frame.get_property("src")
    videoTypeIndex = [index for index, videoName in enumerate(videoLinks) if videoName in src][0]
    functionVideo = players[videoTypeIndex]
    print("[CRAWLER] Aguardando carregamento dos pacotes")
    time.sleep(8)
    print(f"[CRAWLER] Passando para a função {videoLinks[videoTypeIndex]}")
    result = functionVideo(chrome, proxyServer)
    printResult = False if result == False else "All right"
    print(f"[CRAWLER] Retornado: {printResult}")
    chrome.quit()
    serverNav.stop()
    return (title,) + result

def initLogin(chromeProfile, username, password, link):
    try:
        chrome = webdriver.Chrome(chrome_options=chromeProfile)
    except:
        print("[CRAWLER] Erro na abertura do Chrome")
        return False
    chrome.get(link)
    try:
        wait = WebDriverWait(chrome, 30).until(EC.presence_of_element_located((By.ID, "email")))
    except:
        chrome.quit()
        return False
    time.sleep(3)
    print(f"[CRAWLER] Login URL: {chrome.current_url}")
    inputUser = chrome.find_element_by_id("email")
    inputUser.send_keys(username)
    inputPass = chrome.find_element_by_id("password")
    inputPass.send_keys(password)
    time.sleep(2)
    inputPass.submit()
    print(f"[CRAWLER] Loopback")
    while True:
        if chrome.current_url != link:
            time.sleep(5)
            break
        else:
            time.sleep(2)
    print("[CRAWLER] Login Realizado!")
    return chrome

def cleanScreen(chrome):
    part = chrome.find_element_by_id("childrenWrapper")
    while True:
        partVideo = part.find_element_by_tag_name("div")
        if partVideo.get_attribute("id") != "WatchScreenContainer":
            print("[CRAWLER] Há um bloqueio na tela! Aguardando remoção")
            className = partVideo.get_attribute("class")
            chrome.execute_script(f"document.getElementsByClassName(\"{className}\")[0].parentNode.removeChild(document.getElementsByClassName(\"{className}\")[0])")
            time.sleep(2)
        else:
            break
    return True

if __name__ == "__main__":
    link = input("Digite um link:")
    result = getPrincipalLinkVideo(link)
    with open("resultado.txt", "w") as resultt:
        resultt.write(str(result))