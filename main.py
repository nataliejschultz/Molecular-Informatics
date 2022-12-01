import requests as requests

# citieslist = ["Boulder", "Denver", "Englewood", "Longmont", "Aspen"]
#
# for city in citieslist:

url = "https://api.ambeedata.com/latest/by-lat-lng"

querystring = {"lat": str(39.7392), "lng": str(-104.9903)}
headers = {
    'x-api-key': "2412435e0c836f63d2cef3ced8f28f65237485126347dfeba37bd36286d0faeb",
    'Content-type': "application/json"
    }
res = requests.request("GET", url, headers=headers, params=querystring)
print(res.text)

import json

aqdata = res.text

#json.loads method converts the res.text string into a dictionary
aqdata_dict = (json.loads(aqdata))
# print(len(aqdata_dict))

# print(aqdata_dict["stations"][0]["aqiInfo"])
# we know that the "stations" key has a list as its value 
# so we can loop through that list

for dictionary in aqdata_dict["stations"]:
    print(type(dictionary))
    
    # we know that the entries in the list are dictionaries 
    # so we can loop through the key, value pairs with the items() method
    
    # for k,v in dictionary.items():
    CO = dictionary.get("CO")
    print(CO)
    print(type(CO))