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
import matplotlib.cm as cm
import matplotlib.colors as colors
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
# Analyze Neighborhood
###############################################################################
###############################################################################

# list of the recomended  Boughs from cluster 1
Moscow_Recomended_Borough_list = Moscow_Borough_df[Moscow_Borough_df['Cluster_Labels'].isin(['1'])]['Borough_Name']

# list of all subcategories Gym / Fitness Center
gym_categories = ['Gym / Fitness Center','Boxing Gym','Climbing Gym','Cycle Studio','Gymnastics Gym','Gym','Martial Arts Dojo','Outdoor Gym','Pilates Studio','Weight Loss Center','Yoga Studio']

# Make venues subset of all subcategories of "Gym / Fitness Center"
Moscow_gym_venues_df = Moscow_venues_df[Moscow_venues_df['Venue_Category_Name'].isin(gym_categories)]
print('There are {} venues of all "Gym / Fitness Center" subcategories in Moscow City'.format(Moscow_gym_venues_df.shape[0]))

# Delete Venues that placed outside our cluster 1
Moscow_gym_venues_df = Moscow_gym_venues_df[Moscow_gym_venues_df['Borough_Name'].isin(Moscow_Recomended_Borough_list)]
print('There are {} venues of all "Gym / Fitness Center" subcategories in 1 Cluster'.format(Moscow_gym_venues_df.shape[0]))

# save the dataset
Moscow_gym_venues_df.to_csv("data\Moscow_gym_venues_df.csv", index = False)


###############################################################################
# Visialize a Heatmap of Gym in 1 cluster
###############################################################################
# Moscow latitude and longitude values
Moscow_lat= 55.7504461
Moscow_lng= 37.6174943

# create map
Moscow_map = folium.Map(location=[Moscow_lat, Moscow_lng], zoom_start=11)

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

# display map
Moscow_map




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
        #popup=folium.Popup('{}'.format(Venue_name), parse_html=True),
        fill_color='blue',
        fill_opacity=0.6
    ).add_to(Moscow_map)

    folium.Circle([lat, lng], radius=250, color='blue', fill=False).add_to(Moscow_map)

Moscow_map

# display map





















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
Moscow_gym_venues_df.to_csv("data\Moscow_gym_venues_df.csv", index = False)

# Количество фитнес центров по районам
Moscow_gym_count_df = Moscow_gym_venues_df.groupby(['Borough_Name'],as_index=False).count()[['Borough_Name', 'Venue_Id']]

# переименуем колонки
Moscow_gym_count_df.columns = ['Borough_Name', 'Gym_Count']

# сольем датасеты
Moscow_Borough_Gym_df = pd.merge(left=Moscow_Borough_df, right=Moscow_gym_count_df, how='left', left_on='Borough_Name', right_on='Borough_Name', )

# количество жителей на один фитнес центр
Moscow_Borough_Gym_df['Borough_Population_Per_Gym'] = Moscow_Borough_Gym_df['Borough_Population'] / Moscow_Borough_Gym_df['Gym_Count']

# сохраним датасет
Moscow_Borough_Gym_df.to_csv("data\Moscow_Borough_Gym_df.csv", index = False)



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
Moscow_Borough_Gym_Clustering_df.to_csv("data\Moscow_Borough_Gym_Clustering_df.csv", index = False)



###############################################################################
# Visualize the resulting clusters
###############################################################################
# Read previously saved dataset
Moscow_Borough_Gym_Clustering_df = pd.read_csv("data\Moscow_Borough_Gym_Clustering_df.csv")
Moscow_gym_venues_df = pd.read_csv("data\Moscow_gym_venues_df.csv")

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


