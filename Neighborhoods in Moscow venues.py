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
import sys
import json
from shapely.geometry import shape, Point


###############################################################################
# Load previously prepeared dataset 
###############################################################################
Moscow_Borough_df = pd.read_csv("Moscow_Borough_df.csv")
mo_geojson = 'mo.geojson'


###############################################################################
# Visialize a map of Moscow Borough
###############################################################################
# Moscow latitude and longitude values
Moscow_lat= 55.7504461
Moscow_lng= 37.6174943

# create map and display it
Moscow_map = folium.Map(location=[Moscow_lat, Moscow_lng], zoom_start=10)

#==============================================================================
# Generate choropleth map with Borough Population
#==============================================================================
Moscow_map.choropleth(
    geo_data=mo_geojson,
    data=Moscow_Borough_df,
    name='Population Density',
    columns=['Borough_Name', 'Borough_Population'],
    key_on='feature.properties.NAME',
    fill_color='YlOrRd', 
    fill_opacity=0.7, 
    line_opacity=0.2,
    legend_name='Borough in Moscow City'
)

folium.LayerControl().add_to(Moscow_map)

#==============================================================================
# Add borough center as markers to Moscow map 
#==============================================================================
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


#==============================================================================
# display map
#==============================================================================
Moscow_map

#==============================================================================
# As we can see, use center of the brough for searching venues is quite useless as eache borough have very sophisticated shape 
# Api для поиска поддерживает поиск в радиусе до 1000 м
# нам же необходимо искать в радиусе 21 000 м от центра Москвы
#==============================================================================

# Display a circle of 21 000 meter in diametre
folium.Circle([Moscow_lat, Moscow_lng], radius=21000, color='blue', fill=False).add_to(Moscow_map)

# display map
Moscow_map



###############################################################################
# Create a grid of area candidates, equaly spaced, centered around city center and within 20km
# Create our grid of locations in Cartesian 2D coordinate system which allows us to calculate distances in meters
###############################################################################

#==============================================================================
# Create functions to convert between WGS84 spherical coordinate system (latitude/longitude degrees) 
# and UTM Cartesian coordinate system (X/Y coordinates in meters)
#==============================================================================
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



#==============================================================================
# create a hexagonal grid of cells: we offset every other row, and adjust vertical row 
# spacing so that every cell center is equally distant from all it's neighbors.
#==============================================================================

distance_limit = 21000
cell_radius = 300

# City center in Cartesian coordinates
Moscow_center_x, Moscow_center_y = lonlat_to_xy(Moscow_lng, Moscow_lat) 

k = math.sqrt(3) / 2 # Vertical offset for hexagonal grid cells
x_min = Moscow_center_x - distance_limit
x_step = cell_radius *2 
y_min = Moscow_center_y - distance_limit - (int((distance_limit/cell_radius+1)/k)*k*(cell_radius *2) - (distance_limit*2))/2
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
        distance_from_center = calc_xy_distance(Moscow_center_x, Moscow_center_y, x, y)
        if (distance_from_center <= (distance_limit+1)):
            lon, lat = xy_to_lonlat(x, y)
            latitudes.append(lat)
            longitudes.append(lon)
            cells_id.append('{},{}'.format(lat, lon))
            distances_from_center.append(distance_from_center)
            xs.append(x)
            ys.append(y)

# Create new Pandas dataframe with all cells
Moscow_cells_df = pd.DataFrame(list(zip(cells_id, latitudes, longitudes)), columns =['Cell_id', 'Cell_Latitude', 'Cell_Longitude']) 
Moscow_cells_df.insert(3, "Is_Venue_Explore", False) 
Moscow_cells_df.index = Moscow_cells_df['Cell_id']
            
print(len(latitudes), 'candidate neighborhood centers generated.')


#==============================================================================
# Visualize city center location and candidate neighborhood centers
#==============================================================================
Moscow_cell_map = folium.Map(location=[Moscow_lat, Moscow_lng], zoom_start=10)
for lat, lon in zip(Moscow_cells_df['Cell_Latitude'], Moscow_cells_df['Cell_Longitude']):
    folium.Circle([lat, lon], radius=cell_radius, color='blue', fill=False).add_to(Moscow_cell_map)
Moscow_cell_map



###############################################################################
# Explore the neighborhood in Moscow for eache cell
###############################################################################

#==============================================================================
# Define Foursquare Credentials and Version
#==============================================================================
client_id = 'KO15SRHFPF3BBN5XUCEYLDU3ROGESHFXRWPK1Q32QSIDFFBM'
client_secret = 'POBZ0ULK51ARULZXVMOZMAVRCEUWOSXX5HD2QLERC43JCUEK'
version = '20180604'
limit = 100

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

#==============================================================================
# Proccess all cells if it not yet processed
#==============================================================================
for index, lat, lng, is_explore in zip(Moscow_cells_df.index, Moscow_cells_df['Cell_Latitude'], Moscow_cells_df['Cell_Longitude'],  Moscow_cells_df['Is_Venue_Explore']):
    print(index)

    # Using radius=cell_radius+50 to make sure we have overlaps/full coverage so we don't miss any venues
    if not is_explore:
        try:
            venues = get_venues_near_location(lat, lng, client_id, client_secret, radius=cell_radius+50, limit=limit)
            
            Moscow_venues_df = Moscow_venues_df.append([(
                index, 
                lat, 
                lng, 
                v[0], 
                v[1], 
                v[2], 
                v[3], 
                v[4], 
                v[5], 
                v[6], 
                ""
                ) for v in venues], ignore_index=True)
              
            Moscow_cells_df.loc[index, 'Is_Venue_Explore'] = True

           
        except:
            print("Unexpected error:", sys.exc_info()[0])
            pass

#==============================================================================
# Delete duplicate venues
#==============================================================================
# Columns of result dataset
column_names = ['Cell_id', 
              'Cell_Latitude', 
              'Cell_Longitude', 
              'Venue_Id', 
              'Venue_Name', 
              'Venue_All_Categories',
              'Venue_Latitude', 
              'Venue_Longitude', 
              'Venue_Location', 
              'Venue_Distance', 
              'Borough_Name'] 

# Rename columns
Moscow_venues_df.columns=column_names

# Take a look at the dataframe
print(Moscow_venues_df.head())
print(Moscow_venues_df.shape)

# Count duplicates venues
print('Unique Venues {} of {}'.format(Moscow_venues_df['Venue_Id'].nunique(), Moscow_venues_df['Venue_Id'].shape[0]))

# Drop duplicates
Moscow_venues_df.drop_duplicates(subset ="Venue_Id", keep = 'first', inplace = True) 

# Get first category for each Venue
Moscow_venues_df['Venue_Category_Name'] = Moscow_venues_df['Venue_All_Categories'].apply(lambda x: x[0][0])
Moscow_venues_df['Venue_Category_Id'] = Moscow_venues_df['Venue_All_Categories'].apply(lambda x: x[0][1])

Moscow_venues_df.to_csv("Moscow_venues_df.csv", index = False)


###############################################################################
# Place eache Venue inside the corresponding borough shape
###############################################################################
#==============================================================================
# load GeoJSON file with Boroughs and create geometry shape
#==============================================================================
with open(mo_geojson) as json_file:
    geojson_data = json.loads(json_file.read())
    
#==============================================================================
# Itterate through all Borough shape and find all Venues, that is placed in it
#==============================================================================
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


###############################################################################
# Delete Venues that placed outside of the Moscow Borough
###############################################################################
# Calcuate Venue placed outside Moscow Borough
print('{} Venue placed outside Moscow Borough'.format(Moscow_venues_df[~Moscow_venues_df['Borough_Name'].isin(Moscow_Borough_df['Borough_Name'])].shape[0]))

# Delete venues with is not in our scope of Moscow Boroughs
Moscow_venues_df.drop(Moscow_venues_df[~Moscow_venues_df['Borough_Name'].isin(Moscow_Borough_df['Borough_Name'])].index, inplace=True)

# Save result dataset with Venues 
Moscow_venues_df.to_csv("Moscow_venues_df.csv", index = False)

# Drop these Venues 
#Moscow_venues_df.drop(Moscow_venues_df[Moscow_venues_df['Borough_Name'] == ''].index, inplace=True)

# Load polygon for eache borough
#Moscow_polygon_df = pd.DataFrame([(feature['properties']['NAME'], shape(feature['geometry'])) for feature in geojson_data['features']])  
# Rename cloumns 
#Moscow_polygon_df.columns=["Borough_Name", "Borough_Polygon"]



###############################################################################
# Visialize a map of some Moscow Boroughs with venues in it
###############################################################################
# Moscow latitude and longitude values
Moscow_subset_lat = Moscow_Borough_df[Moscow_Borough_df['Borough_Name'] == 'Орехово-Борисово Северное']['Latitude'].iloc[0]
Moscow_subset_lng = Moscow_Borough_df[Moscow_Borough_df['Borough_Name'] == 'Орехово-Борисово Северное']['Longitude'].iloc[0]

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
# Add markers to map for borough 
#==============================================================================
# Create Venues subset for some venue
Moscow_venues_subset = Moscow_venues_df[Moscow_venues_df['Borough_Name'].isin(['Орехово-Борисово Северное', 'Братеево', 'Нагатинский Затон'])]

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
