# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 17:12:24 2020

@author: Roman
"""
###############################################################################
# import library
###############################################################################
import requests # library to handle requests
import pandas as pd # library for data analsysis
import folium
import pyproj
import math
import json
from shapely.geometry import shape, Point


###############################################################################
###############################################################################
# Visialize a map of Moscow Borough
###############################################################################
###############################################################################

# Load previously saved dataframe
Moscow_Borough_df = pd.read_csv("data\Moscow_Borough_df.csv")
mo_geojson = 'data\mo.geojson'

# Moscow latitude and longitude values
Moscow_lat= 55.7504461
Moscow_lng= 37.6174943

# create map and display it
Moscow_map = folium.Map(location=[Moscow_lat, Moscow_lng], zoom_start=10)

# Generate choropleth map with Borough Population
Moscow_map.choropleth(
    geo_data=mo_geojson,
    data=Moscow_Borough_df,
    name='Population Density',
    columns=['Borough_Name', 'Borough_Population'],
    key_on='feature.properties.NAME',
    fill_color='YlOrRd', 
    fill_opacity=0.7, 
    line_opacity=0.2,
    legend_name='Borough Population in Moscow City'
)

folium.LayerControl().add_to(Moscow_map)

# Add Borougs center as markers to Moscow map 
for Borough_Name, lat, lng, Borough_Population in zip(Moscow_Borough_df['Borough_Name'], Moscow_Borough_df['Latitude'], Moscow_Borough_df['Longitude'], Moscow_Borough_df['Borough_Population']):
    folium.features.CircleMarker(
        [lat, lng],
        radius=5, # define how big you want the circle markers to be
        color='yellow',
        fill=True,
        #popup='{}, Москва, Россия ({:})'.format(Borough_Name, Borough_Population),
        popup=folium.Popup('{}, Москва, Россия ({:})'.format(Borough_Name, Borough_Population), parse_html=True),
        fill_color='blue',
        fill_opacity=0.6
    ).add_to(Moscow_map)

    folium.Circle([lat, lng], radius=1000, color='blue', fill=False).add_to(Moscow_map)

# display map
Moscow_map

#==============================================================================
# Display a circle of 28 000 meter in radius, wich cover all the Moscow Boroughs in my reseach
#==============================================================================
Moscow_Circle_lat= 55.7398697
Moscow_Circle_lng= 37.5365271
Circle_radius=28000
folium.Circle([Moscow_Circle_lat,Moscow_Circle_lng], radius=Circle_radius, color='blue', fill=False).add_to(Moscow_map)

# display map
Moscow_map




###############################################################################
###############################################################################
### Obtain Moscow Boroughs venues
# Create a grid of area candidates, equaly spaced, centered around circle center and within 28 km
# Create our grid of locations in Cartesian 2D coordinate system which allows us to calculate distances in meters
###############################################################################
###############################################################################


###############################################################################
# Define functions to convert between WGS84 spherical coordinate system (latitude/longitude degrees) 
# and UTM Cartesian coordinate system (X/Y coordinates in meters)
###############################################################################
def lonlat_to_xy(lon, lat):
    proj_latlon = pyproj.Proj(proj='latlong',datum='WGS84')
    proj_xy = pyproj.Proj(proj="utm", zone=33, datum='WGS84')
    xy = pyproj.transform(proj_latlon, proj_xy, lon, lat)
    return xy[0], xy[1]

def xy_to_lonlat(x, y):
    proj_latlon = pyproj.Proj(proj='latlong',datum='WGS84')
    proj_xy = pyproj.Proj(proj="utm", zone=33, datum='WGS84')
    lonlat = pyproj.transform(proj_xy, proj_latlon, x, y)
    return lonlat[0], lonlat[1]

def calc_xy_distance(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx*dx + dy*dy)

print('Coordinate transformation check')
print('-------------------------------')
print('Moscow center longitude={}, latitude={}'.format(Moscow_lat, Moscow_lng))
x, y = lonlat_to_xy(Moscow_lat, Moscow_lng)
print('Moscow center UTM X={}, Y={}'.format(x, y))
lo, la = xy_to_lonlat(x, y)
print('Moscow center longitude={}, latitude={}'.format(lo, la))


###############################################################################
# Define a function to create a hexagonal grid of cells
###############################################################################
def create_hexagonal_grid (lat, lon, distance_limit, cell_radius):
    center_x, center_y = lonlat_to_xy(lon, lat) 

    # create a hexagonal grid of cells: we offset every other row, and adjust vertical row 
    # spacing so that every cell center is equally distant from all it's neighbors.

    k = math.sqrt(3) / 2 # Vertical offset for hexagonal grid cells
    x_min = center_x - distance_limit
    x_step = cell_radius *2 
    y_min = center_y - distance_limit - (int((distance_limit/cell_radius+1)/k)*k*(cell_radius *2) - (distance_limit*2))/2
    y_step = cell_radius *2  * k 
    
    latitudes = []
    longitudes = []
    cells_id = []
    distances_from_center = []
    xs = []
    ys = []
    for i in range(0, int((distance_limit/cell_radius+1)/k)):
        y = y_min + i * y_step
        x_offset = cell_radius if i%2==0 else 0
        for j in range(0, int(distance_limit/cell_radius+1)):
            x = x_min + j * x_step + x_offset
            distance_from_center = calc_xy_distance(center_x, center_y, x, y)
            if (distance_from_center <= (distance_limit+1)):
                lon, lat = xy_to_lonlat(x, y)
                latitudes.append(lat)
                longitudes.append(lon)
                cells_id.append('{},{}'.format(lat, lon))
                distances_from_center.append(distance_from_center)
                xs.append(x)
                ys.append(y)

    # Create and return new Pandas dataframe with all cells
    return pd.DataFrame(list(zip(cells_id, latitudes, longitudes)), columns =['Cell_id', 'Cell_Latitude', 'Cell_Longitude']) 


###############################################################################
# Folium library have a problem to visualize more then 1000 item in single map  
# So for test purpose create a grid of area candidates, equally spaced, centered around circle center and within 10 km and visualize it
###############################################################################
distance_limit = 10000
cell_radius = 300

Moscow_Circle_lat= 55.7398697
Moscow_Circle_lng= 37.5365271    

Moscow_cells_df =  create_hexagonal_grid(Moscow_Circle_lat, Moscow_Circle_lng, distance_limit, cell_radius)
print(Moscow_cells_df.shape[0], 'candidate neighborhood centers generated.')

# Visualize circle center location and candidate neighborhood centers
Moscow_cell_map = folium.Map(location=[Moscow_Circle_lat, Moscow_Circle_lng], zoom_start=12)

# Generate choropleth map with Borough Population
Moscow_cell_map.choropleth(
    geo_data=mo_geojson,
    data=Moscow_Borough_df,
    name='Population Density',
    columns=['Borough_Name', 'Borough_Population'],
    key_on='feature.properties.NAME',
    fill_color='YlOrRd', 
    fill_opacity=0.7, 
    line_opacity=0.2,
    legend_name='Borough Population in Moscow City'
)

# Add grid of area candidates
for lat, lng in zip(Moscow_cells_df['Cell_Latitude'], Moscow_cells_df['Cell_Longitude']):
    folium.Circle([lat, lng], radius=cell_radius, color='blue', fill=False).add_to(Moscow_cell_map)

Moscow_cell_map




###############################################################################
# Create a grid of area candidates, equaly spaced, centered around circle center and within 28 000 m
###############################################################################
distance_limit = 28000
cell_radius = 300

Moscow_Circle_lat= 55.7398697
Moscow_Circle_lng= 37.5365271    

Moscow_cells_df =  create_hexagonal_grid(Moscow_Circle_lat, Moscow_Circle_lng, distance_limit, cell_radius)
Moscow_cells_df.index = Moscow_cells_df['Cell_id']
print(Moscow_cells_df.shape[0], 'candidate neighborhood centers generated.')

# Save dataframe
Moscow_cells_df.to_csv("data\Moscow_cells_df.csv", index = False)



###############################################################################
###############################################################################
### Explore the neighborhood in the grid
###############################################################################
###############################################################################

# Foursquare API have a certain limitation for API call in one day to explore venues
# So I have to divide cells dataset into subset and call Foursquare API for several days

#==============================================================================
# Define some supplemenatry functions
#==============================================================================
def format_address(location):
    address = ', '.join(location['formattedAddress'])
    address = address.replace(', Россия', '')
    address = address.replace(', Москва', '')
    return address

def get_categories(categories):
    return [(cat['name'], cat['id']) for cat in categories]

def get_venues_near_location(lat, lon, client_id, client_secret, radius=300, limit=100):
    url = 'https://api.foursquare.com/v2/venues/explore?client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
        client_id, client_secret, version, lat, lon, radius, limit)
    #print(url)
    results = requests.get(url).json()['response']['groups'][0]['items']
    venues = [(item['venue']['id'],
               item['venue']['name'],
               get_categories(item['venue']['categories']),
               item['venue']['location']['lat'], 
               item['venue']['location']['lng'],
               format_address(item['venue']['location']),
               item['venue']['location']['distance']) for item in results]        
    return venues


#==============================================================================
# Declare Moscow venues dataframe, intially empty
#==============================================================================
Moscow_venues_df = pd.DataFrame()

# Declare dataframe to store already explored cells
Moscow_cells_explored_df = pd.DataFrame(columns=['Cell_id'])

#==============================================================================
# Define Foursquare Credentials and Version
#==============================================================================
client_id = 'KO15SRHFPF3BBN5XUCEYLDU3ROGESHFXRWPK1Q32QSIDFFBM'
client_secret = 'POBZ0ULK51ARULZXVMOZMAVRCEUWOSXX5HD2QLERC43JCUEK'
version = '20180604'

limit = 100
# Using radius=cell_radius+50 to make sure we have overlaps/full coverage so we don't miss any venues
explore_radius = cell_radius+50

#==============================================================================
# Proccess all cells if it not yet processed
# **!! It takes about 4 hours in several days to compleet so comment it and load previously saved dataframe !!**
#==============================================================================
# Prepare dataset with cell which is not yet have been processed. 1000 record in one batch
Moscow_cells_for_explore_df = Moscow_cells_df[~Moscow_cells_df['Cell_id'].isin(Moscow_cells_explored_df['Cell_id'])].head(1000)

# Itterate through all cell prepared for explore
for index, lat, lng in zip(Moscow_cells_for_explore_df.index, Moscow_cells_for_explore_df['Cell_Latitude'], Moscow_cells_for_explore_df['Cell_Longitude']):
    print('Explore Cell {}'.format(index), end='')
    
    try:
        venues = get_venues_near_location(lat, lng, client_id, client_secret, radius=explore_radius, limit=limit)
        print(' - found {} veenues'.format(len(venues)))

        # if found any venues add they to dataframe
        if (len(venues) > 0):
            Moscow_venues_df = Moscow_venues_df.append([(index, lat, lng, v[0], v[1], v[2], v[3], v[4], v[5], v[6], "") for v in venues], ignore_index=True)

        # save cell id as already explored
        Moscow_cells_explored_df.loc[index] = index 
        
    except Exception as err:
        print(err)
        pass

Moscow_cells_explored_df.to_csv("data\Moscow_cells_explored_df.csv", index = False)
Moscow_venues_df.to_csv("data\Moscow_venues_df_raw.csv", index = False)



###############################################################################
###############################################################################
### Clear Venues dataset
###############################################################################
###############################################################################

#==============================================================================
# Load previously saved dataframe
#==============================================================================
Moscow_venues_df = pd.read_csv("data\Moscow_venues_df_raw.csv")

# Columns of result dataset
column_names = ['Cell_id', 'Cell_Latitude', 'Cell_Longitude', 'Venue_Id', 'Venue_Name', 
              'Venue_All_Categories','Venue_Latitude', 'Venue_Longitude', 'Venue_Location', 'Venue_Distance', 'Borough_Name'] 

# Rename columns
Moscow_venues_df.columns=column_names

# Take a look at the dataframe
print('Take a look at the dataframe')
print(Moscow_venues_df.head())
print(Moscow_venues_df.shape)

print('Take a look at the dataframe data types')
print(Moscow_venues_df.dtypes)



#==============================================================================
# Delete duplicate venues
#==============================================================================
# Count duplicates venues
print('Unique Venues {} of {}'.format(Moscow_venues_df['Venue_Id'].nunique(), Moscow_venues_df['Venue_Id'].shape[0]))

# Drop duplicates
print('Delete duplicates')
Moscow_venues_df.drop_duplicates(subset ="Venue_Id", keep = 'first', inplace = True) 

# Reset index
Moscow_venues_df.reset_index(inplace = True) 

# Take a look at the dataframe
print('Take a look at the dataframe shape')
print(Moscow_venues_df.shape)

#==============================================================================
# Get first category for each Venue
#==============================================================================
#Moscow_venues_df['Venue_Category_Name'] = Moscow_venues_df['Venue_All_Categories'].apply(lambda x: x[0][0])
#Moscow_venues_df['Venue_Category_Id'] = Moscow_venues_df['Venue_All_Categories'].apply(lambda x: x[0][1])

# Get first category for each Venue
Moscow_venues_df['Venue_Category_Name'] = Moscow_venues_df['Venue_All_Categories'].apply(lambda x: x.strip('[()]').split(', ')[0].strip("'"))
Moscow_venues_df['Venue_Category_Id'] = Moscow_venues_df['Venue_All_Categories'].apply(lambda x: x.strip('[()]').split(', ')[1].strip("'"))

print('Take a look at the Venue Category')
print(Moscow_venues_df[['Venue_Name', 'Venue_Category_Name', 'Venue_Category_Id']].head())


#==============================================================================
# Bind each venue to Moscow Boroughs in which borders they were placed
#==============================================================================

# load GeoJSON file with Boroughs and create geometry shape
with open(mo_geojson) as json_file:
    geojson_data = json.loads(json_file.read())

    
# Itterate through all Borough shape and find all Venues, that is placed in it
for feature in geojson_data['features']:
    # shape of the Borough
    polygon = shape(feature['geometry'])
    borough_name = feature['properties']['NAME']
    
    print('Process borough "{}"'.format(borough_name), end='')
    
    # Itterate throug all Venues
    for index, name, lat, lng in zip(Moscow_venues_df.index, Moscow_venues_df['Venue_Name'], Moscow_venues_df['Venue_Latitude'], Moscow_venues_df['Venue_Longitude']):
        # construct point based on lon/lat
        point = Point(lng, lat)
    
        if polygon.contains(point):
            print('.', end='')
            Moscow_venues_df.loc[index, 'Borough_Name'] = borough_name
    
    print('done')

print('Take a look at the Venue of some Boroughs')
print(Moscow_venues_df[['Venue_Name', 'Venue_Category_Name', 'Borough_Name']].head(10))


#==============================================================================
# Delete Venues that placed outside of the Moscow Boroughs
#==============================================================================
# Calcuate Venue placed outside Moscow Borough
print('{} Venue placed outside Moscow Boroughs'.format(Moscow_venues_df[~Moscow_venues_df['Borough_Name'].isin(Moscow_Borough_df['Borough_Name'])].shape[0]))

# Delete venues with is not in our scope of Moscow Boroughs
print('Delete Venue placed outside Moscow Boroughs')
Moscow_venues_df.drop(Moscow_venues_df[~Moscow_venues_df['Borough_Name'].isin(Moscow_Borough_df['Borough_Name'])].index, inplace=True)

# Reset index
Moscow_venues_df.reset_index(inplace = True) 

# Take a look at the dataframe
print('Take a look at the dataframe shape')
print(Moscow_venues_df.shape)

# Save result dataset with Venues 
Moscow_venues_df.to_csv("data\Moscow_venues_df.csv", index = False)



###############################################################################
# Visialize a map of some Moscow Boroughs with venues in it
###############################################################################
# Moscow latitude and longitude values
Moscow_subset_lat = Moscow_Borough_df[Moscow_Borough_df['Borough_Name'] == 'Бирюлёво Западное']['Latitude'].iloc[0]
Moscow_subset_lng = Moscow_Borough_df[Moscow_Borough_df['Borough_Name'] == 'Бирюлёво Западное']['Longitude'].iloc[0]

# create map and display it
Moscow_map = folium.Map(location=[Moscow_subset_lat, Moscow_subset_lng], zoom_start=12)

# generate choropleth map
Moscow_map.choropleth(
    geo_data=mo_geojson,
    data=Moscow_Borough_df,
    name='Population Density',
    columns=['Borough_Name', 'Borough_Population'],
    key_on='feature.properties.NAME',
    fill_color='YlOrRd', 
    fill_opacity=0.7, 
    line_opacity=0.2,
    legend_name='Borough Population in Moscow City'
)

#==============================================================================
# Create Venues subset for some Boroughs
#==============================================================================
Moscow_venues_subset = Moscow_venues_df[Moscow_venues_df['Borough_Name'].isin(['Орехово-Борисово Северное', 'Чертаново Южное', 'Южное Бутово'])]

#==============================================================================
# Add markers to map for venues
#==============================================================================
for Venue_name, lat, lng in zip(Moscow_venues_subset['Venue_Name'], Moscow_venues_subset['Venue_Latitude'], Moscow_venues_subset['Venue_Longitude']):
    folium.features.CircleMarker(
        [lat, lng],
        radius=5, # define how big you want the circle markers to be
        color='yellow',
        fill=True,
        popup=folium.Popup('{}'.format(Venue_name), parse_html=True),
        fill_color='blue',
        fill_opacity=0.6
    ).add_to(Moscow_map)


# display map
Moscow_map
