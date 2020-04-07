from flask import Flask, url_for, render_template, redirect, request, session, abort
import hashlib
import crawler
from multiprocessing.pool import ThreadPool
import threading
import os

app = Flask(__name__)
with open("secret.txt", "r") as secret:
    app.secret_key = secret.read()
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

@app.route("/videodownload")
def videodownload():
    if "USERID" not in session:
        return redirect(url_for("index"))
    else:
        return render_template("videodownload.html")

@app.route("/videoworker", methods=["POST"])
def videoworker():
    global linkList
    if request.method == "POST":
        linkValue = request.data.decode()
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
        return "Dont found this video"
    else:
        return f"{linkList[0][0]}-|||{linkList[0][1]}|||{linkList[0][2]}"

@app.route("/logout", methods=["GET"])
def logout():
    session.pop("USERID")
    return redirect(url_for("index"))

def appCrawlerVersion(linkValue):
    global linkList
    response = crawler.getPrincipalLinkVideo(linkValue)
    linkList.append(response)
    return True


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
