from flask import *
from geopy.geocoders import Nominatim
import geocoder
from waitress import serve
from gevent.pywsgi import WSGIServer
import requests
import json
import pyqrcode
import png
from pyqrcode import QRCode

GENERATED = False
VERIFIED = False

app = Flask(__name__,template_folder='template',static_folder='static')

def findcoordinates(address):

    loc = Nominatim(user_agent="GetLoc")
    getLoc = loc.geocode(address)
    #print(getLoc.address)
    #print("Latitude = ", getLoc.latitude, "\n")
    #print("Longitude = ", getLoc.longitude)
    return getLoc.address,getLoc.latitude,getLoc.longitude

# Function to find plus code using Coordinates
def findpluscode(lat,long):
    s1 = str(lat) + ',' +str(long)
    parameters = {
        # 'address' : '19.108914019118583, 72.86535472954193'
        'address' : str(s1)
    }
    response = requests.get("https://plus.codes/api", params=parameters)
    r = json.loads(response.text)
    return r['plus_code']['global_code']

def findaddressusingcoordinates(lat,long):
    s1 = str(lat) + ',' + str(long)
    geoLoc = Nominatim(user_agent="GetLoc")
    locname = geoLoc.reverse(s1)
    return str(locname.address)



@app.route("/")
def LandingPage():
    return render_template('LandingPage.html')


@app.route("/main")
def Main():
    return render_template('MainPage.html', generated = GENERATED)


@app.route("/about")
def AboutPage():
    return render_template('About.html')


@app.route("/generate", methods=['GET', 'POST'])
def GenerateCode():
    global GENERATED

    if request.method == "POST":
        GENERATED = True
        flat_building = str(request.form['flat_building'])
        street = str(request.form['street'])
        city = str(request.form['city'])
        state = str(request.form['state'])
        country = "India"
        pincode = str(request.form['pincode'])
        # print(flat_building)
        # print(street)
        # print(city)
        # print(state)
        # print(country)
        # print(pincode)
        address = str(street + ',' + city + ',' + country + ',' + pincode)
        #global_address = str(flat_building + ',' + street + ',' + city + ',' + country + ',' + pincode)
        print(address)

        a,b,c = findcoordinates(address)
        print(a,b,c)

        pluscode = findpluscode(float(b),float(c))
        qr = pyqrcode.create(pluscode)
        qr.png('static/img/qr.png', scale = 6)
        qrsrc="static/img/qr.png"

        return render_template('GenerateCode.html', generated = GENERATED, global_address = a, latitude_generated = b, longitude_generated = c, plus_code = pluscode, qr_code = qrsrc)

    GENERATED = False
    return render_template('GenerateCode.html', generated = GENERATED)

@app.route("/verify", methods=['GET', 'POST'])
def Verify():
    global VERIFIED

    if request.method == "POST":
        VERIFIED = True
        latitude = str(request.form['lat'])
        longitude = str(request.form['long'])
        #pluscode = str(request.form['pcode'])
        globaladdress = findaddressusingcoordinates(latitude,longitude)
        pluscode = findpluscode(latitude,longitude)
        #globaladdress = findcoordinatespluscode(pluscode)
        return render_template('VerifyCode.html', verified=VERIFIED, global_address=globaladdress, plus_code=pluscode, latitude_generated=latitude,longitude_generated=longitude)
        

    VERIFIED = False
    return render_template('VerifyCode.html', verified=VERIFIED)

if __name__ == "__main__":
    app.run(debug=True)
    #serve(app, host="localhost", port=8080)
    #http_server = WSGIServer(('', 5000), app)
    #http_server.serve_forever()