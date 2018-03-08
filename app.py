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

pidentity = ""
pimage = ""

#.modal-content {
#    margin: 5% auto 5% auto; /* 5% from the top, 5% from the bottom and centered */
#    border: 1px solid #888;
#    width: 80%; /* Could be more or less, depending on screen size *
#}


begin_html = """<!DOCTYPE html>
<html>
<head>
<style>
.center80 {
    margin: auto;
    width: 80%;
    border: 3px solid #73AD21;
    padding: 10px;
}


.one {
    border-style: solid;
    border-width: 5px;
}

header, footer {
    padding: 1em;
    color: white;
    background-color: black;
    clear: left;
    text-align: center;
}
header {background: black;color:white;}
footer {background: #aaa;color:white;}

</style>
</head>
<body>
"""

#<meta name="viewport" content="width=device-width, initial-scale=1">
#<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">

end_html = "</body></html>"

@app.route('/')
def mainpage():

    response = make_response(render_template('login.html'))
    return response

@app.route('/sulogin.html', methods=['POST'])
def sulogin():
    global pidentity
    global pimage
    
    uname = request.form['username']
    passwd = request.form['password']
    chc = request.form['choice']
    
    if chc == "login":
        pname = ""
        for p in r.keys ('hero*'):
            pname = r.hget(p,'username')
            ppasswd = r.hget(p,'password')
            pidentity = r.hget(p, 'identity')
            pimage = r.hget(p, 'image')
            if uname == pname:
                break
        if uname == pname:
            resp = start_game(pname)
        else:
             resp = """<a href="/register"><h3>Please register</h3></a>"""
    else:
        resp = register()
    return resp

@app.route('/start_game/<pname>')
def start_game(pname):

    mid_html = """ <header> <h1> Welcome {} <img src="{}/{}/{}" style="width:120px;height:100px;vertical-align:text-top"> to the PIED PIPER PORTAL
                   <img src="{}/{}/PiedPiper.jpg" align="right" style="width:120px;height:100px;vertical-align:text-top"></h1></header> """.format(pname, object_access_url, herobucket, pimage, object_access_url, avatarbucket)

    mid_html += """<div class = "center80">
		<h3> #Rebels #RebellionFighters</h3>
		<nav><ul>"""
    temp_html = ""
    for each_photo in herob.list():
        photo_split = each_photo.key.split('.')
        #Call hero and pass in username, the name of the photofile before the '.' and the key to the photo
        mid_html += """<a href="/hero/{}/{}/{}">""".format(pname, photo_split[0], each_photo.key)
#        mid_html += """<img src="{}/{}/{}" style="width:100px;height:80px;vertical-align:text-top"> </a><b>{}</b>""".format(object_access_url, herobucket, each_photo.key, photo_split[0])
        mid_html += """<img src="{}/{}/{}" style="width:100px;height:80px;vertical-align:text-top"> </a>""".format(object_access_url, herobucket, each_photo.key)
        temp_html += """<b><textarea style="font-weight: bold" rows="1" cols="12"> {} </textarea></b>""".format(photo_split[0])

    mid_html += "<br>" + temp_html + """</ul> </nav> </div> """
	
    mid_html += """<div class = "center80">
	        <h3> #Monitoredplanets </h3>
		<nav><ul>"""
    temp_html = ""
    for each_photo in planetb.list():
        photo_split = each_photo.key.split('.')
        #Call planet and pass in username, the name of the photofile before the '.' and the key to the photo
        mid_html += """<a href="/planet/{}/{}/{}">""".format(pname, photo_split[0], each_photo.key)
#        mid_html += """<img src="{}/{}/{}" style="width:100px;height:100px;vertical-align:text-top"> </a><b>{}</b>""".format(object_access_url, planetbucket, each_photo.key, photo_split[0])
        mid_html += """<img src="{}/{}/{}" style="width:100px;height:100px;vertical-align:text-top"> </a>""".format(object_access_url, planetbucket, each_photo.key)
        temp_html += """<b><textarea style="font-weight: bold" rows="1" cols="12"> {} </textarea></b>""".format(photo_split[0])

    mid_html += "<br>" + temp_html + """</ul> </nav> </div> """

    mid_html += """<footer>Copyright &copy; PiWars.com</footer> """
    response = begin_html + mid_html + end_html
    return response

@app.route('/hero/<pname>/<avatar>/<filename>')
def hero(pname,avatar, filename):
    global pidentity
    global pimage

    for h in r.keys ('hero*'):
        hname = r.hget(h,'username')
        hidentity = r.hget(h, 'identity')
        himage = r.hget(h, 'image')
        if hname == avatar:
            break

    pplres = requests.get(hidentity)
    people = json.loads(pplres.content)

    mid_html = """<div>
                <header> <h1> PIED PIPER PORTAL
                <img src="{}/{}/PiedPiper.jpg" align="right" style="width:120px;height:100px;vertical-align:text-top"></h1>
                         <h2> Information on {} </h2></header>""".format(object_access_url, avatarbucket, people['name'])
    mid_html += """</div> """   

    mid_html += """<div>"""
    mid_html += """<ul style="width:30%; float:left;">"""
    mid_html += """<img src="{}/{}/{}" style="width:240x;height:200px;vertical-align:text-top"> """.format(object_access_url, herobucket, filename)
    mid_html += """<br><li>Height : {} </li>""".format(people['height'])
    mid_html += """<li>Gender : {} </li>""".format(people['gender'])
    mid_html += """<li>Birth Year : {} </li></ul>""".format(people['birth_year'])
    hwres = requests.get(people['homeworld'])
    homeworld = json.loads(hwres.content)

    mid_html += """<ul style="width:30%; float:left;">"""
    mid_html += """<b> <font size = "5"> Homeworld :{} </font></b><br>""".format(homeworld['name'])
    if homeworld['name'] == "unknown":
        mid_html += "</ul>"
    else:
        for i in r.keys('planet*'):
            planetname = r.hget(i, 'planetname')
            if planetname == homeworld['name']:       
                planetfilename = r.hget(i, 'image')
                planetidentity = r.hget(i, 'identity')
                break
        mid_html += """<a href="/planet/{}/{}/{}">""".format(pname, planetname, planetfilename)
        mid_html += """<img src="{}/{}/{}" style="width:240x;height:200px;vertical-align:text-top"> </a></ul>""".format(object_access_url, planetbucket, planetfilename)

    mid_html += """<ul style="width:30%; float:left;">"""
    mid_html += """<b> <font size = "5"> Starships are : </font></b>"""
    for i in people['starships']:
        stshres = requests.get(i)
        starship = json.loads(stshres.content)
        mid_html += """<li> {} </li>""".format(starship['name'])
    mid_html += """</ul></div> """   
   
    mid_html += """<div> <br>
                <a href="/start_game/{}"> <b>RETURN TO MAIN SCREEN</b></a>
                <footer>Copyright &copy; PiWars.com</footer>
                </div>""".format(pname)
 
    response = begin_html + mid_html + end_html
    return response

        
@app.route('/planet/<pname>/<avatar>/<filename>')
def planet(pname, avatar, filename):

    mid_html = """<div>
                <header> <h1> PIED PIPER PORTAL
                <img src="{}/{}/PiedPiper.jpg" align="right" style="width:120px;height:100px;vertical-align:text-top"></h1>
                         <h2> Information on {} </h2></header>""".format(object_access_url, avatarbucket, avatar)
    mid_html += """</div> """   

    mid_html += """<div>"""
    mid_html += """<ul style="width:30%; float:left;">"""
    mid_html += """<img src="{}/{}/{}" style="width:240x;height:200px;vertical-align:text-top"> """.format(object_access_url, planetbucket, filename)

    if avatar == "Earth":
        mid_html +="""</div>"""
        mid_html += """<div>"""
        mid_html += """<ul style="width:30%; float:left;">"""
        mid_html += """<h3>#Monitoredcities</h3>"""
        mid_html += """<br><li><a href="/city/{}/{}/{}"> <b>SAN FRANCISCO </b></a>""".format (pname, 'CA', 'San_Francisco')
        mid_html += """<br><li><a href="/city/{}/{}/{}"> <b>NEW YORK </b></a>""".format (pname, 'NY', 'New_York')
        mid_html += """<br><li><a href="/city/{}/{}/{}"> <b>LONDON </b></a>""".format (pname, 'UK', 'London')
        mid_html += """<br><li><a href="/city/{}/{}/{}"> <b>KUALA LUMPUR </b></a>""".format (pname, 'Malaysia', 'Kuala_Lumpur')
    else:
        for h in r.keys ('planet*'):
            planetname = r.hget(h,'planetname')
            planetidentity = r.hget(h, 'identity')
            planetimage = r.hget(h, 'image')
            if planetname == avatar:
                break
        planetres = requests.get(planetidentity)
        planet = json.loads(planetres.content)
 
        mid_html += """<br><li>Diameter : {} </li>""".format(planet['diameter'])
        mid_html += """<li>Climate : {} </li>""".format(planet['climate'])
        mid_html += """<li>Terrain : {} </li></ul>""".format(planet['terrain'])
    mid_html +="""</div>"""
 
    mid_html += """<div>"""
    if avatar == "Tatooine":
        mid_html += """<ol style="width:30%; float:left;"> """
        mid_html += """<b> <font size = "3"> #LIGHT #BEAMEDUP #READINGS </font></b>"""
        for i in range (10):
            l = "light" + str(i)
#           l = r.keys(light_str)
#            for l in r.keys (light_str):
            ltime = r.hget(l, 'time')
            lreading = r.hget(l, 'reading')
            mid_html += """<li>Light Reading on {} is {}</li>""".format(ltime, lreading)
        mid_html += """</ol>"""

        mid_html += """<ol style="width:30%; float:left;">"""
        mid_html += """<b> <font size = "3"> #HEAT #BEAMEDUP #READINGS </font></b>"""
        for i in range (10):
            h = "heat" + str(i)
#            for h in r.keys (heat_str):
            htime = r.hget(h, 'time')
            hreading = r.hget(h, 'reading')
            mid_html += """<li>Heat Reading on {} is {}</li>""".format(htime, hreading)
        mid_html += """</ol>"""
    else:
        mid_html += """<p><b> <font size = "3"> #BEAMEDUP #READINGS - NONE </font></b></p><br>"""

    mid_html += """</div> <div>
                <a href="/start_game/{}"> <b>RETURN TO MAIN SCREEN</b></a>
                <footer>Copyright &copy; PiWars.com</footer>
                </div>""".format(pname)
 
    response = begin_html + mid_html + end_html
    return response

@app.route('/city/<pname>/<state>/<city>')
def city(pname, state, city):

    cityres = requests.get("""http://api.wunderground.com/api/47aab655a351d52c/conditions/q/{}/{}.json""".format(state, city))
    cityobj = json.loads(cityres.content)

    mid_html = """<div>
                <header> <h1> PIED PIPER PORTAL
                <img src="{}/{}/PiedPiper.jpg" align="right" style="width:120px;height:100px;vertical-align:text-top"></h1>
                         <h2> Information on {} </h2></header>""".format(object_access_url, avatarbucket, cityobj['current_observation']['display_location']['full'])
    mid_html += """</div> """   

    mid_html += """<div>"""
    mid_html += """<ul style="width:30%; float:left;">"""
#    mid_html += """<img src="{}/{}/{}" style="width:240x;height:200px;vertical-align:text-top"> """.format(object_access_url, planetbucket, filename)

    mid_html += """<br><li>Last updated on : {} </li>""".format(cityobj['current_observation']['observation_time'])

    mid_html += """<li>Weather : {} </li>""".format(cityobj['current_observation']['weather'])
    mid_html += """<li>Temperature : {} </li></ul>""".format(cityobj['current_observation']['temperature_string'])
    mid_html += """<li>Feels like : {} </li></ul>""".format(cityobj['current_observation']['feelslike_string'])
    mid_html += """<li>Feels like : {} </li></ul>""".format(cityobj['current_observation']['feelslike_string'])
    mid_html += """<li>Heat Index : {} </li></ul>""".format(cityobj['current_observation']['heat_index_string'])

    mid_html += """</div> <div>
                <a href="/start_game/{}"> <b>RETURN TO MAIN SCREEN</b></a>
                <footer>Copyright &copy; PiWars.com</footer>
                </div>""".format(pname)
 
    response = begin_html + mid_html + end_html
    return response

@app.route('/register')
def register():
    response = make_response(render_template('register.html'))
    return response

@app.route('/suregister.html', methods=['POST'])
def suregister():

    uname = request.form['username']
    upassword = request.form['psw']
    uidentity = request.form['identity']
    uswapi = "http://swapi.co/api/people/"+ uidentity + "/"
    uimage = request.form['image']
    resp = "Username : " + uname
    hero_num = r.incr('new_hero_num')
    newhero = 'hero' + str(hero_num)
    
    pname = ""
    for p in r.keys ('hero*'):
        pname = r.hget(p,'username')
        ppasswd = r.hget(p,'password')
        if uname == pname:
            break
    if uname == pname:
        resp = "Username : " + uname + " exists.  Please choose another name"
    else:
        r.hmset(newhero, {'username':uname, 'password':upassword, 'identity':uswapi, 'image':uimage})
        resp = "Username : " + uname + " has been created"
    return resp
    
if __name__ == "__main__":
	app.run(debug=False, host='0.0.0.0', \
                port=int(os.getenv('PORT', '5000')), threaded=True)
