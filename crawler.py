from selenium import webdriver
from browsermobproxy import Server
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import requests
import ast

def getPrincipalLinkVideo(url):
    #Colocar certificado no firefox!!!!!!!
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
    chrome.get("https://beta.proenem.com.br")
    wait = WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.ID, "email")))

    inputUser = chrome.find_element_by_id("email")
    inputUser.send_keys("meusestudos.gb@gmail.com")
    inputPass = chrome.find_element_by_id("password")
    inputPass.send_keys("Oportunidadea")
    time.sleep(2)
    inputPass.submit()
    print("[CRAWLER] Login Realizado!")
    proxyServer.new_har("video")

    wait = WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "bcwNtx")))

    chrome.get(url)

    try:
        wait = WebDriverWait(chrome, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        wait = WebDriverWait(chrome, 20).until(
            EC.element_to_be_clickable((By.TAG_NAME, "iframe"))
        )
    except:
        return False

    divTitle = chrome.find_element_by_id("WatchScreenContainer")
    title = divTitle.find_element_by_tag_name("h1").text
    wait = WebDriverWait(chrome, 20).until(EC.element_to_be_clickable((By.TAG_NAME, "iframe")))
    print("[CRAWLER] Obtendo Vídeo!")
    time.sleep(10)
    har = proxyServer.har.copy()
    serverNav.stop()
    chrome.quit()
    print("[CRAWLER] Tratando HAR")
    response = getVideoFormat(har)
    print(f"[CRAWLER] Response:{response} Title:{title}")
    return (response, title)
    
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
    link = "https://beta.proenem.com.br/app/plano-de-estudos/semana-4/09-03-2020/ao-vivo/21888"
    result = getPrincipalLinkVideo(link)
    with open("resultado.txt", "w") as resultt:
        resultt.write(str(result))