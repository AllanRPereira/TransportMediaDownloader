from flask import Flask, url_for, render_template, redirect, request, session, abort, send_file
from flask_cors import cross_origin
import hashlib
import crawler
import requests
from multiprocessing import Process, Queue, Manager
from multiprocessing.queues import Empty
import threading
import os
import time
from videoplayer.player_3 import sendDownloadFilesToClient



app = Flask(__name__)
with open("secret.txt", "r") as secret:
    app.secret_key = secret.read()

queueManager = Queue()
linkList = []
manager = Manager()
lastestResponse = manager.list()

@app.route("/")
def index():
    if "USERID" not in session:
        return render_template("login.html")
    else:
        return redirect(url_for("videodownload"))

@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].replace(" ", "")
        password = request.form["password"]
        with open("user.txt", "r") as user:
            data = user.read().split('\n')
            user, key_pass = data[0].replace(" ", ""), data[1]
            
        if username == user and password == key_pass:
            session["USERID"] = hashlib.md5(bytes(username + password, "utf-8")).hexdigest()
        else:
            redirect(url_for("index"))
        return redirect(url_for("videodownload"))

@app.route("/corslivestream/<path:url>")
@cross_origin()
def corslivestream(url):
    if url.find("livestream") == -1:
        return "Not allowed"
    else:
        contentPackage = requests.get(url).content
        return contentPackage

@app.route("/getscreen")
def screenshot():
    for file in os.listdir():
        if file == "statusAfterCleaning.png":
            return send_file("statusAfterCleaning.png", mimetype="image/png", as_attachment=True, attachment_filename="screenshot.png")
    return "não existe"

@app.route("/videodownload")
def videodownload():
    if "USERID" not in session:
        return redirect(url_for("index"))
    else:
        return render_template("videodownload.html")

@app.route("/videoworker", methods=["POST"])
def videoworker():
    global lastestResponse
    if request.method == "POST":
        linkValue, partNumber = request.data.decode().split(",")
        threadRequestLink = Process(target=appCrawlerVersion, args=(linkValue, int(partNumber), lastestResponse))
        threadRequestLink.start()
        return "Request Succefful! Wait a moment!"
    else:
        abort(404)

@app.route("/getlink", methods=["POST"])
def getLink():
    global linkList
    valueInQueue = queueResponse("linkList")
    if valueInQueue != False:
        linkList.append(valueInQueue)

    if linkList == []:
        contentResponse = "Not Ready"
    elif linkList[0][1] == False:
        contentResponse = "Don't found this video"
    elif linkList[0] == "vimeo-waiting":
        contentResponse = "vimeo-15-downloading"
    else:
        contentResponse = f"{linkList[0][0]}-|||{linkList[0][1]}|||{linkList[0][2]}"
    linkList = []
    return contentResponse

@app.route("/getfilevimeo", methods=["POST"])
def getFileVimeo():
    valueInQueue = queueResponse("vimeoParts")
    if valueInQueue != False:
        vimeoParts = valueInQueue
        if vimeoParts == False:
            return "Error"
        else:
            nameFile = vimeoParts[0]
            outputFile = vimeoParts[1]
            return send_file(f"videoplayer/{outputFile}", mimetype="video/mp4", attachment_filename=f"{nameFile}.mp4", as_attachment=True)
    else:
        return "Download ainda não disponível"
def queueResponse(requestType):
    global queueManager
    try:
        responseCrawlerMode = queueManager.get(timeout=2)
        if responseCrawlerMode[0] == requestType:
            print(f"[QUEUE] {responseCrawlerMode[1]} REQUEST: {requestType}")
            return responseCrawlerMode[1]
    except Empty as error:
        print("[QUEUE] Pilha Vazia")
    return False

@app.route("/confirmvdownload", methods=["POST"])
def confirmvdownload():
    global queueManager
    global lastestResponse
    bodyValue = request.data.decode()
    if bodyValue == "completed":
        cleanLastestResponse()
        return "Success"
    else:
        partDownloadNow = int(bodyValue.split("&")[1])
        instanceSendFiles = Process(target=sendDownloadFilesToClient, args=(queueManager, lastestResponse[0], partDownloadNow))
        instanceSendFiles.start()
        print("[CONFIRM] Parte Confirmada, nova parte adicionada a pilha")
        return "New Part Adicionada"

@app.route("/logout", methods=["GET"])
def logout():
    session.pop("USERID")
    return redirect(url_for("index"))

def cleanLastestResponse():
    global lastestResponse
    lastestResponse = manager.list()
    return True

def appCrawlerVersion(linkValue, partNumber, lastestResponse):
    global queueManager
    response = crawler.getPrincipalLinkVideo(linkValue)
    if response == False:
        queueManager.put(("linkList", (False, False)))
        return False
    if response[1] == "vimeo":
        queueManager.put(("linkList", "vimeo-waiting"))
        lastestResponse.append(response)

        partDownloadNow = 1 if partNumber == 0 else partNumber
        instanceSendFiles = Process(target=sendDownloadFilesToClient, args=(queueManager, response, partDownloadNow))
        instanceSendFiles.start()
        print("[CRAWLER] Instância adiciona à pilha")
        return True
        
    else:
        queueManager.put(("linkList", response))
    return True


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
