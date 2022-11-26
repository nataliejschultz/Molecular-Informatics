import json
import folium
from flask import Flask, render_template, redirect, url_for, request
import time

app = Flask(__name__, template_folder="templates")

from app import app as application
#passes in city from user input and outputs city's longitude
#and latitude from API Ninjas Geocoding API.

def get_city_coordindates(city):
    import requests
    url = "https://api.api-ninjas.com/v1/geocoding?city={}&country=USA&state=Colorado".format(city)

    payload={}
    headers = {
        'x-api-key': ''
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
    print(float(long))
    print(float(lat))
    m = folium.Map(location=[float(lat), float(long)], tiles="https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png?api_key=", attr="Stadia.AlidadeSmooth", zoom_start=13)
    tooltip = "Click for air quality data!"
    folium.Marker([float(lat), float(long)],
                  popup=folium.Popup(f"<strong> {city}, Colorado </strong>" ),
                  tooltip = tooltip,
                  icon=folium.Icon(icon="cloud", color="purple")).add_to(m)
    m.save(map_loc)


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

@app.route('/results', methods=["GET","POST"])
def results():
    if request.method == "POST":
        #gets input from user and sets city equal to city name
        city = request.form.get("city")
        long2,lat2 = get_city_coordindates(city)
        path_to_map = "city.html"
        update_map(long2, lat2, city, "./templates/" + path_to_map)
        return render_template(path_to_map)

if __name__ == '__main__': 
    application.run(host="localhost", port=8080, debug=True)