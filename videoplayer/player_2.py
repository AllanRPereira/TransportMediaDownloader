from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json
import time

#Code Sequence to Enter in this player
def playerTwo(chrome, proxyInstance):
    proxyInstance.new_har("livestream")
    iframe = chrome.find_element_by_tag_name("iframe")
    chrome.switch_to_frame(iframe)
    button = chrome.find_element_by_class_name("watch_again_link")
    button.click()
    chrome.switch_to_default_content()
    time.sleep(10)
    chrome.get("https://www.google.com")
    har = proxyInstance.har.copy()
    with open("newharlive.txt", "w") as live:
        live.write(str(har))
    print("[PLAYER2] Iniciando Varredura")
    return getVideoFormat(har)

def getVideoFormat(harDict):
    codec = ""
    request = harDict["log"]["entries"]
    for harRow in request:
        '''
        #Modulo para HAR do Navegador!
        try:
            print(harRow['response']['content'].keys())
            jsonVideo = json.loads(harRow['response']['content']['text'])
        except:
            continue
        if jsonVideo == []:
            continue
        '''
        urlGet = harRow['request']['url']
        if urlGet.find(".m3u8") != -1:
            getContent = requests.get(urlGet).content.decode()
            resolutions = getContent.split("#EXT-X-STREAM-INF")[1:]
            for informationCodecs in resolutions:
                if informationCodecs.find("864x486") != -1 or informationCodecs.find("640x360") != -1:
                    urlParts = "https" + informationCodecs.split("https")[1].replace("\n", "")
            try:
                requestParts = requests.get(urlParts).content.decode()
            except:
                return False
            numberOfParts = max([int(urls.split(".")[0].split("-")[::-1][0]) for urls in requestParts.split("\n") if urls.find(".ts") != -1])
            linkDownload = urlParts.split(".m3u8")[0] + "-"
            return ("http://videogabidownload.herokuapp.com/corslivestream/" + linkDownload, numberOfParts)
    return False

if __name__ == "__main__":
    import ast
    file = open("../newharlive.txt", "r")
    string = file.read()
    dictionary = ast.literal_eval(string)
    file.close()
    print(getVideoFormat(dictionary))
