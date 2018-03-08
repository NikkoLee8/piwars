import SENSOR
import setenv
import time
import os
import redis
from flask import Flask, render_template, redirect, request, url_for, make_response
#import boto

r = redis.Redis(host=os.environ['redis_hostname'], port=os.environ['redis_port'], password=os.environ['redis_password'])
avatarbucket = os.environ['avatar']
ecs_access_key = os.environ['ECS_access_key']
ecs_secret_key = os.environ['ECS_secret']
ecs_host = os.environ['ECS_host']
object_acess_utl = os.environ['object_access_URL']

app = Flask(__name__)

begin_html = """<!DOCTYPE html>
<html>
<head>
<style> 

header {background: black;color:white;}
footer {background: #aaa;color:white;}
.nav {background:#eee;color:black;}

.nav ul {
    list-style-type: none;
    padding: 0;
}
.nav ul a {
    text-decoration: none;
}

@media all and (min-width: 768px) {
    .nav {text-align:left;-webkit-flex: 1 auto;flex:1 auto;-webkit-order:1;order:1;}
    .article {-webkit-flex:5 0px;flex:5 0px;-webkit-order:2;order:2;}
    footer {-webkit-order:3;order:3;}
}
</style>
</head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
<body>
"""

end_html = "</body></html>"

@app.route('/')
def mainmenu():

    mid_html = """<header> <h1> PIED PIPER APPLIANCE </h1>"""
#<img src={}/{}/PiedPiper.jpg" align="right" style="width:120px;height:100px;vertical-align:text-top"></h1> """.format(object_access_url,avatarbucket)
    mid_html += """<header> <h1> Readings for HEAT OR LIGHT </h1> 
        <nav class="nav">
        <ul>"""

    mid_html += """<li><a href="/photoloop"> <font color = "black"> <b> LIGHT READING </b></a> </li>
                   <li><a href="/thermoloop"> <font color = "black"> <b>HEAT READING </b></a> </li>  """
    mid_html += """</ul> </nav> """
    mid_html += """<footer>Copyright &copy; PiWar.com</footer>
            </div> """
    response = begin_html + mid_html + end_html
    return response

def init():
    SENSOR.setup()

# For Photoresist to get light. 10 readings
@app.route('/photoloop')
def photoloop():
    init()
    mid_html = """<div class = "flex-container">
                <header> <h1> Readings for LIGHT </h1> 
        <nav class="nav">
        <ol>"""
    for x in range(10):        

        SENSOR.LedRedOn()
        res = SENSOR.getResult() - 80
        if res < 0:
            res = 0
        if res > 100:
            res = 100
        print 'res = %d' % res
        newreading = "light"+str(x)
        readtime = time.ctime()
        r.hmset(newreading, {'time' :readtime, 'reading':res})
        mid_html += "<li>Light Reading on {} is {}</li>".format (readtime, res)
        time.sleep(0.5)
        SENSOR.LedRedOff()
        time.sleep(1.5)
    SENSOR.destroy()
    mid_html += """</ol> <a href="/"> <font color = "black"> <b> RETURN TO MAIN SCREEN </b></a> </nav>"""
    mid_html += """<footer>Copyright &copy; PiWar.com</footer>
            </div> """
    response = begin_html + mid_html + end_html
    return response

# For Thermistor to get heat. 10 readings
@app.route('/thermoloop')
def thermoloop():
    init()
    mid_html = """<div class = "flex-container">
                <header> <h1> Readings for HEAT </h1> 
        <nav class="nav">
        <ol>"""
    for x in range(10):
        res = SENSOR.getResult()
        print 'res = %d' % res
        newreading = "heat"+str(x)
        readtime = time.ctime()
        r.hmset(newreading, {'time' :readtime, 'reading':res})
        mid_html += "<li>Heat Reading on {} is {}</li>".format (readtime, res)
        time.sleep(2)
        if res > 80:
            SENSOR.SoundBuzzer()
    SENSOR.destroy()
    mid_html += """</ol> <a href="/"> <font color = "black"> <b> RETURN TO MAIN SCREEN </b></a> </nav>"""
    mid_html += """<footer>Copyright &copy; PiWar.com</footer>
            </div> """
    response = begin_html + mid_html + end_html
    return response

# if __name__ == '__main__':
#   init()
#   try:
#       loop()
#   except KeyboardInterrupt: 
#       ADC0832.destroy()
#       print 'The end !'

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', \
                port=int(os.getenv('PORT', '5000')), threaded=True)
