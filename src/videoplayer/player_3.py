#Code Sequence to Enter in this player
import requests
import hashlib
import json
import time
import ast
import sh
import os
from io import StringIO

lastestResponse = []

def playerThree(chrome, proxyInstance):
    ok = False
    while True:
        harFile = proxyInstance.har
        for row in harFile['log']['entries']:
            if row['request']['url'].find("master.json") != -1:
                print("[PLAYER3] Master Encontrado!")
                ok = True
        if ok:
            break
        else:
            print("[PLAYER3] Aguardando Json")
            chrome.find_element_by_tag_name("iframe").click()
            time.sleep(3)
    
    harFile = proxyInstance.har
    return getVideoFormat(harDict=harFile)

def getVideoFormat(harDict):
    codec = ""
    request = harDict["log"]["entries"]
    for harRow in request:
        urlGet = harRow['request']['url']
        if urlGet.find("master.json") != -1:
            baseUrl = "/".join(urlGet.replace("https://", "").split("/")[::-1][3:][::-1])
            content = requests.get(urlGet).content.decode()
            getContent = ast.literal_eval(requests.get(urlGet).content.decode())
            for videoFormats in getContent['video']:
                if videoFormats['width'] == 640:
                    baseUrlVideo = "https://" + baseUrl + "/video/" + videoFormats['base_url']
                    numberOfSegment = len(videoFormats['segments'])
            for audioFormats in getContent['audio']:
                if audioFormats['bitrate'] == 128000:
                    baseUrlAudio = "https://" + baseUrl + "/" + "/".join(audioFormats['base_url'].split("/")[1:])
            return ('vimeo', baseUrlVideo, baseUrlAudio, numberOfSegment)
    return False

def cleanVideosAudio(directory):
    listFiles = os.listdir(directory)
    listMP4 = [file for file in listFiles if file.find(".mp4") != -1]
    for mp4 in listMP4:
        os.remove(f"{directory}/{mp4}")
    return True

def downloadVideo(videoUrl, audioUrl, numberOfSegment, partNumber):
    #numberOfSegment -> 0 = Segmento Inicial, 1 -> Segmento Final
    multipleParts = False
    numberVideoPerPart = numberOfSegment // 3 + 1

    #Remove complete files
    cleanVideosAudio("videoplayer")
    cleanVideosAudio("videoplayer/video")
    cleanVideosAudio("videoplayer/audio")
    
    partDownload = partNumber

    init = 1 + (partDownload - 1) * numberVideoPerPart if partDownload == 1 else (partDownload - 1) * numberVideoPerPart
    end = partDownload * numberVideoPerPart
    videoName = f"video_{hashlib.md5(bytes(videoUrl, 'utf-8')).hexdigest()}_part_{partDownload}.mp4"
    with open(f"videoplayer/video/{videoName}", "wb") as video:
        # Header 0 to MP4
        segment_zero = requests.get(f"{videoUrl}segment-0.mp4").content
        video.write(segment_zero)
        
        for segment in range(init, end):
            request = requests.get(f"{videoUrl}segment-{segment}.m4s")
            if request.status_code == 404:
                break
            segment_download = request.content
            video.write(segment_download)
    print("[DOWNLOADER] Video Download")
    audioName = f"audio{hashlib.md5(bytes(audioUrl, 'utf-8')).hexdigest()}_part_{partDownload}.mp4"
    with open(f"videoplayer/audio/{audioName}", "wb") as audio:
        # Header 0 to MP4
        segment_zero = requests.get(f"{audioUrl}segment-0.mp4").content
        audio.write(segment_zero)
        
        for segment in range(init, end):
            request = requests.get(f"{audioUrl}segment-{segment}.m4s")
            if request.status_code == 404:
                return (videoName, audioName, "Finish 404", partDownload)
            segment_download = request.content
            audio.write(segment_download)
    print("[DOWNLOADER] Audio Download")
    if multipleParts:
        partDownload += 1
        if partDownload == 4:
            return (videoName, audioName, "Finish Video Download", partDownload - 1)
        return (videoName, audioName, "Other Part Download", partDownload - 1)
    
    return (videoName, audioName, "Part Download", partDownload)

def joinFiles(videoName, audioName, partNumber):
    buffError = StringIO()
    nameOutput = f"complete_{hashlib.md5(bytes(f'{videoName}{audioName}', 'utf-8')).hexdigest()}_part_{partNumber}.mp4"
    sh.ffmpeg(["-i", f"videoplayer/video/{videoName}", "-i", f"videoplayer/audio/{audioName}", "-c", "copy", f"videoplayer/{nameOutput}"], _err_to_out=buffError)
    print("[JOINFILES] Video e Audio Mesclados!")
    if buffError.getvalue() != "":
        print("[JOINFILES] Error encontrado!")
        return (False)
    else:
        sh.rm([f"videoplayer/audio/{audioName}", f"videoplayer/video/{videoName}"])
        print("[JOINFILES] Video e Audio removidos!")
        return (nameOutput)


def sendDownloadFilesToClient(queueManager, response, partNumber):

    videoUrl, audioUrl, numberOfSegment = response[2:]    
    print(f"[GETVIDEOS] Baixando Parte {partNumber}")
    try:
        resultDownload = downloadVideo(videoUrl, audioUrl, numberOfSegment, partNumber)
        videoFileName, audioFileName, statusDownload, partWrite = resultDownload
        outputFile = joinFiles(videoFileName, audioFileName, partWrite)
        nameLastFile = outputFile
        queueManager.put(("vimeoParts",(f"{response[0]}-part-{partNumber}", outputFile)))
        if statusDownload == "Finish 404" or statusDownload == "Finish Video Download":
            print(f"[MAIN] Finalizando com: {statusDownload}")
    except Exception as error:
        print(error)
        queueManager.put(("vimeoParts", (False, )))
        return False

if __name__ == "__main__":
    os.chdir("videoplayer")
    results = playerThree(False, False)
    for n in range(3):
        downloadVideo(results[1], results[2], results[3], 0)
        joinFiles(results[1], results[2], n + 1)