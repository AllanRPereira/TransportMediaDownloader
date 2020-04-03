from selenium import webdriver
from browsermobproxy import Server
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

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

    firefoxProfile = webdriver.FirefoxProfile()
    firefoxProfile.set_proxy(proxyServer.selenium_proxy())
    firefoxProfile.accept_untrusted_certs = True
    firefoxProfile.assume_untrusted_cert_issuer = False
    firefoxOptions = Options()
    firefoxOptions.headless = True
    firefox = webdriver.Firefox(options=firefoxOptions, firefox_profile=firefoxProfile)
    firefox.get("https://beta.proenem.com.br")
    wait = WebDriverWait(firefox, 20).until(EC.presence_of_element_located((By.ID, "email")))

    inputUser = firefox.find_element_by_id("email")
    inputUser.send_keys("meusestudos.gb@gmail.com")
    inputPass = firefox.find_element_by_id("password")
    inputPass.send_keys("Oportunidadea")
    time.sleep(5)
    inputPass.submit()
    proxyServer.new_har("video")

    wait = WebDriverWait(firefox, 100).until(EC.presence_of_element_located((By.CLASS_NAME, "bcwNtx")))

    firefox.get(url)

    try:
        wait = WebDriverWait(firefox, 100).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        wait = WebDriverWait(firefox, 100).until(
            EC.element_to_be_clickable((By.TAG_NAME, "iframe"))
        )
    except:
        return False

    divTitle = firefox.find_element_by_id("WatchScreenContainer")
    title = divTitle.find_element_by_tag_name("h1").text
    firefox.find_element_by_tag_name("iframe").click()
    time.sleep(20)
    har = proxyServer.har.copy()
    serverNav.stop()
    firefox.quit()
    response = getVideoFormat(har)
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
