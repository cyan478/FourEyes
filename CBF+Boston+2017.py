
# coding: utf-8

# # <a href="https://www.evensi.us/boston-cognitive-builder-faire-masschallenge/218135254"><img src="https://ibm.box.com/shared/static/j7xfq3avjufdua1r0kxoxcegybuzgr05.png" width=1000></a>
# 
# <hr>

# # <center> Learning FourSquare API with Python
# ## <center><a href="https://www.linkedin.com/in/aklson/">Alex Aklson</a>, Ph.D. (Data Scientist, IBM)

#    

# ## <center>Please Tweet about this event! 
# <a href=https://twitter.com/intent/tweet?text=Learning+%23datascience+at+%23CognitiveBuilder+%40BuildWithWatson+%40CognitiveClass+%40FoursquareAPI+Free+data+science+courses%3A+http%3A%2F%2Fcocl.us%2FCBF_Boston_CC><img src=https://ibm.box.com/shared/static/oza9rtt3xgxz310v9k197qadpb5yy38n.png style='border:1px solid #D3D3D3' width = 800></a>

#    

# <div class="alert alert-block alert-info" style="margin-top: 20px">
# <h2> Table of Contents</h2>  
# <font size = 3>
# 1. <a href="#item1">Foursquare API Search Function</a>    
# 2. <a href="#item2">Explore a Given Venue</a>   
# 3. <a href="#item3">Explore a User</a>  
# 4. <a href="#item4">Foursquare API Explore Function</a>  
# 5. <a href="#item5">Get Trending Venues</a>    
# 6. <a href="#item6">Explore real world data - San Francisco Crime Rate</a>  
# 7. <a href="#item7">Use Foursquare API to do cool analysis</a>  
# </font>
# <br>
# <p></p>
# 
# Estimated Time Needed: <strong>60 min</strong>
# </div>

# ### Import necessary Libraries

# In[ ]:

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
print ("Your credentails:")
print ("CLIENT_ID: " + CLIENT_ID)
print ("CLIENT_SECRET:" + CLIENT_SECRET)


#  

# #### Convert the address of MassChallenge to its latitude and longitude equivalence

# In[ ]:

address = "21 Drydock Ave, Boston, MA"
geolocator = Nominatim()
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print (latitude, longitude)


#    

# <a id="item1"></a>

# ## 1. Search for a specific venue category
# > `https://api.foursquare.com/v2/venues/`**search**`?client_id=`**CLIENT_ID**`&client_secret=`**CLIENT_SECRET**`&ll=`**LATITUDE**`,`**LONGITUDE**`&v=`**VERSION**`&query=`**QUERY**`&radius=`**RADIUS**`&limit=`**LIMIT**

# #### Define a search query for Italian restaurants

# In[ ]:

search_query = "Coffee Shops"
print (search_query + " .... OK!")


# #### Define the corresponding URL

# In[ ]:

radius = 2000
url="https://api.foursquare.com/v2/venues/search?client_id={}&client_secret={}&ll={},{}&v={}&query={}&radius={}&limit={}".format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, search_query, radius, LIMIT)
url


# #### Send the GET Request and examine the results

# In[ ]:

results = requests.get(url).json()
results


# #### Get relevant part of JSON and transform it into a *pandas* dataframe

# In[ ]:

# assign relevant part of JSON to venues
venues = results["response"]["venues"]

# tranform venues into a dataframe
dataframe = json_normalize(venues)
dataframe.head()


# #### Define information of interest and filter dataframe

# In[ ]:

# keep only columns that include venue name, url, and anything that is associated with location
filtered_columns = ['name', 'url', 'categories', 'verified'] + [col for col in dataframe.columns if col.startswith('location.')] + ['id']
dataframe_filtered = dataframe.ix[:, filtered_columns]

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

# <a id="item3"></a>

# ## 3. Search a Foursquare User
# > `https://api.foursquare.com/v2/users/`**USER_ID**`?client_id=`**CLIENT_ID**`&client_secret=`**CLIENT_SECRET**`&v=`**VERSION**

# ### Define URL, send GET request and display features associated with user

# In[ ]:

user_id="35607697" # user ID with most agree counts and complete profile

url="https://api.foursquare.com/v2/users/{}?client_id={}&client_secret={}&v={}".format(user_id, CLIENT_ID, CLIENT_SECRET, VERSION) # define URL

# send GET request
results = requests.get(url).json()
user_data = results["response"]["user"]

# display features associated with user
user_data.keys()


# In[ ]:

print ("First Name: " + user_data["firstName"])
print ("Last Name: " + user_data["lastName"])
print ("Home City: " + user_data["homeCity"])


# #### How many tips has this user submitted?

# In[ ]:

user_data["tips"]


# ### Get User's tips

# In[ ]:

# define tips URL
url="https://api.foursquare.com/v2/users/{}/tips?client_id={}&client_secret={}&v={}&limit={}".format(user_id, CLIENT_ID, CLIENT_SECRET, VERSION, limit)

# send GET request and get user's tips
results = requests.get(url).json()
tips = results["response"]["tips"]["items"]

# format column width
pd.set_option('display.max_colwidth', -1)

tips_df = json_normalize(tips)

# filter columns
filtered_columns = ["text", "agreeCount", "disagreeCount", "id"]
tips_filtered = tips_df.ix[:, filtered_columns]

# display user's tips
tips_filtered


# #### Let's get the venue for the tip with the greatest number of agree counts

# In[ ]:

tip_id = "5050a360e4b0dd1afe04855e" # tip id

# define URL
url = "http://api.foursquare.com/v2/tips/{}?client_id={}&client_secret={}&v={}".format(tip_id, CLIENT_ID, CLIENT_SECRET, VERSION)

# send GET Request and examine results
result = requests.get(url).json()
print (result["response"]["tip"]["venue"]["name"])
print (result["response"]["tip"]["venue"]["location"])


# ### Get User's friends

# In[ ]:

user_friends = json_normalize(user_data["friends"]["groups"][0]["items"])
user_friends


# ### Retrieve the User's Profile Image

# In[ ]:

user_data


# In[ ]:

# 1. grab prefix of photo
# 2. grab suffix of photo
# 3. concatenate them using the image size  
Image(url="https://igx.4sqi.net/img/user/300x300/HFSZXA4SW105O1CW.jpg")


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


# create a feature group for popular venues around Barrington Coffee and add it to the map
popular_venues = folium.map.FeatureGroup()
for lat, lng, in zip(dataframe_filtered.lat, dataframe_filtered.lng):
    popular_venues.add_child(
        folium.features.CircleMarker(
            [lat, lng],
            radius=5,
            color="blue",
            fill_color="blue",
            fill_opacity=0.6)
        )
venues_map.add_child(popular_venues)


# add labels to each point on the map
latitudes_list = list(dataframe_filtered.lat) + [latitude]
longitudes_list = list(dataframe_filtered.lng) + [longitude]
labels = list(dataframe_filtered.name) + ["Barrington Coffee"]
venue_categories = list(dataframe_filtered.categories) + ["Coffee Shop"]

#for lat, lng, label, category in zip(latitudes_list, longitudes_list, labels, venue_categories):
    # popup_text = label + ", " + category
#    folium.Marker([lat, lng], popup=popup_text).add_to(venues_map)

# display map
venues_map


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


    # create a feature group for popular venues around Barrington Coffee and add it to the map
    trending_venues = folium.map.FeatureGroup()
    for lat, lng, in zip(trending_venues_df["location.lat"], trending_venues_df["location.lng"]):
        trending_venues.add_child(
            folium.features.CircleMarker(
                [lat, lng],
                radius=5,
                color="blue",
                fill_color="blue",
                fill_opacity=0.6
            )
        )
    venues_map.add_child(trending_venues)


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
venues_map


# <a id="item6"></a>

#    

# #### Interested in learning how to build a chatbot around location-based data? 
# Make sure to attend my tutorial session on building chatbots. Amazing free course on chatbots available: http://cocl.us/CBF_Boston_Chatbot

# # <center>Thank you for attending!
