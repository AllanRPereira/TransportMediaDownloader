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

def getPrincipalLinkVideo(url):
    videoLinks = ["vzaar", "livestream", "vimeo"]
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
    chrome = webdriver.Chrome(chrome_options=chromeProfile)
    chrome.get(link)
    wait = WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.ID, "email")))
    time.sleep(7)
    inputUser = chrome.find_element_by_id("email")
    inputUser.send_keys(username)
    inputPass = chrome.find_element_by_id("password")
    inputPass.send_keys(password)
    time.sleep(2)
    inputPass.submit()
    time.sleep(3)

    print("[CRAWLER] Login Realizado!")
    proxyServer.new_har("video")
    chrome.get(url)
    print("[CRAWLER] Aguardando Frame")
    WebDriverWait(chrome, 20).until(EC.element_to_be_clickable((By.TAG_NAME, "iframe")))
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
    print(f"[CRAWLER] Retornado: {result}")
    chrome.quit()
    serverNav.stop()
    return (title,) + result
    
def getVideoFormat(harDict):
    codec = ""
    request = harDict["log"]["entries"]
    for harRow in request:
        urlGet = harRow['request']['url']
        if urlGet.find(".m3u8") != -1:
            getContent = requests.get(urlGet).content.decode()
            if getContent.find("#EXT-X-STREAM-INF") != -1:
                partsVideo = getContent.split("#EXT-X-STREAM-INF")
                part360 = [part for part in partsVideo if part.find("640x360") != -1][0]
                codec = part360.split("\n")[1].split(".m3u8")[0]
        elif urlGet.find(".ts") != -1 and codec != "":
            prefix = urlGet.split(".ts")[0].split("/")
            prefix[1] = "/"
            finish = prefix[:len(prefix) - 1][:]
            finish.append(codec)
            return "/".join(finish)
        else:
            pass
    return False

if __name__ == "__main__":
    link = input("Digite um link:")
    result = getPrincipalLinkVideo(link)
    with open("resultado.txt", "w") as resultt:
        resultt.write(str(result))
