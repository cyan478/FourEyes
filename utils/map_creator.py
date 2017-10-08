from geopy.geocoders import Nominatim # module to convert an address into latitude and longitude values
import requests # library to handle requests
import pandas as pd # library for data analsysis
import numpy as np # library to handle data in a vectorized manner
import random # library for random number generation

# libraries for displaying images
from IPython.display import Image 
from IPython.core.display import HTML 
    
# tranforming json file into a pandas dataframe library
from pandas.io.json import json_normalize

import folium # plotting library


# ### Define Foursquare Credentials and Version

CLIENT_ID = "DTSVJ0JJUJBJCB51255FIKRRGZ2FLC0SOJYIHQKCMXCJM5NS"
CLIENT_SECRET = "WSQTKQWIQZYMYIAVVAUXPJCUHML0DNMW34O5AUCMM4R0I1KZ"
VERSION = "20171006"
LIMIT = 30
print ("Your credentials:")
print ("CLIENT_ID: " + CLIENT_ID)
print ("CLIENT_SECRET:" + CLIENT_SECRET)

# function that extracts the category of the venue
def get_category_type(row):
    try:
        categories_list = row["categories"]
    except:
        categories_list = row["venue.categories"]
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]["name"].encode('ascii',errors='ignore')

# #### Convert the address of MassChallenge to its latitude and longitude equivalence

def generateMap(imgObj):

    address = "21 Drydock Ave, Boston, MA"
    geolocator = Nominatim()
    location = geolocator.geocode(address)
    latitude = location.latitude
    longitude = location.longitude
    print (latitude, longitude)

    print (imgObj + " .... OK!")
    radius = 2000
    
    url="https://api.foursquare.com/v2/venues/search?client_id={}&client_secret={}&ll={},{}&v={}&query={}&radius={}&limit={}".format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, imgObj, radius, LIMIT)

    results = requests.get(url).json()

    venues = results["response"]["venues"]

    print ( venues )

    # tranform venues into a dataframe
    dataframe = json_normalize(venues)
    dataframe.head()

    # #### Define information of interest and filter dataframe

    # keep only columns that include venue name, url, and anything that is associated with location
    filtered_columns = ['name', 'url', 'categories', 'verified'] + [col for col in dataframe.columns if col.startswith('location.')] + ['id']
    dataframe_filtered = dataframe.ix[:, filtered_columns]

    # filter the category for each row
    dataframe_filtered['categories'] = dataframe_filtered.apply(get_category_type, axis=1)

    # clean column names by keeping only last term
    dataframe_filtered.columns = [column.split(".")[-1] for column in dataframe_filtered.columns]
    dataframe_filtered.head(10)

    # #### Let's visualize the coffee shops that are nearby

    venues_map = folium.Map(location=[latitude, longitude], zoom_start=13) # generate map centred around MassChallenge

    # create a feature group for MassChallenge and add it to the map
    masschallenge = folium.map.FeatureGroup()
    masschallenge.add_child(
        folium.features.CircleMarker(
            [latitude, longitude],
            radius = 10,
            color = "red",
            fill_color = "red",
            fill_opacity = 0.6
        )
    )
    venues_map.add_child(masschallenge)


    # create a feature group for the coffee shops around MassChallenge and add it to the map
    coffee_shops = folium.map.FeatureGroup()
    for lat, lng, in zip(dataframe_filtered.lat, dataframe_filtered.lng):
        coffee_shops.add_child(
            folium.features.CircleMarker(
                [lat, lng],
                radius=5,
                color="blue",
                fill_color="blue",
                fill_opacity=0.6)
            )
    venues_map.add_child(coffee_shops)


    # add labels to each point on the map
    latitudes_list = list(dataframe_filtered.lat) + [latitude]
    longitudes_list = list(dataframe_filtered.lng) + [longitude]
    labels = list(dataframe_filtered.name) + ["MassChallenge"]

    for lat, lng, label in zip(latitudes_list, longitudes_list, labels):
        folium.Marker([lat, lng], popup=label).add_to(venues_map)

    # display map
    return venues_map


   