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

print ("Folium installed")
print ("Libraries imported.")


# ### Define Foursquare Credentials and Version

# ##### Make sure that you have created a Foursquare developer account and have your credentials handy

# In[ ]:

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

# In[ ]:

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
    url

    results = requests.get(url).json()
    results

    venues = results["response"]["venues"]

    # tranform venues into a dataframe
    dataframe = json_normalize(venues)
    dataframe.head()

    # #### Define information of interest and filter dataframe

    # In[ ]:

    # keep only columns that include venue name, url, and anything that is associated with location
    filtered_columns = ['name', 'url', 'categories', 'verified'] + [col for col in dataframe.columns if col.startswith('location.')] + ['id']
    dataframe_filtered = dataframe.ix[:, filtered_columns]

    # filter the category for each row
    dataframe_filtered['categories'] = dataframe_filtered.apply(get_category_type, axis=1)

    # clean column names by keeping only last term
    dataframe_filtered.columns = [column.split(".")[-1] for column in dataframe_filtered.columns]
    dataframe_filtered.head(10)

    # #### Let's visualize the coffee shops that are nearby

    # In[ ]:

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
    venues_map


    #    

    # <a id="item2"></a>

    # ## 2. Explore a Given Venue
    # > `https://api.foursquare.com/v2/venues/`**VENUE_ID**`?client_id=`**CLIENT_ID**`&client_secret=`**CLIENT_SECRET**`&v=`**VERSION**

    # ### A. Let's explore the first verified coffee shop -- _Barrington Coffee Roasting Company_

    # In[ ]:

    venue_id = "4ed934370aaf49e0281c7f9d" # ID of Barrington Coffee
    url="https://api.foursquare.com/v2/venues/{}?client_id={}&client_secret={}&v={}".format(venue_id, CLIENT_ID, CLIENT_SECRET, VERSION)
    url


    # #### Send GET request for result

    # In[ ]:

    result = requests.get(url).json()
    result["response"]["venue"].keys()


    # ### B. Get the venue's overall rating

    # In[ ]:

    result["response"]["venue"]["rating"]


    # ### C. Get the number of tips

    # In[ ]:

    result["response"]["venue"]["tips"]["count"]


    # ### D. Get the venue's tips
    # > `https://api.foursquare.com/v2/venues/`**VENUE_ID**`/tips?client_id=`**CLIENT_ID**`&client_secret=`**CLIENT_SECRET**`&v=`**VERSION**`&limit=`**LIMIT**

    # #### Create URL and send GET request. Make sure to set limit to get all tips

    # In[ ]:

    ## Barrington Coffee tips
    limit = 100 # set limit to be greater than the total number of tips
    url="https://api.foursquare.com/v2/venues/{}/tips?client_id={}&client_secret={}&v={}&limit={}".format(venue_id, CLIENT_ID, CLIENT_SECRET, VERSION, limit)

    results = requests.get(url).json()
    results


    # #### Get tips and list of associated features

    # In[ ]:

    tips = results["response"]["tips"]["items"]

    tip = results["response"]["tips"]["items"][0]
    tip.keys()


    # #### Format column width and display all tips

    # In[ ]:

    pd.set_option('display.max_colwidth', -1)

    tips_df = json_normalize(tips) # json normalize tips

    # columns to keep
    filtered_columns = ["text", "agreeCount", "disagreeCount", "id", "user.firstName", "user.lastName", "user.gender", "user.id"]
    tips_filtered = tips_df.ix[:, filtered_columns]

    # display tips
    tips_filtered

    # 

    # <a id="item4"></a>

    # ## 4. Explore a location
    # > `https://api.foursquare.com/v2/venues/`**explore**`?client_id=`**CLIENT_ID**`&client_secret=`**CLIENT_SECRET**`&ll=`**LATITUDE**`,`**LONGITUDE**`&v=`**VERSION**`&limit=`**LIMIT**

    # #### Get latitude and longitude values of Barrington Coffee Roasting Company

    # In[ ]:

    latitude = 42.350688
    longitude = -71.048868


    # #### Define URL

    # In[ ]:

    url="https://api.foursquare.com/v2/venues/explore?client_id={}&client_secret={}&ll={},{}&v={}&radius={}&limit={}".format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, radius, LIMIT)
    url


    # #### Send GET request and examine results

    # In[ ]:

    results = requests.get(url).json()
    results


    # #### Get relevant part of JSON

    # In[ ]:

    items = results["response"]["groups"][0]["items"]
    items[0]["venue"].keys()


    # #### Process JSON and convert it to a clean dataframe

    # In[ ]:

    dataframe = json_normalize(items) # flatten JSON

    # filter columns
    filtered_columns = ['venue.name', 'venue.url', 'venue.categories'] + ["venue.rating"] + [col for col in dataframe.columns if col.startswith('venue.location.')] + ["venue.id"]
    dataframe_filtered = dataframe.ix[:, filtered_columns]

    # filter the category for each row
    dataframe_filtered['venue.categories'] = dataframe_filtered.apply(get_category_type, axis=1)

    # clean columns
    dataframe_filtered.columns = [col.split(".")[-1] for col in dataframe_filtered.columns]

    dataframe_filtered.head(10)


    # #### Let's visualize these items on the map around our location

    # In[ ]:

    venues_map = folium.Map(location=[latitude, longitude], zoom_start=15) # generate map centred around Barrington Coffee


    # create a feature group for Barrington Coffee and add it to the map
    barrington = folium.map.FeatureGroup()
    barrington.add_child(
        folium.features.CircleMarker(
            [latitude, longitude],
            radius = 10,
            color = "red",
            fill_color = "red",
            fill_opacity = 0.6
        )
    )
    venues_map.add_child(barrington)

    # add labels to each point on the map
    latitudes_list = list(dataframe_filtered.lat) + [latitude]
    longitudes_list = list(dataframe_filtered.lng) + [longitude]
    labels = list(dataframe_filtered.name) + ["Barrington Coffee"]
    venue_categories = list(dataframe_filtered.categories) + ["Coffee Shop"]

    #for lat, lng, label, category in zip(latitudes_list, longitudes_list, labels, venue_categories):
        # popup_text = label + ", " + category
    #    folium.Marker([lat, lng], popup=popup_text).add_to(venues_map)

    # display map
    venues_map.save("map.html")


    #    

    # <a id="item5"></a>

    # ## 5. Explore Trending Venues
    # > `https://api.foursquare.com/v2/venues/`**trending**`?client_id=`**CLIENT_ID**`&client_secret=`**CLIENT_SECRET**`&ll=`**LATITUDE**`,`**LONGITUDE**`&v=`**VERSION**

    # ### Let's get trending venues around Barrington Coffee

    # In[ ]:

    # define URL
    url="https://api.foursquare.com/v2/venues/trending?client_id={}&client_secret={}&ll={},{}&v={}".format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION)

    # send GET request and get trending venues
    results = requests.get(url).json()
    results


    # ### Check if any venues are trending at this time

    # In[ ]:

    if len(results["response"]["venues"]) == 0:
        trending_venues_df = "No trending venues are available at the moment!"
        
    else:
        trending_venues = results["response"]["venues"]
        trending_venues_df = json_normalize(trending_venues)

        # filter columns
        columns_filtered = ["name", "url", "categories"] + [col for col in trending_venues_df.columns if col.startswith("stats")] + ["location.distance", "location.address", "location.city", "location.postalCode", "location.state", "location.country", "location.lat", "location.lng"]
        trending_venues_df = trending_venues_df.ix[:, columns_filtered]

        # filter the category for each row
        trending_venues_df['categories'] = trending_venues_df.apply(get_category_type, axis=1)


    # In[ ]:

    # display trending venues
    trending_venues_df


    # ### Visualize trending venues

    # In[ ]:

    if len(results["response"]["venues"]) == 0:
        venues_map = "Can't generate visual as no trending venues are available at the moment!"

    else:
        venues_map = folium.Map(location=[latitude, longitude], zoom_start=15) # generate map centred around Barrington Coffee


        # create a feature group for Barrington Coffee and add it to the map
        barrington = folium.map.FeatureGroup()
        barrington.add_child(
            folium.features.CircleMarker(
                [latitude, longitude],
                radius = 10,
                color = "red",
                fill_color = "red",
                fill_opacity = 0.6
            )
        )
        venues_map.add_child(barrington)

        # add labels to each point on the map
        latitudes_list = list(trending_venues_df["location.lat"]) + [latitude]
        longitudes_list = list(trending_venues_df["location.lng"]) + [longitude]
        labels = list(trending_venues_df.name) + ["Barrington Coffee"]
        venue_categories = list(trending_venues_df.categories) + [""]

        #for lat, lng, label, category in zip(latitudes_list, longitudes_list, labels, venue_categories):
        #    popup_text = label + ", " + category
        #    folium.Marker([lat, lng], popup=popup_text).add_to(venues_map)


    # In[ ]:

    # display map
    return venues_map.save("map.html")

generateMap("Coffee Shops")