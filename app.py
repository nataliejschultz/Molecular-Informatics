import json
from tempfile import tempdir
import folium
from flask import Flask, render_template, redirect, url_for, request
import requests as requests
import boto3
from botocore.exceptions import ClientError
import sys

ambee_api_key = ''
api_ninjas_key = ''

app = Flask(__name__, template_folder="templates")

if len(sys.argv) > 1:
    ambee_api_key = sys.argv[1]
    api_ninjas_key = sys.argv[2]
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
    secret = client.get_secret_value(SecretId=secret_name)['SecretString'] #get_secret_value returns secret as a json string
    secret_dict = json.loads(secret) #convert secret string to a dictionary using json loads 
    ambee_api_key = secret_dict.get("ambee_api")
    api_ninjas_key = secret_dict.get("api_ninjas")

#passes in city from user input and outputs city's longitude
#and latitude from API Ninjas Geocoding API.
def get_city_coordindates(city):
    #calls REST based API
    url = "https://api.api-ninjas.com/v1/geocoding?city={}&country=USA&state=Colorado".format(city)

    payload={}
    headers = {
        'x-api-key': api_ninjas_key #key is either pulled from secrets manager or input in command line
    }
    response = requests.request("GET", url, headers=headers, data=payload) #calls api using inputs above
    res = json.loads(response.text) #converts json response to a list of dictionaries in python format

    for city_dict in res: #loops through the list of dictionaries generated above
        if city_dict.get("state") == "Colorado": #finds matching k,v pair for Colorado
            long, lat = city_dict.get("longitude"), city_dict.get("latitude") #uses .get method to assign long and lat
            break #this keeps it from looping through after it finds the first k,v pair that matches

    return long, lat

#takes long, lat, and user input city from above function and
#generates a map html file using folium. map saves as city.html
def update_map(long, lat, city, map_loc):

    url = "https://api.ambeedata.com/latest/by-lat-lng"

    querystring = {"lat": str(lat), "lng": str(long)} #query input determined by api
    headers = {
        'x-api-key': ambee_api_key, #api key is set 
        'Content-type': "application/json"
    }
    res = requests.request("GET", url, headers=headers, params=querystring)
    aqdata = res.text
    aqdata_dict = (json.loads(aqdata))
    # since we only care about one dictionary in the list of dictionaries (aqdata_dict["stations"])
    # you don't need a for loop and instead can do this for all variables needed:
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
        outer_circle = "#8486e0"
        inner_circle = "#495280"
        air_quality_value = "Good"

    #moderate air quality 
    elif 51 <= int(AQI) <= 100:
        outer_circle = "#258016"
        inner_circle = "#13420b"
        air_quality_value = "Moderate" 
    #unhealthy for sensitive groups
    elif 101 <= int(AQI) <= 150:
        outer_circle = "#e2e810"
        inner_circle = "#9fa318"
        air_quality_value = "Unhealthy for Sensitive Groups" 

    #unhealthy air quality
    elif 151 <= int(AQI) <= 200:
        outer_circle= "#eb9502"
        inner_circle= "#c47f08"
        air_quality_value = "Unhealthy" 

    #very unhealthy air quality
    elif 201 <= int(AQI) <= 300:
        outer_circle = "#e33809"
        inner_circle = "#a12908" 
        air_quality_value = "Very Unhealthy" 

    #hazardous 
    elif 300 <= int(AQI):
        outer_circle = "#f20a99"
        inner_circle = "#990861"
        air_quality_value = "Hazardous" 

    #the standards are different for each of the particles, so they have their own conditionals.
  
    if int(CO) <= 100:
        co_color  = "#4DCB7D"
        co_quality = "Good"
    elif 100 < int(CO):
        co_color = "#e33809"
        co_quality = "Poor"
 
    if int(NO2) <= 100:
        no2_color  = "#4DCB7D"
        no2_quality = "Good"
    elif 100 < int(NO2):
        no2_color = "#e33809"
        no2_quality = "Poor"
    
    if int(SO2) <= 75:
        so2_color  = "#4DCB7D"
        so2_quality = "Good"
    elif 75 < int(SO2):
        so2_color = "#e33809"
        so2_quality = "Poor"

    if int(OZONE) <= 70:
        ozone_color  = "#4DCB7D"
        ozone_quality = "Good"
    elif 70 < int(OZONE):
        ozone_color = "#e33809"
        ozone_quality = "Poor"
    

    # if there is more than 1 word in the split city string 
    if len(city.split(" ")) > 1:
        # then capitalize each word in list and add to a new list
        # then join all words in the list with speaces
        city = ' '.join([x.capitalize() for x in city.split(" ")])
    else:
        # otherwise just capitalize the one word in the city name
        city = city.capitalize()

    popup_info = f"""<table style='width: 100%; white-space: nowrap; border: 1px solid white; border-collapse: collapse; font-family: "American Typewriter", serif; font-size: 20px; text-align: center;'>
    <tr>
    <th style="text-align: center; width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse;"> Parameter </th>
    <th style="text-align: center; width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse;"> Value </th>
    <th style="text-align: center; width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse;"> Quality </th>
    </tr>

    <tr style="background-color: {outer_circle};">
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; "background-color: transparent;"><span style="color: #000000;"> AQI </span></td>
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; background-color: transparent;">{AQI}</td>
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; background-color: transparent;>"<span style="color: #000000;"> {air_quality_value} </span></td>
    </tr> 
    
    <tr style="background-color: {co_color};">
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; "background-color: transparent;"><span style="color: #000000;"> CO </span></td>
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; background-color: transparent;"> {CO} (ppm)</td>
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; background-color: transparent;>"<span style="color: #000000;"> {co_quality} </span></td>
    </tr>

    <tr style="background-color: {no2_color};">
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse;"background-color: transparent;"><span style="color: #000000;"> NO2 </span></td></td>
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; background-color: transparent;>"<span style="color: #000000;"> {NO2} (ppb) </span></td>
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; background-color: transparent;>"<span style="color: #000000;"> {no2_quality} </span></td>
    </tr>

    <tr style="background-color: {so2_color};">
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; "background-color: transparent;"><span style="color: #000000;"> SO2 </span></td>
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; background-color: transparent;>"<span style="color: #000000;"> {SO2} (ppb) </span></td>
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; background-color: transparent;>"<span style="color: #000000;"> {so2_quality} </span></td>
    </tr>

    <tr style="background-color: {ozone_color};">
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; "background-color: transparent;"><span style="color: #000000;"> OZONE </span></td>
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; background-color: transparent;>"<span style="color: #000000;"> {OZONE} (ppb) </span></td>
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; background-color: transparent;>"<span style="color: #000000;"> {ozone_quality} </span></td>
    </tr>

    <tr style="background-color: #E7E7F4;">
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; "background-color: transparent;"><span style="color: #000000;"> PM10 </span></td>
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; background-color: transparent;>"<span style="color: #000000;"> {PM10} (μg/m3) </span></td>
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; background-color: transparent;>"<span style="color: #000000;"> N/A </span></td>
    </tr>

    <tr style="background-color: #E7E7F4;">
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; "background-color: transparent;"><span style="color: #000000;"> PM2.5 </span></td>
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; background-color: transparent;>"<span style="color: #000000;"> {PM25} (ug/m3) </span></td>
    <td style="width: 300px; padding: 15px; border-spacing: 10px; border: 1px solid white; border-collapse: collapse; background-color: transparent;>"<span style="color: #000000;"> N/A </span></td>
    </tr>

    </table>"""
  
    m = folium.Map(location=[float(lat), float(long)], tiles="https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}", attr="Esri.NatGeoWorldMap", zoom_start=13)
    tooltip_format = "<strong>Click for air quality data!</strong>"
    # folium.element.CssLink("./templates/mapstyle.css", download=True)
    folium.Marker([float(lat), float(long)],
                    # popup=folium.Popup(popup_info, min_width=125, max_width=130),
                    popup = folium.Popup(popup_info),
                    tooltip = folium.map.Tooltip(tooltip_format, style='font-family: "American Typewriter", serif;'),
                    icon = folium.DivIcon(html=f"""
        <div><svg style= "overflow: visible">
            <circle cx="0" cy="0" r="80" fill="{outer_circle}" opacity=".4"/>
            <circle cx="0", cy="0" r="50" fill="{inner_circle}", opacity=".3" 
        </svg></div>""")).add_to(m)
    m.save(map_loc)


#displays homepage (if get) or creates map if it's a post

@app.route('/', methods=["GET", "POST"], endpoint='root')
def root():
    if request.method == "POST": #if user enters in a city to the input box:
        city = request.form["city"] # set city variable equal to their input
        return redirect(url_for('results', city=city)) #redirects to results route
    return render_template('home_page.html') #returns homepage until input is received 

#app.route decorator tells the server to execute the function below when the result
@app.route('/results', methods=["GET","POST"], endpoint='results')
def results():
    if request.method == "POST":
        #gets input from user and sets city equal to the input
        city = request.form.get("city") # city from user input
        long, lat = get_city_coordindates(city) # calls func, get user's requested city coords
        path_to_map = "city.html" #sets path to html file that displays the map
        update_map(long, lat, city, "./templates/" + path_to_map) #passes in coords and user input to update the city.html page
        return render_template(path_to_map) #render_template function renders the updated html page to the user 

if __name__ == '__main__': 
    if len(sys.argv) > 1:
        app.run(host="localhost", port=8080, debug=True)
    else:
        app.run(host="0.0.0.0", port=8080, debug=True)