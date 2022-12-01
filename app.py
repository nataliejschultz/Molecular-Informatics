import json
from tempfile import tempdir
import folium
from flask import Flask, render_template, redirect, url_for, request
import requests as requests
import boto3
from botocore.exceptions import ClientError
import sys

app = Flask(__name__, template_folder="templates")

#passes in city from user input and outputs city's longitude
#and latitude from API Ninjas Geocoding API.

if sys.argv[1] is not None and sys.argv[1] == "dev":
    ambee_api_key = sys.argv[2]
    api_ninjas_key = sys.argv[3]
else:
    secret_name = "MolecularInformatics/FinalProject/AirQualityData"
    #we can't access anything in other regions, so we have to set it to the same region as the EC2 instance
    region_name = "us-west-2"

    # Create a Secrets Manager client using boto3
    session = boto3.session.Session()
    #pass in service name and region name arguments to create the client
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
        # Decrypts secret using the associated KMS key.
        #get secret value method is specific to this secrets manager client 
    secret = client.get_secret_value(SecretID=secret_name)['SecretString'] #get_secret_value returns secret as a json string
    secret_dict = json.loads(secret) #convert secret string to a dictionary using json loads 
    ambee_api_key = secret_dict.get("ambee_api")
    api_ninjas_key = secret_dict.get("api_ninjas")

def get_city_coordindates(city):
    import requests
    url = "https://api.api-ninjas.com/v1/geocoding?city={}&country=USA&state=Colorado".format(city)

    payload={}
    headers = {
        'x-api-key': api_ninjas_key
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    res = json.loads(response.text)

    for city_dict in res:
        if city_dict.get("state") == "Colorado":
            long, lat = city_dict.get("longitude"), city_dict.get("latitude")
            break

    return long, lat

#takes long, lat, and user input city from above function and
#generates a map html file using folium. map saves as city.html
def update_map(long, lat, city, map_loc):

    url = "https://api.ambeedata.com/latest/by-lat-lng"

    querystring = {"lat": str(lat), "lng": str(long)}
    headers = {
        'x-api-key': ambee_api_key,
        'Content-type': "application/json"
    }
    res = requests.request("GET", url, headers=headers, params=querystring)
    print(res.text)
    aqdata = res.text
    aqdata_dict = (json.loads(aqdata))
    # since we only care about one dictionary in the list of dictionaries (aqdata_dict["stations"])
    # you don't need a for loop and instead can do this for all variables needed:
    # for dictionary in aqdata_dict["stations"]:
    AQI = aqdata_dict["stations"][0].get("AQI")
    CO = aqdata_dict["stations"][0].get("CO")
    NO2 = aqdata_dict["stations"][0].get("NO2")
    SO2 = aqdata_dict["stations"][0].get("SO2")
    OZONE = aqdata_dict["stations"][0].get("OZONE")
    PM10 = aqdata_dict["stations"][0].get("PM10")
    PM25 = aqdata_dict["stations"][0].get("PM25")

#this series of ifs is used to set the color of the icon 
    #good air quality
    if int(AQI) <= 50:
        outer_circle= "#8486e0"
        inner_circle= "#495280"

    #moderate air quality 
    elif 51 <= int(AQI) <= 100:
        outer_circle= "#258016"
        inner_circle= "#13420b"

    #unhealthy for sensitive groups
    elif 101 <= int(AQI) <= 150:
        outer_circle= "#e2e810"
        inner_circle= "#9fa318"

    #unhealthy air quality
    elif 151 <= int(AQI) <= 200:
        outer_circle= "#eb9502"
        inner_circle= "#c47f08"

    #very unhealthy air quality
    elif 201 <= int(AQI) <= 300:
        outer_circle= "#e33809"
        inner_circle= "#a12908" 

    #hazardous 
    elif 300 <= int(AQI):
        outer_circle= "#f20a99"
        inner_circle= "#990861"

    # if there is more than 1 word in the split city string 
    if len(city.split(" ")) > 1:
        # then capitalize each word in list and add to a new list
        # then join all words in the list with speaces
        city = ' '.join([x.capitalize() for x in city.split(" ")])
    else:
        # otherwise just capitalize the one word in the city name
        city = city.capitalize()
    
    popup_info = f"""<strong> {city}, Colorado </strong> 
    <br>AQI = {AQI}
    <br> CO = {CO}
    <br> NO2 = {NO2}
    <br>SO2 = {SO2}
    <br>OZONE = {OZONE}
    <br>PM10 = {PM10}
    <br>PM25 = {PM25}"""

    # m = folium.Map(location=[float(lat), float(long)], tiles="https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}", attr="Esri.NatGeoWorldMap", zoom_start=13)
    # AN INVALUABLE RESOURCE https://www.python-graph-gallery.com/312-add-markers-on-folium-map
    m = folium.Map(location=[float(lat), float(long)], tiles="https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}", attr="Esri.NatGeoWorldMap", zoom_start=13)
    tooltip = "Click for air quality data!"
    # folium.element.CssLink("./templates/mapstyle.css", download=True)
    folium.Marker([float(lat), float(long)],
                    popup=folium.Popup(popup_info, min_width=125, max_width=130),
                    tooltip = tooltip,
                    icon=folium.DivIcon(html=f"""
        <div><svg style= "overflow: visible">
            <circle cx="0" cy="0" r="80" fill="{outer_circle}" opacity=".4"/>
            <circle cx="0", cy="0" r="50" fill="{inner_circle}", opacity=".3" 
        </svg></div>""")).add_to(m)
    m.save(map_loc)

from app import app as application

#displays homepage (if get) or creates map if it's a post
@app.route('/', methods=["GET", "POST"])
def root():
    #if user enters in a city to the input box:
    if request.method == "POST":
        #then set city equal to their input
        city = request.form["city"]
        #redirects to results page (below)
        return redirect(url_for('results', city=city))
    return render_template('home_page.html')

@app.route('/results', methods=["GET","POST"]) #app.route decorator tells the server to execute the function below when the result
def results():
    if request.method == "POST":
        #gets input from user and sets city equal to the input
        city = request.form.get("city") # city from user input
        long, lat = get_city_coordindates(city) # calls func, get user's requested city coords
        path_to_map = "./templates/city.html" #sets path to html file that displays the map
        update_map(long, lat, city, path_to_map) #passes in coords and user input to update the city.html page
        return render_template(path_to_map) #render_template function renders the updated html page to the user 

if __name__ == '__main__': 
    application.run(host="localhost", port=8080, debug=True)