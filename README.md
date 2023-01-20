# Overview
* This project provides both frontend and backend functionality of a Colorado based Air Quality mapping website.
The majority of backend functionality is located in app.py, with additonal files being present for the frontend
design in the templates directory. 

* Users input a Colorado city of their choice on the hompage, and are redirected to a map of Colorado with their 
chosen city at the center. A circular icon initially indicates the AQI. When clicked, a popup of a table
appears and displays different air quality metrics for the user to analyze. 


## Example command to run locally

`pip3 install requirements.txt`

`python3 app.py ambee_api_key api_ninjas_apikey`


## Prerequisites
    * Must sign up for Ambee and Api-Ninjas' Geocoding api to obtain API keys
