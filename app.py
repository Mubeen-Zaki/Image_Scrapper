from flask import Flask,request,render_template
from flask_cors import cross_origin
import requests
from bs4 import BeautifulSoup as bs
import pymongo
import os
import logging

logging.basicConfig(filename="./Image_Scrapper/img_scraper/logging.log",level=logging.INFO)

app = Flask(__name__)

@app.route("/")
def home():
        return render_template("index.html")

@app.route("/review",methods = ["POST"])
def search():
        if request.method == "POST":
                try:
                        img_dir = "./Image_Scrapper/img_scraper/images/"
                        if not os.path.exists(img_dir):
                                os.makedirs(img_dir)
                        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}
                        query = request.form["content"]
                        link = f"https://www.google.com/search?sca_esv=562262235&hl=en&sxsrf=AB5stBjdLylzTBl3dapakXJom9mb7YIXhQ:1693707102269&q={query}&tbm=isch&source=lnms&sa=X&ved=2ahUKEwjCpLzRro2BAxV-UGwGHagaC0IQ0pQJegQIDBAB&biw=1229&bih=591&dpr=1.56"
                        page_html = bs(requests.get(link).content,'html.parser')
                        image_boxes = page_html.find_all("img")
                        l = []
                        del image_boxes[0]
                        for i in image_boxes:
                                url = i["src"]
                                image_data = requests.get(url).content
                                my_dict = {"url":url,"image":image_data}
                                l.append(my_dict)
                                with open(os.path.join(img_dir,f"{query}_{image_boxes.index(i)}.jpg"),"wb") as f:
                                        f.write(image_data)
                        db_url = "mongodb+srv://user.name:user.password@cluster0.urxsqur.mongodb.net/?retryWrites=true&w=majority" # replace user.name & user.password with your name & password
                        connection = pymongo.MongoClient(db_url)
                        database = connection["Image_Scrapper"]
                        collection = database["Images_Data"]
                        collection.insert_many(l)
                        return render_template("index.html",result = "Images scrapped and saved on local system and database successfully!")
                except Exception as e:
                        logging.INFO(e)
                        return render_template("index.html",result = "Something Went Wrong! Check .log file")
        else:
                return render_template("index.html", result = "Enter query and submit!")

if __name__ == "__main__":
        app.run(host="0.0.0.0",port=8080)
