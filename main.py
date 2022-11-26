import requests as requests

citieslist = ["Boulder", "Denver", "Englewood", "Longmont", "Aspen"]

for city in citieslist:

    url = "https://api.ambeedata.com/latest/by-city"

    querystring = {"city": city}
    headers = {
        'x-api-key': "",
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
    
    for k,v in dictionary.items():
        print("key",k,"value",v)