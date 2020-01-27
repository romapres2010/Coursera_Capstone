# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 17:12:24 2020

@author: Roman
"""
###############################################################################
# import library
###############################################################################
import pandas as pd # library for data analsysis
import folium
from folium.plugins import HeatMap
import matplotlib.cm as cm
import matplotlib.colors as colors
import numpy as np # library to handle data in a vectorized manner
from sklearn.preprocessing import StandardScaler


###############################################################################
# Load previously prepeared dataset 
###############################################################################
Moscow_Borough_df = pd.read_csv("Moscow_Borough_df.csv")
Moscow_venues_df = pd.read_csv("Moscow_venues_df.csv")
mo_geojson = 'mo.geojson'


###############################################################################
# Analyze Neighborhood
###############################################################################
# How many unique venue categories 
print('There are {} unique categories.'.format(len(Moscow_venues_df['Venue_Category_Name'].unique())))

# Named all subcategories of "Gym / Fitness Center" from foursquare API
#gym_categories = ['Gym / Fitness Center','Boxing Gym','Climbing Gym','Cycle Studio','Gym Pool','Gymnastics Gym','Gym','Martial Arts Dojo','Outdoor Gym','Pilates Studio','Track','Weight Loss Center','Yoga Studio']
gym_categories = ['Gym / Fitness Center','Gym']
#gym_categories = ['Pilates Studio','Yoga Studio']
#gym_categories = ['Gym / Fitness Center','Boxing Gym','Climbing Gym','Cycle Studio','Gymnastics Gym','Gym','Martial Arts Dojo','Outdoor Gym','Pilates Studio','Weight Loss Center','Yoga Studio']

# Make venues subset of all subcategories of "Gym / Fitness Center"
Moscow_gym_venues_df = Moscow_venues_df[Moscow_venues_df['Venue_Category_Name'].isin(gym_categories)]

# Make a copy ofthen dataframe
Moscow_gym_venues_df.to_csv("Moscow_gym_venues_df.csv", index = False)

# Количество фитнес центров по районам
Moscow_gym_count_df = Moscow_gym_venues_df.groupby(['Borough_Name'],as_index=False).count()[['Borough_Name', 'Venue_Id']]

# переименуем колонки
Moscow_gym_count_df.columns = ['Borough_Name', 'Gym_Count']

# сольем датасеты
Moscow_Borough_Gym_df = pd.merge(left=Moscow_Borough_df, right=Moscow_gym_count_df, how='left', left_on='Borough_Name', right_on='Borough_Name', )

# количество жителей на один фитнес центр
Moscow_Borough_Gym_df['Borough_Population_Per_Gym'] = Moscow_Borough_Gym_df['Borough_Population'] / Moscow_Borough_Gym_df['Gym_Count']

# сохраним датасет
Moscow_Borough_Gym_df.to_csv("Moscow_Borough_Gym_df.csv", index = False)



###############################################################################
# Visialize a Heatmap of Gym in Moscow
###############################################################################
# Moscow latitude and longitude values
Moscow_lat= 55.7504461
Moscow_lng= 37.6174943

# create map
Moscow_map = folium.Map(location=[Moscow_lat, Moscow_lng], zoom_start=11)

# List comprehension to make out list of lists
heat_data = [[row['Venue_Latitude'], row['Venue_Longitude']] for index, row in Moscow_gym_venues_df.iterrows()]

# Add HeatMap
HeatMap(heat_data).add_to(Moscow_map)
folium.GeoJson(mo_geojson).add_to(Moscow_map)

# display map
Moscow_map



###############################################################################
# Analyze Moscow Bogouhs by categories
###############################################################################

#==============================================================================
# one hot encoding
#==============================================================================
Moscow_onehot = pd.get_dummies(Moscow_gym_venues_df[['Venue_Category_Name']], prefix="", prefix_sep="")
# add Borough Name  column back to dataframe
Moscow_onehot['Borough_Name'] = Moscow_gym_venues_df['Borough_Name'] 

# move neighborhood column to the first column
fixed_columns = [Moscow_onehot.columns[-1]] + list(Moscow_onehot.columns[:-1])
Moscow_onehot = Moscow_onehot[fixed_columns]

#Examine the new dataframe size
Moscow_onehot.head()
print (Moscow_onehot.shape)


#==============================================================================
# Group rows by Borough and by taking the mean of the frequency of occurrence of each category
#==============================================================================
Moscow_grouped_df = Moscow_onehot.groupby('Borough_Name').mean().reset_index()
#Examine the new dataframe size
Moscow_grouped_df.head()
print (Moscow_grouped_df.shape)


#==============================================================================
# Print each Borough along with the top 5 most common venues
#==============================================================================
num_top_venues = 5

for hood in Moscow_grouped_df['Borough_Name']:
    print("----"+hood+"----")
    temp = Moscow_grouped_df[Moscow_grouped_df['Borough_Name'] == hood].T.reset_index()
    temp.columns = ['venue','freq']
    temp = temp.iloc[1:]
    temp['freq'] = temp['freq'].astype(float)
    temp = temp.round({'freq': 2})
    print(temp.sort_values('freq', ascending=False).reset_index(drop=True).head(num_top_venues))
    print('\n')




###############################################################################
# Cluster Boroughs venue categories using k-means with elbow method
###############################################################################
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist 
import matplotlib.pyplot as plt 

#==============================================================================
# Define the function clustering using k-means with elbow visualizations
#==============================================================================
def KMeans_elbow(X, max_clusters=10):
   
    #==============================================================================
    # Building the clustering model and calculating the values of the Distortion and Inertia
    #==============================================================================
    distortions = [] 
    inertias = [] 
    mapping1 = {} 
    mapping2 = {} 
    K = range(1,max_clusters) 
    
     
    for k in K: 
        #Building and fitting the model 
        kmeans = KMeans(init = "k-means++", n_clusters=k, random_state=0, n_init = 12)
        kmeans.fit(X) 
          
        distortions.append(sum(np.min(cdist(X, kmeans.cluster_centers_, 'euclidean'), axis=1)) / X.shape[0]) 
        inertias.append(kmeans.inertia_) 
      
        mapping1[k] = sum(np.min(cdist(X, kmeans.cluster_centers_, 'euclidean'), axis=1)) / X.shape[0] 
        mapping2[k] = kmeans.inertia_ 
    
    
    #==============================================================================
    # Visualizing the results using the different values of Distortion
    #==============================================================================
    print('Visualizing the results using the different values of Distortion')
    for key,val in mapping1.items(): 
        print(str(key)+' : '+str(val))
    
    plt.plot(K, distortions, 'bx-') 
    plt.xlabel('Values of K') 
    plt.ylabel('Distortion') 
    plt.title('The Elbow Method using Distortion') 
    plt.show() 
    
    #==============================================================================
    # Visualizing the results using the different values of Inertia
    #==============================================================================
    print('Visualizing the results using the different values of Inertia')
    for key,val in mapping2.items(): 
        print(str(key)+' : '+str(val)) 
        
    plt.plot(K, inertias, 'bx-') 
    plt.xlabel('Values of K') 
    plt.ylabel('Inertia') 
    plt.title('The Elbow Method using Inertia') 
    plt.show() 


#==============================================================================
# Prepare the dataset and calculate result ncluster value using elbow method
#==============================================================================
X = Moscow_grouped_df.drop('Borough_Name', 1)
#X = StandardScaler().fit_transform(X)
KMeans_elbow(X, 10)

#==============================================================================
# Thus for the given data, we conclude that the optimal number of clusters for the data is 3
# Set the number of clusters = 3 
#==============================================================================
kclusters = 3

# run k-means clustering
kmeans = KMeans(init = "k-means++", n_clusters=kclusters, random_state=0, n_init = 12)
kmeans.fit(X)

# check cluster labels generated for each row in the dataframe
kmeans.labels_

# Add clustering labels
Moscow_grouped_df['Cluster_Labels'] = kmeans.labels_.astype(int)
#Moscow_grouped_df.insert(0, 'Cluster_Labels', kmeans.labels_.astype(int))

# Merge datasets, use left join as not all Boroughs have Gym venues
Moscow_Borough_Gym_Clustering_df = pd.merge(left=Moscow_Borough_Gym_df, right=Moscow_grouped_df, how='left', left_on='Borough_Name', right_on='Borough_Name')

# сохраним датасет
Moscow_Borough_Gym_Clustering_df.to_csv("Moscow_Borough_Gym_Clustering_df.csv", index = False)



###############################################################################
# Visualize the resulting clusters
###############################################################################
# Read previously saved dataset
Moscow_Borough_Gym_Clustering_df = pd.read_csv("Moscow_Borough_Gym_Clustering_df.csv")
Moscow_gym_venues_df = pd.read_csv("Moscow_gym_venues_df.csv")

# create map and display it
Moscow_map = folium.Map(location=[Moscow_lat, Moscow_lng], zoom_start=11)

# generate choropleth map
Moscow_map.choropleth(
    geo_data=mo_geojson,
    data=Moscow_Borough_Gym_Clustering_df,
    name='Population Density',
    columns=['Borough_Name', 'Cluster_Labels'],
    key_on='feature.properties.NAME',
    fill_color='YlOrRd', 
    fill_opacity=0.7, 
    line_opacity=0.2,
    legend_name='Borough Gym Clustering in Moscow City'
)

#==============================================================================
# Add markers to map for borough 
#==============================================================================
for Venue_name, lat, lng in zip(Moscow_gym_venues_df['Venue_Name'], Moscow_gym_venues_df['Venue_Latitude'], Moscow_gym_venues_df['Venue_Longitude']):
    folium.features.CircleMarker(
        [lat, lng],
        radius=5, # define how big you want the circle markers to be
        color='yellow',
        fill=True,
        #popup=folium.Popup('{}'.format(Venue_name), parse_html=True),
        fill_color='blue',
        fill_opacity=0.6
    ).add_to(Moscow_map)


# display map
Moscow_map



###############################################################################
# 
###############################################################################
#==============================================================================
# Prepare the dataset and calculate result ncluster value using elbow method
#==============================================================================
Moscow_Borough_df.columns

# create subset 
#X2 = Moscow_Borough_df[['Borough_Population','Borough_Housing_Area','Borough_Housing_Price']]
X2 = Moscow_Borough_df[['Borough_Population','Borough_Housing_Price']]
#X2 = Moscow_Borough_df[['Borough_Population_Housing_Price']]

# Normalizing over the standard deviation¶
X2 = StandardScaler().fit_transform(X2)

KMeans_elbow(X2, 10)

kclusters = 3

# run k-means clustering
kmeans = KMeans(init = "k-means++", n_clusters=kclusters, random_state=0, n_init = 12)
kmeans.fit(X2)

# Add clustering labels
Moscow_Borough_df['Cluster_Labels'] = kmeans.labels_.astype(int)

# сохраним датасет
Moscow_Borough_df.to_csv("Moscow_Borough_Gym_Clustering_df.csv", index = False)

# Analyze Clustres 
groups = Moscow_Borough_df.groupby('Cluster_Labels')
Moscow_Clustering_df = groups.mean().reset_index()[['Cluster_Labels', 'Borough_Population', 'Borough_Housing_Price']]
Moscow_Clustering_df.columns = ['Cluster_Labels', 'Mean_Population', 'Mean_Housing_Price']
Moscow_Clustering_df['Sum_Population'] = groups.sum().reset_index()[['Borough_Population']]
Moscow_Clustering_df['Count_Borough'] = groups.count().reset_index()[['Borough_Name']]

Moscow_Recomended_Borough_list = Moscow_Borough_df[Moscow_Borough_df['Cluster_Labels'].isin(['1'])]['Borough_Name']

# Delete Venues that placed outside our cluster 
Moscow_gym_venues_df = Moscow_gym_venues_df[Moscow_gym_venues_df['Borough_Name'].isin(Moscow_Recomended_Borough_list)]
Moscow_gym_venues_df.to_csv("Moscow_gym_venues_df.csv", index = False)


print(Moscow_Clustering_df)


# Normalizing over the standard deviation¶
from sklearn.preprocessing import StandardScaler
X = np.nan_to_num(X)
Clus_dataSet = StandardScaler().fit_transform(X)

