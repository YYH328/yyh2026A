import requests
from bs4 import BeautifulSoup

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
    link += "<a href=/sp1>爬取課程</a><hr>"
    link += "<a href=/movie1>即將上映的電影</a><hr>"
    link += "<a href=/movie2>讀取開眼電影即將上映影片，寫入Firestore</a><hr>"
    link += "<a href=/movie3>查詢相關電影資訊</a><hr>"
    link += "<a href=/road>台中市十大肇事路口</a><hr>"
    link += "<a href=/weather>天氣預報查詢</a><hr>"

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

@app.route("/sp1")
def sp1():
    R = ""
    url = "https://yyh2026-a.vercel.app/about"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    #print(Data.text)
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select("td a")

    for item in result:
        R += item.text + "<br>" + item.get("href") + "<br><br>"
    return R


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

@app.route("/movie1")
def movie1():
    url = "https://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    
    # 根據你圖片中的選取器邏輯
    result = sp.select(".filmListAllX li")
    
    R = "<h1>即將上映電影清單</h1>"
    R += "<a href='/'>回到首頁</a><br><hr>"
    
    for item in result:
        try:
            # 抓取電影名稱 (從 img 的 alt 屬性)
            name = item.find("img").get("alt")
            # 抓取連結 (補上完整網址)
            link = "https://www.atmovies.com.tw" + item.find("a").get("href")
            
            # 組合 HTML 字串
            R += f"🎬 <b>{name}</b><br>"
            R += f"🔗 <a href='{link}' target='_blank'>電影介紹連結</a><br><br>"
        except:
            # 防止部分 li 結構不完整導致報錯
            continue
            
    return R

@app.route("/movie2")
def movie2():
  url = "http://www.atmovies.com.tw/movie/next/"
  Data = requests.get(url)
  Data.encoding = "utf-8"
  sp = BeautifulSoup(Data.text, "html.parser")
  result=sp.select(".filmListAllX li")
  lastUpdate = sp.find("div", class_="smaller09").text[5:]

  for item in result:
    picture = item.find("img").get("src").replace(" ", "")
    title = item.find("div", class_="filmtitle").text
    movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
    hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
    show = item.find("div", class_="runtime").text.replace("上映日期：", "")
    show = show.replace("片長：", "")
    show = show.replace("分", "")
    showDate = show[0:10]
    showLength = show[13:]

    doc = {
        "title": title,
        "picture": picture,
        "hyperlink": hyperlink,
        "showDate": showDate,
        "showLength": showLength,
        "lastUpdate": lastUpdate
      }

    db = firestore.client()
    doc_ref = db.collection("電影").document(movie_id)
    doc_ref.set(doc)    
  return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 

@app.route("/movie3", methods=["GET", "POST"])
def movie3():
    if request.method == "POST":
        keyword = request.form.get("keyword")
        db = firestore.client()
        
        # 1. 取得 movies 集合中的所有文件 (請確認你的集合名稱是 movies)
        movies_ref = db.collection("電影").stream()
        
        movie_list = []
        for doc in movies_ref:
            movie_data = doc.to_dict()
            # 2. 檢查關鍵字是否在標題內 (不分大小寫)
            if keyword.lower() in movie_data.get("title", "").lower():
                movie_list.append(movie_data)
        
        return render_template("movie3.html", movies=movie_list, keyword=keyword)
    
    return render_template("movie3.html", movies=None)

@app.route("/road")
def road():
    R = ""
    url = " https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=a1b899c0-511f-4e3d-b22b-814982a97e41"
    Data = requests.get(url)
    #print(Data.text)

    JsonData = json.loads(Data.text)
    for item in JsonData:
        R += item["路口名稱"] + ",總共發生" + item["總件數"] + "件事故<br>"
    return R + "<a href='/'>回到首頁</a><br><hr>"

@app.route("/weather", methods=["GET", "POST"])
def weather():
    if request.method == "POST":
        # 取得表單輸入的城市名稱
        city = request.form.get("city")
    else:
        # 如果是 GET 請求，預設顯示「臺中市」
        city = request.args.get("city", "臺中市")
    
    # 處理台/臺字體轉換（如截圖第 4 行）
    city = city.replace("台", "臺")
    
    # 氣象局 API 設定（參考截圖第 5-6 行）
    token = "rdec-key-123-45678-011121314"
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={token}&format=JSON&locationName={city}"
    
    try:
        Data = requests.get(url)
        Data.encoding = "utf-8"
        json_data = json.loads(Data.text)
        
        # 檢查是否有抓到該城市的資料
        if not json_data["records"]["location"]:
            return f"找不到 '{city}' 的氣象資料，請檢查縣市名稱是否正確。<br><a href='/weather'>重新查詢</a>"

        # 解析資料（參考截圖第 11, 14, 15 行）
        WeatherTitle = json_data["records"]["datasetDescription"]
        location_data = json_data["records"]["location"][0]
        
        # 天氣現象 (Wx)
        Weather = location_data["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
        # 降雨機率 (PoP)
        Rain = location_data["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
        
        # 建立簡單的 HTML 表單供使用者輸入
        html_form = f"""
            <form method="POST" action="/weather">
                請輸入縣市名稱：<input type="text" name="city" value="{city}">
                <input type="submit" value="查詢">
            </form>
            <hr>
            <h2>{city} - {WeatherTitle}</h2>
            <p>目前預報：{Weather}</p>
            <p>降雨機率：{Rain}%</p>
            <a href="/">回到首頁</a>
        """
        return html_form
        
    except Exception as e:
        return f"查詢失敗，錯誤訊息：{str(e)}<br><a href='/weather'>返回查詢</a>"


if __name__ == "__main__":
    app.run(debug=True)
