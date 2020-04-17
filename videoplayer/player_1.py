from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json
import time
import ast

#Code Sequence to Enter in this player
def playerOne(chrome, proxyServer):
    har = proxyServer.har.copy()
    print("[PLAYER1] Iniciando Varredura")
    response = getVideoFormat(har)
    return response

def getVideoFormat(harDict):
    codec = ""
    request = harDict["log"]["entries"]
    responseReturn = ()
    for harRow in request:
        urlGet = harRow['request']['url']
        if urlGet.find(".m3u8") != -1 and len(responseReturn) <= 1:
            getContent = requests.get(urlGet).content.decode()
            resolutions = getContent.split("#EXT-X-STREAM-INF")[1:]
            for informationCodecs in resolutions:
                if informationCodecs.find("864x486") != -1 or informationCodecs.find("640x360") != -1:
                    urlForm1 = urlGet.split("https://")[1].split("/")
                    urlForm1 = "https://" + "/".join(urlForm1[:len(urlForm1)-1])
                    urlParts = urlForm1 + "/" + informationCodecs.split("\n")[1].split("?")[0]
                    namePrefix = urlParts.split("/")[::-1][0].split(".m3u8")[0]
            requestParts = requests.get(urlParts).content.decode()
            numberOfParts = max([int(urls.split(".")[0].split("-")[::-1][0]) for urls in requestParts.split("\n") if urls.find(".ts") != -1])
            linkDownload = urlParts.split(".m3u8")[0] + "-"
            return (linkDownload, numberOfParts)

    return False

if __name__ == "__main__":
    content = open("../teste", "r").read()
    harDict = ast.literal_eval(content)
    print(getVideoFormat(harDict))