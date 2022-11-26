import folium
from folium import CustomIcon
import os
#create a map pbject

m = folium.Map(location=[39.7392, -104.9903], tiles="", zoom_start=12)

#Global Tooltip

tooltip = "Click for air quality data!"

#create county overlay 
overlay = os.path.join("overlays","denver.geojson")

#create custom marker icon
#logoIcon = folium.features.CustomIcon("ozone.png", icon_size= (50,50))

#air quality data


#create markers on the map. We can use HTML here 
#possible ideas: add data, add chemical symbols of each 
folium.Marker([39.739200, -104.990300],
             popup = '<strong> Denver, Colorado <\strong>', 
            tooltip = tooltip,
            icon=folium.Icon(icon="cloud")).add_to(m),
folium.Marker([40.0150, -105.2705],
             popup = '<strong> Boulder, Colorado <\strong>', 
            tooltip = tooltip,
            icon=folium.Icon(icon="cloud", color="purple")).add_to(m),

folium.Marker([39.7047, -105.0814],
             popup = '<strong> Lakewood, Colorado <\strong>', 
            tooltip = tooltip,
            icon=folium.Icon(icon="cloud", color="purple")).add_to(m),
folium.Marker([39.6478, -104.9878],
             popup = folium.Popup('<strong> Englewood, Colorado <\strong>'),
            tooltip = tooltip,
            icon=folium.Icon(icon="cloud", color="purple")).add_to(m),
#Special circle marker

#Adding overlays to counties

folium.GeoJson(overlay, name="Denver").add_to(m)
#generates map html file with all the javascript necessary to display the map
m.save('map_ref.html')