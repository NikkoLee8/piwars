import os
import redis
from flask import Flask, render_template, redirect, request, url_for, make_response
import boto
# import boto3
import setenv
import time
# import uuid
# import random
import requests
import json
import pymongo
from pymongo import MongoClient

r = redis.Redis(host=os.environ['redis_hostname'], port=os.environ['redis_port'], password=os.environ['redis_password'])
herobucket = os.environ['hero']
avatarbucket = os.environ['avatar']
planetbucket = os.environ['planet']
ecs_access_key = os.environ['ECS_access_key'] 
ecs_secret_key = os.environ['ECS_secret']
ecs_host = os.environ['ECS_host']
object_access_url = os.environ['object_access_URL']
app = Flask(__name__)
session = boto.connect_s3(ecs_access_key, ecs_secret_key, host=ecs_host)  
herob = session.get_bucket(herobucket)
avatarb = session.get_bucket(avatarbucket)
planetb = session.get_bucket(planetbucket)

if 'VCAP_SERVICES' in os.environ:
    VCAP_SERVICES = json.loads(os.environ['VCAP_SERVICES'])
    MONCRED = VCAP_SERVICES["mlab"][0]["credentials"]
    client = MongoClient(MONCRED["uri"])
    DB_NAME = str(MONCRED["uri"].split("/")[-1])
else:
    client = MongoClient('127.0.0.1:27017')
    DB_NAME = "starwars"

print "Connecting to database : " + DB_NAME
db = client[DB_NAME]
print db

begin_html = """<!DOCTYPE html>
                <html>
                <head>
                <style>
                body {
                      background-color: black; color:white;
                      }
                div.fixed {
                      position: fixed;
                      width: 100%;
                      bottom: 20px;
                      text-align:center;
                      line-height:4;
                      font-family: "Times New Roman", Times, serif;
                      }
                 </style>
                 </head>
                 <body>"""

end_html = "</pre></div></body></html>"
crawl_list = []

@app.route('/')
def mainmenu():
    global crawl_list

    print "\n## Let's sort them by a specific field, display only some fields"
    cursor = db.intro.find().sort("name", pymongo.ASCENDING)
    for c in cursor:
        print c['name']
        crawl_list.append(c['crawlline'])    
    response = """<a href="/crawl/1"><h3>Start</h3></a>"""

    return response

@app.route('/crawl/<str_i>/')
def crawl(str_i):
    global crawl_list

    int_i = int(str_i)
    mid_html =  """<div class="fixed"><pre>"""

    if int_i > len(crawl_list):
        mid_html += """<img src="{}/{}/piwars.jpg">""".format(object_access_url, avatarbucket)
        mid_html += """<audio controls autoplay>"""
        mid_html += """<source src="{}/{}/starwars.mp3" type="audio/mpeg"></audio>""".format(object_access_url, avatarbucket)
    else:
        rev_i = int(str_i)
        for j in range (int_i):
            rev_i -= 1
            fsize = 7 - rev_i
            if fsize < 0:
                fsize = 0
            mid_html += """<p><font size ={} color="yellow"> {}</font></p>""".format(str(fsize), crawl_list[j])
        ecs_crawl = "crawl" + str(int_i - 1).zfill(2)
        mid_html +="""<audio controls autoplay>
                  <source src="{}/{}/{}.mp3" type="audio/mpeg">
                 our browser does not support the audio element.
                 </audio>""".format(object_access_url, avatarbucket, ecs_crawl)
        inc_i = int_i + 1
        mid_html += """<a href="/crawl/{}"<p> <font color="yellow">.</p></a>""".format(str(inc_i))

    response = begin_html + mid_html + end_html
    print response
    return response

if __name__ == "__main__":
	app.run(debug=False,host='0.0.0.0', port=int(os.getenv('PORT', '5000')))
