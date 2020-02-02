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
import numpy as np # library to handle data in a vectorized manner
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist 
import matplotlib.pyplot as plt 
import seaborn as sns
from scipy import stats

###############################################################################
# Load previously prepeared dataset 
###############################################################################
Moscow_Borough_df = pd.read_csv("data\Moscow_Borough_df.csv")
Moscow_venues_df = pd.read_csv("data\Moscow_venues_df.csv")
mo_geojson = 'data\mo.geojson'

Moscow_Borough_df.columns


###############################################################################
###############################################################################
# Exploratory Data Analysis
###############################################################################
###############################################################################

###############################################################################
# Сreate subset of the features
###############################################################################
# list of the potential features
Moscow_Borough_Feature_list = ['Borough_Name', 'District_Name', 'Borough_Area', 'Borough_Population_Density', 'Borough_Housing_Area', 'Borough_Population', 'Borough_Housing_Price']

# create subset of the potential features
Moscow_Borough_Feature_df = Moscow_Borough_df[Moscow_Borough_Feature_list]

# rename columns for easier understanding
Moscow_Borough_Feature_df.columns = ['Borough', 'District', 'Area', 'Population_Density', 'Housing_Area', 'Population', 'Housing_Price']

# Take a look at the correlation matrix 
print('Take a look at the features dataframe')
Moscow_Borough_Feature_df.head(10)


###############################################################################
# Descriptive ctatistical analysis
###############################################################################
# the count of that variable
# the mean
# the standard deviation (std)
# the minimum value
# the IQR (Interquartile Range: 25%, 50% and 75%)
# the maximum value

print('Take a look at the basic statistics')
Moscow_Borough_Feature_df.describe()


###############################################################################
# Categorical variables analysis
###############################################################################
print ("Let's look at the relationship between 'District' and 'Population'")
sns.boxplot(x="District", y="Population", data=Moscow_Borough_Feature_df)

print ("Let's look at the relationship between 'District' and 'Housing_Price'")
sns.boxplot(x="District", y="Housing_Price", data=Moscow_Borough_Feature_df)



###############################################################################
# Correlation analysis
###############################################################################
# calculate correlation matrix 
Moscow_Borough_Feature_corr = Moscow_Borough_Feature_df.corr()

# visualize correlation matrix 
f, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(Moscow_Borough_Feature_corr, mask=np.zeros_like(Moscow_Borough_Feature_corr, dtype=np.bool), cmap=sns.diverging_palette(220, 10, as_cmap=True),
            square=True, ax=ax)

# Take a look at the correlation matrix 
print('Take a look at the correlation matrix ')
Moscow_Borough_Feature_corr.head(6)


# Let's estimate the significant of the correlations between 'Area', 'Population_Density', 'Housing_Area' and 'Population'
pearson_coef, p_value = stats.pearsonr(Moscow_Borough_Feature_df['Area'], Moscow_Borough_Feature_df['Population'])
print("The Pearson Correlation Coefficient 'Area' to 'Population' is", pearson_coef, " with a P-value of P =", p_value)  
pearson_coef, p_value = stats.pearsonr(Moscow_Borough_Feature_df['Population_Density'], Moscow_Borough_Feature_df['Population'])
print("The Pearson Correlation Coefficient 'Population_Density' to 'Population' is", pearson_coef, " with a P-value of P =", p_value)  
pearson_coef, p_value = stats.pearsonr(Moscow_Borough_Feature_df['Housing_Area'], Moscow_Borough_Feature_df['Population'])
print("The Pearson Correlation Coefficient 'Housing_Area' to 'Population' is", pearson_coef, " with a P-value of P =", p_value)  

#Let's estimate the significant of the correlations between 'Area', 'Population_Density', 'Housing_Area' and 'Housing_Price'
pearson_coef, p_value = stats.pearsonr(Moscow_Borough_Feature_df['Area'], Moscow_Borough_Feature_df['Housing_Price'])
print("The Pearson Correlation Coefficient 'Area' to 'Housing_Price' is", pearson_coef, " with a P-value of P =", p_value)  
pearson_coef, p_value = stats.pearsonr(Moscow_Borough_Feature_df['Population_Density'], Moscow_Borough_Feature_df['Housing_Price'])
print("The Pearson Correlation Coefficient 'Population_Density' to 'Housing_Price' is", pearson_coef, " with a P-value of P =", p_value)  
pearson_coef, p_value = stats.pearsonr(Moscow_Borough_Feature_df['Housing_Area'], Moscow_Borough_Feature_df['Housing_Price'])
print("The Pearson Correlation Coefficient 'Housing_Area' to 'Housing_Price' is", pearson_coef, " with a P-value of P =", p_value)  

#Let's estimate the significant of the correlations between 'Area', 'Population_Density', 'Housing_Area'
pearson_coef, p_value = stats.pearsonr(Moscow_Borough_Feature_df['Area'], Moscow_Borough_Feature_df['Population_Density'])
print("The Pearson Correlation Coefficient 'Area' to 'Population_Density' is", pearson_coef, " with a P-value of P =", p_value)  
pearson_coef, p_value = stats.pearsonr(Moscow_Borough_Feature_df['Housing_Area'], Moscow_Borough_Feature_df['Population_Density'])
print("The Pearson Correlation Coefficient 'Housing_Area' to 'Population_Density' is", pearson_coef, " with a P-value of P =", p_value)  
pearson_coef, p_value = stats.pearsonr(Moscow_Borough_Feature_df['Housing_Area'], Moscow_Borough_Feature_df['Area'])
print("The Pearson Correlation Coefficient 'Housing_Area' to 'Area' is", pearson_coef, " with a P-value of P =", p_value)  


# plt.figure(figsize=(12, 10))
# sns.regplot(x="Housing_Area", y="Population_Density", data=Moscow_Borough_Feature_df)
# plt.ylim(0,)



###############################################################################
###############################################################################
# K-Means Clustering
###############################################################################
###############################################################################

###############################################################################
# Define the function clustering using k-means with elbow visualizations
###############################################################################
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



###############################################################################
# Prepare the dataset and calculate result ncluster value using elbow method
###############################################################################
# prepare dataset for K-means clustering
X2 = Moscow_Borough_df[['Borough_Population','Borough_Housing_Price']]

# Normalizing over the standard deviation
X2 = StandardScaler().fit_transform(X2)

# itterate from 1 to 10 n_clusters, calculate distortion and inertia, visualize it
KMeans_elbow(X2, 10)


###############################################################################
# Analyze 3 centroid KMeans clustering
###############################################################################
#==============================================================================
# Analyze 3 centroid KMeans clustering
#==============================================================================
kclusters = 3

# run k-means clustering
kmeans = KMeans(init = "k-means++", n_clusters=kclusters, random_state=0, n_init = 12)
kmeans.fit(X2)

# Add clustering labels
Moscow_Borough_df['Cluster_Labels'] = kmeans.labels_.astype(int)

# Analyze Clustres 
groups = Moscow_Borough_df.groupby('Cluster_Labels')
Moscow_population = Moscow_Borough_df['Borough_Population'].sum()
Moscow_area = Moscow_Borough_df['Borough_Area'].sum()
Moscow_Clustering_df = groups.mean().reset_index()[['Cluster_Labels', 'Borough_Population', 'Borough_Housing_Price']]
Moscow_Clustering_df.columns = ['Cluster_Labels', 'Population_Mean', 'Housing_Price_Mean']
Moscow_Clustering_df['Population_Sum'] = groups.sum().reset_index()[['Borough_Population']]
Moscow_Clustering_df['Population_%'] = Moscow_Clustering_df['Population_Sum'] / Moscow_population * 100
Moscow_Clustering_df['Borough_Count'] = groups.count().reset_index()[['Borough_Name']]
Moscow_Clustering_df['Area_Sum'] = groups.sum().reset_index()[['Borough_Area']]
Moscow_Clustering_df['Area_%'] = Moscow_Clustering_df['Area_Sum'] / Moscow_area * 100
Moscow_Clustering_df['Population_Density'] = Moscow_Clustering_df['Population_Sum'] / Moscow_Clustering_df['Area_Sum']

# Print clusters 
Moscow_Clustering_df.head()

# Save dataframe
Moscow_Clustering_df.to_csv("data\Moscow_Clustering_df.csv", index = False)
Moscow_Borough_df.to_csv("data\Moscow_Borough_df.csv", index = False)


#==============================================================================
# Vizualize clusters using boxplots visualization
#==============================================================================
print ("Let's look at the relationship between 'Cluster_Labels' and 'Borough_Housing_Price'")
sns.boxplot(x="Cluster_Labels", y="Borough_Housing_Price", data=Moscow_Borough_df)

print ("Let's look at the relationship between 'Cluster_Labels' and 'Borough_Population'")
sns.boxplot(x="Cluster_Labels", y="Borough_Population", data=Moscow_Borough_df)


#==============================================================================
# Vizualize clusters using choropleth map
#==============================================================================
mo_geojson = 'data\mo.geojson'

# Moscow latitude and longitude values
Moscow_lat= 55.7504461
Moscow_lng= 37.6174943

# create map 
Moscow_map = folium.Map(location=[Moscow_lat, Moscow_lng], zoom_start=10)

# generate choropleth map
Moscow_map.choropleth(
    geo_data=mo_geojson,
    data=Moscow_Borough_df,
    name='Population Density',
    columns=['Borough_Name', 'Cluster_Labels'],
    key_on='feature.properties.NAME',
    fill_color='YlOrRd', 
    fill_opacity=0.7, 
    line_opacity=0.2,
    legend_name='Borough Gym Clustering in Moscow City')


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

Moscow_map


###############################################################################
###############################################################################
# Result - location of fitness centers
###############################################################################
###############################################################################

###############################################################################
# Dataset of the optimal Boroughs
###############################################################################
# List of optimal Boroughs for the location of fitness centers
Moscow_Recomended_Borough_df = Moscow_Borough_df[Moscow_Borough_df['Cluster_Labels'].isin(['1'])]

# Drop some colums 
Moscow_Recomended_Borough_df.drop(['Latitude','Longitude','Cluster_Labels', 'OKTMO_District_Code', 'OKATO_Borough_Code', 'Borough_Housing_Area_Per_Person'], axis=1, inplace=True)

# reset index
Moscow_Recomended_Borough_df.reset_index(drop=True, inplace=True)

# save the result dataset
Moscow_Recomended_Borough_df.to_csv("data\Moscow_Recomended_Borough_df.csv", index = False)

# Take a look at the dataframe
Moscow_Recomended_Borough_df.head(40)


###############################################################################
# Dataset of the competitive fitness facilities
###############################################################################

# load previously saved dataset
Moscow_venues_df = pd.read_csv("data\Moscow_venues_df.csv")

# list of the recomended  Boughs from cluster 1
Moscow_Recomended_Borough_list = Moscow_Borough_df[Moscow_Borough_df['Cluster_Labels'].isin(['1'])]['Borough_Name']

# list of all subcategories Gym / Fitness Center
gym_categories = ['Gym / Fitness Center','Boxing Gym','Climbing Gym','Cycle Studio','Gymnastics Gym','Gym','Martial Arts Dojo','Outdoor Gym','Pilates Studio','Weight Loss Center','Yoga Studio']

# Make venues subset of all subcategories of "Gym / Fitness Center"
Moscow_gym_venues_df = Moscow_venues_df[Moscow_venues_df['Venue_Category_Name'].isin(gym_categories)]
print('There are {} venues of "Gym / Fitness Center" subcategories of all {} venues in Moscow City'.format(Moscow_gym_venues_df.shape[0], Moscow_venues_df.shape[0]))

# Delete Venues that placed outside our cluster 1
Moscow_gym_venues_df = Moscow_gym_venues_df[Moscow_gym_venues_df['Borough_Name'].isin(Moscow_Recomended_Borough_list)]
print('There are {} venues of all "Gym / Fitness Center" subcategories in 1 Cluster'.format(Moscow_gym_venues_df.shape[0]))

# prepare the result dataset with fitness center 
Moscow_gym_venues_df = Moscow_gym_venues_df[['Borough_Name','Venue_Name','Venue_Category_Name','Venue_Location','Venue_Latitude','Venue_Longitude']]

# reset index
Moscow_gym_venues_df.reset_index(drop=True, inplace=True)

# save the result dataset
Moscow_gym_venues_df.to_csv("data\Moscow_gym_venues_df.csv", index = False)

# Take a look at the dataframe
Moscow_gym_venues_df.head(30)


###############################################################################
# Visialize a Heatmap of Gym in 1 cluster
###############################################################################
Moscow_Borough_df = pd.read_csv("data\Moscow_Borough_df.csv")
mo_geojson = 'data\mo.geojson'

# Moscow latitude and longitude values
Moscow_lat= 55.7504461
Moscow_lng= 37.6174943

# create map
Moscow_map = folium.Map(location=[Moscow_lat, Moscow_lng], zoom_start=10)


# generate choropleth map
Moscow_map.choropleth(
    geo_data=mo_geojson,
    data=Moscow_Borough_df,
    name='Population Density',
    columns=['Borough_Name', 'Cluster_Labels'],
    key_on='feature.properties.NAME',
    fill_color='YlOrRd', 
    fill_opacity=0.4, 
    line_opacity=0.2,
    legend_name='Borough Gym Clustering in Moscow City')

# List comprehension to make out list of lists
heat_data = [[row['Venue_Latitude'], row['Venue_Longitude']] for index, row in Moscow_gym_venues_df.iterrows()]

# Add HeatMap
HeatMap(heat_data).add_to(Moscow_map)
#folium.GeoJson(mo_geojson).add_to(Moscow_map)

# Add Borougs center as markers to Moscow map 
for Venue_name, lat, lng in zip(Moscow_gym_venues_df['Venue_Name'], Moscow_gym_venues_df['Venue_Latitude'], Moscow_gym_venues_df['Venue_Longitude']):
    folium.features.CircleMarker(
        [lat, lng],
        radius=1, # define how big you want the circle markers to be
        color='yellow',
        fill=True,
        popup=folium.Popup('{}'.format(Venue_name), parse_html=True),
        fill_color='blue',
        fill_opacity=0.6
    ).add_to(Moscow_map)

# display map
Moscow_map

Moscow_map.save('map\Moscow_gym_heatmap.html')

#==============================================================================
# Add markers to map for borough 
#==============================================================================
mo_geojson = 'data\mo.geojson'

# Moscow latitude and longitude values
Moscow_lat= 55.7504461
Moscow_lng= 37.6174943

# create map 
Moscow_map = folium.Map(location=[Moscow_lat, Moscow_lng], zoom_start=10)

# generate choropleth map
Moscow_map.choropleth(
    geo_data=mo_geojson,
    data=Moscow_Borough_df,
    name='Population Density',
    columns=['Borough_Name', 'Cluster_Labels'],
    key_on='feature.properties.NAME',
    fill_color='YlOrRd', 
    fill_opacity=0.7, 
    line_opacity=0.2,
    legend_name='Borough Gym Clustering in Moscow City')


# Add Borougs center as markers to Moscow map 
for Venue_name, lat, lng in zip(Moscow_gym_venues_df['Venue_Name'], Moscow_gym_venues_df['Venue_Latitude'], Moscow_gym_venues_df['Venue_Longitude']):
    folium.features.CircleMarker(
        [lat, lng],
        radius=5, # define how big you want the circle markers to be
        color='yellow',
        fill=True,
        popup=folium.Popup('{}'.format(Venue_name), parse_html=True),
        fill_color='blue',
        fill_opacity=0.6
    ).add_to(Moscow_map)

    folium.Circle([lat, lng], radius=250, color='blue', fill=False).add_to(Moscow_map)

# display map
Moscow_map
