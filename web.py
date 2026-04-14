import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)

from flask import Flask, render_template, request
from datetime import datetime
import random

app = Flask(__name__)

@app.route("/")
def index():
    link = "<h1>歡迎進入楊硯涵的網站首頁</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>今天日期</a><hr>"
    link += "<a href=/about>關於硯哈</a><hr>"
    link += "<a href=/welcome?u=硯哈&dep=靜宜資管>歡迎光臨</a><hr>"
    link += "<a href=/account>帳號密碼</a><hr>"
    link += "<a href=/math>數學運算</a><hr>"
    link += "<a href=/cup>擲茭</a><hr>"
    link += "<a href=/read>讀取Firestore資料(根據lab遞減排序,取前4</a><hr>"
    link += "<a href=/search>查詢老師及其研究室</a><hr>"


    return link

@app.route("/read")
def read():
    Temp = ""
    db = firestore.client()

    collection_ref = db.collection("靜宜資管2026a")    
    docs = collection_ref.order_by("lab", direction=firestore.Query.DESCENDING).limit(4).get()   
    for doc in docs:         
        Temp += str(doc.to_dict()) + "<br>"     

    return Temp

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>回到網站首頁</a>"

@app.route("/today")
def today():
    now = datetime.now() #取得年份
    year = str(now.year) #取得月份
    month = str(now.month) #取得日期
    day = str(now.day)
    now = year + "年" + month + "月" + day + "日"
    return render_template("today.html", datetime = str(now))

@app.route("/about")
def about():
    return render_template("mis2a.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    x = request.values.get("u")
    y = request.values.get("dep")
    return render_template("welcome.html", name = x, dep = y)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/math")
def math():
    return render_template("math.html")

@app.route('/cup', methods=["GET"])
def cup():
    # 檢查網址是否有 ?action=toss
    #action = request.args.get('action')
    action = request.values.get("action")
    result = None
    
    if action == 'toss':
        # 0 代表陽面，1 代表陰面
        x1 = random.randint(0, 1)
        x2 = random.randint(0, 1)
        
        # 判斷結果文字
        if x1 != x2:
            msg = "聖筊：表示神明允許、同意，或行事會順利。"
        elif x1 == 0:
            msg = "笑筊：表示神明一笑、不解，或者考慮中，行事狀況不明。"
        else:
            msg = "陰筊：表示神明否定、憤怒，或者不宜行事。"
            
        result = {
            "cup1": "/static/" + str(x1) + ".jpg",
            "cup2": "/static/" + str(x2) + ".jpg",
            "message": msg
        }
        
    return render_template('cup.html', result=result)

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        # 這裡對應你圖片中的 keyword = input(...)
        keyword = request.form.get("teacher_keyword")
        db = firestore.client()
        
        # 對應你圖片中的 collection_ref 與 get()
        collection_ref = db.collection("靜宜資管2026a")
        docs = collection_ref.get()
        
        results = []
        for doc in docs:
            user = doc.to_dict()
            # 這裡就是你圖片第 16 行的判斷邏輯
            if keyword in user.get("name", ""):
                results.append(user)
        
        # 將結果傳送到結果頁面，不再是 print 到終端機
        return render_template("search_results.html", results=results, keyword=keyword)
    
    # 如果是直接點網址 (GET)，就顯示搜尋輸入框
    return render_template("search.html")


if __name__ == "__main__":
    app.run(debug=True)
