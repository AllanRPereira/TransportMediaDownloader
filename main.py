from flask import Flask, url_for, render_template, redirect, request, session, abort
import hashlib
import crawler
from multiprocessing.pool import ThreadPool
import threading
import os

app = Flask(__name__)
app.secret_key = "eb84d7e1f89488a41c657d47f35489beea957aac9278f1baa25a68d446e4fb93"
linkList = []

@app.route("/")
def index():
    if "USERID" not in session:
        return render_template("login.html")
    else:
        return redirect(url_for("videodownload"))

@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "gabriela melo" and password == "nosceitipsum":
            session["USERID"] = hashlib.md5(bytes(username + password, "utf-8")).hexdigest()
        else:
            redirect(url_for("index"))
        return redirect(url_for("videodownload"))

@app.route("/videodownload")
def videodownload():
    if "USERID" not in session:
        return redirect(url_for("index"))
    else:
        return render_template("videodownload.html")

@app.route("/videoworker", methods=["POST"])
def videoworker():
    
    if request.method == "POST":
        linkValue = request.data.decode()
        if linkValue == "teste":
            return "Top"
        else:
            requestLink = ThreadPool(processes=1)
            threadInstance = requestLink.apply_async(appCrawlerVersion, (linkValue, ))
            return "Request Succefful! Wait a moment!"
    else:
        abort(404)

@app.route("/getlink", methods=["POST"])
def getLink():
    global linkList
    if linkList == []:
        return "Not Ready"
    elif linkList[0] == False:
        return "Don't found this video"
    else:
        return f"{linkList[0][0]}-|||{linkList[0][1]}"

def appCrawlerVersion(linkValue):
    global linkList
    response = crawler.getPrincipalLinkVideo(linkValue)
    linkList.append(response)
    return True


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
