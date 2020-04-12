#Code Sequence to Enter in this player
import requests
import hashlib
import json
import time
import ast
import sh

def playerThree(chrome, proxyInstance):
    harFile = proxyInstance.har
    #with open('opening.har', 'r') as opening:
     #   harFile = ast.literal_eval(opening.read())
    return getVideoFormat(harDict=harFile)

def getVideoFormat(harDict):
    codec = ""
    request = harDict["log"]["entries"]
    for harRow in request:
        urlGet = harRow['request']['url']
        if urlGet.find("master.json") != -1:
            baseUrl = "/".join(urlGet.replace("https://", "").split("/")[::-1][3:][::-1])
            getContent = json.loads(requests.get(urlGet).content)
            for videoFormats in getContent['video']:
                if videoFormats['width'] == 640:
                    baseUrlVideo = "https://" + baseUrl + "/video/" + videoFormats['base_url']
                    numberOfSegment = len(videoFormats['segments'])
            for audioFormats in getContent['audio']:
                if audioFormats['bitrate'] == 128000:
                    baseUrlAudio = "https://" + baseUrl + "/" + "/".join(audioFormats['base_url'].split("/")[1:])
            return ('vimeo', baseUrlVideo, baseUrlAudio, numberOfSegment)
    return False

def downloadVideo(videoUrl, audioUrl, numberOfSegment=[]):
    #numberOfSegment -> 0 = Segmento Inicial, 1 -> Segmento Final

    with open(f"video_{hashlib.md5(videoUrl).hexdigest()}.mp4", "wb") as video:
        # Header 0 to MP4
        segment_zero = requests.get(f"{videoUrl}segment-0.mp4").content
        video.write(segment_zero)

        for segment in range(numberOfSegment[0], numberOfSegment[1]):
            segment_download = requests.get(f"{videoUrl}segment-{segment}.mp4").content
            video.write(segment_download)
    
    with open(f"audio_{hashlib.md5(audioUrl).hexdigest()}.mp4", "wb") as audio:
        # Header 0 to MP4
        segment_zero = requests.get(f"{audioUrl}segment-0.mp4").content
        audio.write(segment_zero)

        for segment in range(numberOfSegment[0], numberOfSegment[1]):
            segment_download = requests.get(f"{audioUrl}segment-{segment}.mp4").content
            audio.write(segment_download)
    
    return True

def joinFiles():
    return sh.ffmpeg(["-i", "video.mp4", "-i", "audio.mp4", "-c", "copy", "complete.mp4"])


if __name__ == "__main__":
    print(playerThree(False, False))