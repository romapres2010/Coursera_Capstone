# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 17:12:24 2020

@author: Roman
"""
#==============================================================================
# Import requied libraries
#==============================================================================
import requests
import pandas as pd
import json
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim



###############################################################################
###############################################################################
### Request and clear Moscow Boroughs list
###############################################################################
###############################################################################


###############################################################################
# Define function for HTML table parse
###############################################################################
def parse_html_table(table):
    n_columns = 0
    n_rows=0
    column_names = []

    # Find number of rows and columns
    # we also find the column titles if we can
    for row in table.find_all('tr'):
        
        # Determine the number of rows in the table
        td_tags = row.find_all('td')
        if len(td_tags) > 0:
            n_rows+=1
            if n_columns == 0:
                # Set the number of columns for our table
                n_columns = len(td_tags)
                
        # Handle column names if we find them
        th_tags = row.find_all('th') 
        if len(th_tags) > 0 and len(column_names) == 0:
            for th in th_tags:
                column_names.append(th.get_text())

    # Safeguard on Column Titles
    if len(column_names) > 0 and len(column_names) != n_columns:
        raise Exception("Column titles do not match the number of columns")

    columns = column_names if len(column_names) > 0 else range(0,n_columns)
    df = pd.DataFrame(columns = columns,
                        index= range(0,n_rows))
    row_marker = 0
    for row in table.find_all('tr'):
        column_marker = 0
        columns = row.find_all('td')
        for column in columns:
            df.iat[row_marker,column_marker] = column.get_text()
            column_marker += 1
        if len(columns) > 0:
            row_marker += 1
            
    # Convert to float if possible
    for col in df:
        try:
            df[col] = df[col].astype(float)
        except ValueError:
            pass
    
    return df


###############################################################################
# Load and parse Moscow Boroughs dataset from HTML page 
###############################################################################
# Load page with Moscow Boroughs
url = "https://gis-lab.info/qa/moscow-atd.html"
response = requests.get(url)

# Take second HTML table with districts from the page and parse it into dataframe
soup = BeautifulSoup(response.text, 'lxml')
tables = soup.findAll('table', { 'class' : 'wikitable sortable' }, limit=2) 
Moscow_df = parse_html_table(tables[1])  

# Define columns for dataframe
Moscow_df.columns=["Borough_index", "Borough_Name", "District_Name", "Borough_Type", "OKATO_Borough_Code", "OKTMO_District_Code"]

# Take a look at the dataframe
print(Moscow_df.head())
print(Moscow_df.shape)
print(Moscow_df.dtypes)


###############################################################################
# Clear Moscow Boroughs dataset
###############################################################################
# Drop Borough_index colums 
Moscow_df.drop("Borough_index", axis=1, inplace=True)

# Replace "\n" in the end of the text data
Moscow_df.replace('\n', '', regex=True, inplace=True)

# convert float to int for code columns
Moscow_df["OKATO_Borough_Code"] = Moscow_df["OKATO_Borough_Code"].astype(int)
Moscow_df["OKTMO_District_Code"] = Moscow_df["OKTMO_District_Code"].astype(int)

# Delete some Boroughs that far from the center of the Moscow city and have not enough statistics 
Moscow_df.drop(Moscow_df[Moscow_df['Borough_Type'].isin(['Городской округ', 'Поселение'])].index, inplace=True)
Moscow_df.drop(Moscow_df[Moscow_df['District_Name'].isin(['ЗелАО'])].index, inplace=True)
Moscow_df.drop(Moscow_df[Moscow_df['Borough_Name'].isin(['Некрасовка', 'Косино-Ухтомский', 'Восточный', 'Внуково', 'Молжаниновский', 'Куркино', 'Северный', 'Митино', 'Ново-Переделкино', 'Солнцево', 'Южное Бутово', 'Северное Бутово'])].index, inplace=True)

# Take a look at the result dataframe
print(Moscow_df.head())
print(Moscow_df.dtypes)

# Save dataframe for future use
Moscow_df.to_csv("Moscow_df.csv", index = False)




###############################################################################
###############################################################################
### Request coordinate of Moscow Borough
###############################################################################
###############################################################################
# define the dataframe columns
column_names = ['Borough_Name', 'Latitude', 'Longitude'] 

# instantiate the dataframe
Moscow_coord_df = pd.DataFrame(columns=column_names)

# create class instance of Nominatim
geolocator = Nominatim(user_agent="foursquare_agent", timeout=2)

# loop frough all Boroughs
for Borough_Name, Borough_Type in zip(Moscow_df['Borough_Name'], Moscow_df['Borough_Type']):
    address = '{}, {}, Москва, Россия'.format(Borough_Name, Borough_Type)
    print(address)

    location = None

    # loop until you get the coordinates
    while(location is None):
        location = geolocator.geocode(address)

    print('The geograpical coordinate of {}, {} are {}, {}.'.format(Borough_Name, Borough_Type, location.latitude, location.longitude))

    latitude = location.latitude
    longitude = location.longitude
    Moscow_coord_df = Moscow_coord_df.append({'Borough_Name': Borough_Name, 'Latitude': latitude, 'Longitude': longitude}, ignore_index=True) 

# Take a look at the dataframe
print(Moscow_coord_df.head())
print(Moscow_coord_df.shape)

# Save copy of the dataframe as service Nominatim not stable
Moscow_coord_df.to_csv("Moscow_coord_df.csv", index = False)

# As service Nominatim not stable, load coordinate from previously saved file
#Moscow_coord_df = pd.read_csv("Moscow_coord_df_new.csv")





###############################################################################
###############################################################################
### Request and clear Moscow Boroughs Housing Price
###############################################################################
###############################################################################

###############################################################################
# Load and parse Moscow Boroughs Housing Price dataset from HTML page 
###############################################################################
# Load page with Moscow Boroughs Housing Price
url = "https://www.mirkvartir.ru/journal/analytics/2018/02/25/reiting-raionov-moskvi-po-stoimosti-kvartir"
response = requests.get(url)

# Take first HTML table with districts from the page and parse it into dataframe
soup = BeautifulSoup(response.text, 'lxml')
tables = soup.findAll('table', limit=1) 
Moscow_housing_price_df = parse_html_table(tables[0]) 

# Take a look at the dataframe
print(Moscow_housing_price_df.head())
print(Moscow_housing_price_df.shape)
print(Moscow_housing_price_df.dtypes)

###############################################################################
# Clear Moscow Boroughs Housing Price dataset
###############################################################################
# Drop some unused colums 
Moscow_housing_price_df.drop([Moscow_housing_price_df.columns[0], Moscow_housing_price_df.columns[3], Moscow_housing_price_df.columns[4], Moscow_housing_price_df.columns[5]], axis=1, inplace=True)
Moscow_housing_price_df.drop(0, axis=0, inplace=True)

# Set columns for dataframe
Moscow_housing_price_df.columns=["Borough_Name", "Borough_Housing_Price"]

# Clear Borough Name from additional information
Moscow_housing_price_df["Borough_Name"] = Moscow_housing_price_df["Borough_Name"].str.strip(' \n\t')

# Replace '\n' in some columns
Moscow_housing_price_df.replace('\n', '', regex=True, inplace=True)

# Convert from string to numeric
Moscow_housing_price_df["Borough_Housing_Price"] = Moscow_housing_price_df["Borough_Housing_Price"].astype(int)

# replace some Borough_Name as of russian letters "е" and "ё" and change places of some words 
Moscow_housing_price_df["Borough_Name"].replace('Бирюлево Восточное', 'Бирюлёво Восточное', regex=True, inplace=True)
Moscow_housing_price_df["Borough_Name"].replace('Бирюлево-Западное', 'Бирюлёво Западное', regex=True, inplace=True)
Moscow_housing_price_df["Borough_Name"].replace('Дегунино Восточное', 'Восточное Дегунино', regex=True, inplace=True)
Moscow_housing_price_df["Borough_Name"].replace('Измайлово Восточное', 'Восточное Измайлово', regex=True, inplace=True)
Moscow_housing_price_df["Borough_Name"].replace('Дегунино Западное', 'Западное Дегунино', regex=True, inplace=True)
Moscow_housing_price_df["Borough_Name"].replace('Савеловский', 'Савёловский', regex=True, inplace=True)
Moscow_housing_price_df["Borough_Name"].replace('Измайлово Северное', 'Северное Измайлово', regex=True, inplace=True)
Moscow_housing_price_df["Borough_Name"].replace('Медведково Северное', 'Северное Медведково', regex=True, inplace=True)
Moscow_housing_price_df["Borough_Name"].replace('Тушино Северное', 'Северное Тушино', regex=True, inplace=True)
Moscow_housing_price_df["Borough_Name"].replace('Теплый Стан', 'Тёплый Стан', regex=True, inplace=True)
Moscow_housing_price_df["Borough_Name"].replace('Тропарево-Никулино', 'Тропарёво-Никулино', regex=True, inplace=True)
Moscow_housing_price_df["Borough_Name"].replace('Филевский Парк', 'Филёвский Парк', regex=True, inplace=True)
Moscow_housing_price_df["Borough_Name"].replace('Хорошево-Мневники', 'Хорошёво-Мнёвники', regex=True, inplace=True)
Moscow_housing_price_df["Borough_Name"].replace('Хорошевский', 'Хорошёвский', regex=True, inplace=True)
Moscow_housing_price_df["Borough_Name"].replace('Черемушки', 'Черёмушки', regex=True, inplace=True)
Moscow_housing_price_df["Borough_Name"].replace('Медведково Южное', 'Южное Медведково', regex=True, inplace=True)
Moscow_housing_price_df["Borough_Name"].replace('Тушино Южное', 'Южное Тушино', regex=True, inplace=True)

# Take a look at the result dataframe
print(Moscow_housing_price_df.head())
print(Moscow_housing_price_df.shape)
print(Moscow_housing_price_df.dtypes)

# Save copy of the dataframe
Moscow_housing_price_df.to_csv("Moscow_housing_price_df.csv", index = False)





###############################################################################
###############################################################################
### Request and clear Moscow Boroughs Population Density
###############################################################################
###############################################################################

###############################################################################
# Load and parse Moscow Boroughs Population Density dataset from HTML page 
###############################################################################
# Load page with Moscow Boroughs Population Density
url = "https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D1%80%D0%B0%D0%B9%D0%BE%D0%BD%D0%BE%D0%B2_%D0%B8_%D0%BF%D0%BE%D1%81%D0%B5%D0%BB%D0%B5%D0%BD%D0%B8%D0%B9_%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D1%8B"
response = requests.get(url)

# Take first HTML table with districts from the page and parse it into dataframe
soup = BeautifulSoup(response.text, 'lxml')
tables = soup.findAll('table', { 'class' : 'standard sortable' }, limit=1) 
Moscow_dens_df = parse_html_table(tables[0]) 

# Take a look at the dataframe
print(Moscow_dens_df.head())
print(Moscow_dens_df.shape)
print(Moscow_dens_df.dtypes)


###############################################################################
# Clear Moscow Boroughs Population Density dataset
###############################################################################
# Drop some unused colums 
Moscow_dens_df.drop([Moscow_dens_df.columns[0], Moscow_dens_df.columns[1], Moscow_dens_df.columns[2], Moscow_dens_df.columns[3], Moscow_dens_df.columns[5]], axis=1, inplace=True)

# Set columns for dataframe
Moscow_dens_df.columns=["Borough_Name", "Borough_Area", "Borough_Population", "Borough_Population_Density", "Borough_Housing_Area", "Borough_Housing_Area_Per_Person"]

# Clear Borough Name from additional information
Moscow_dens_df["Borough_Name"].replace(', поселение ', '', regex=True, inplace=True)
Moscow_dens_df["Borough_Name"].replace(', городской округ ', '', regex=True, inplace=True)
Moscow_dens_df["Borough_Name"] = Moscow_dens_df["Borough_Name"].str.strip(' \n\t')
Moscow_dens_df["Borough_Name"].replace('Мосрентген', '"Мосрентген"', regex=True, inplace=True)

# Replace '\n' and ' ↗' in some columns
Moscow_dens_df.replace('\n', '', regex=True, inplace=True)
Moscow_dens_df.replace('↗', '', regex=True, inplace=True)
Moscow_dens_df.replace('↘', '', regex=True, inplace=True)

# Delete extra spaces in numeric columns
Moscow_dens_df["Borough_Area"].replace(' ', '', regex=True, inplace=True)
Moscow_dens_df["Borough_Population"].replace('\xa0', '', regex=True, inplace=True)
Moscow_dens_df["Borough_Population"].replace(' ', '', regex=True, inplace=True)
Moscow_dens_df["Borough_Population_Density"].replace(' ', '', regex=True, inplace=True)
Moscow_dens_df["Borough_Housing_Area"].replace(' ', '', regex=True, inplace=True)
Moscow_dens_df["Borough_Housing_Area_Per_Person"].replace(' ', '', regex=True, inplace=True)

# Replace ',' to '.' for float columns
Moscow_dens_df["Borough_Area"].replace(',', '.', regex=True, inplace=True)
Moscow_dens_df["Borough_Housing_Area"].replace(',', '.', regex=True, inplace=True)
Moscow_dens_df["Borough_Housing_Area_Per_Person"].replace(',', '.', regex=True, inplace=True)

# Convert from string to numeric
Moscow_dens_df["Borough_Population"] = Moscow_dens_df["Borough_Population"].astype(int)
Moscow_dens_df["Borough_Population_Density"] = Moscow_dens_df["Borough_Population_Density"].astype(int)
Moscow_dens_df["Borough_Area"] = Moscow_dens_df["Borough_Area"].astype(float)
Moscow_dens_df['Borough_Housing_Area'] = pd.to_numeric(Moscow_dens_df['Borough_Housing_Area'], errors='coerce')
Moscow_dens_df['Borough_Housing_Area_Per_Person'] = pd.to_numeric(Moscow_dens_df['Borough_Housing_Area_Per_Person'], errors='coerce')

# Take a look at the dataframe
print(Moscow_dens_df.head())
print(Moscow_dens_df.dtypes)

# Save copy of the dataframe
Moscow_dens_df.to_csv("Moscow_dens_df.csv", index = False)




###############################################################################
###############################################################################
### Join all datasets into result Moscow Borough dataset
###############################################################################
###############################################################################
# Merge datasets
Moscow_Borough_df = pd.merge(left=Moscow_df, right=Moscow_dens_df, left_on='Borough_Name', right_on='Borough_Name')
Moscow_Borough_df = pd.merge(left=Moscow_Borough_df, right=Moscow_coord_df, left_on='Borough_Name', right_on='Borough_Name')
Moscow_Borough_df = pd.merge(left=Moscow_Borough_df, right=Moscow_housing_price_df, left_on='Borough_Name', right_on='Borough_Name')

# Take a look at the dataframe
print(Moscow_Borough_df.head())
print(Moscow_Borough_df.dtypes)

# Save result dataframe
Moscow_Borough_df.to_csv("Moscow_Borough_df.csv", index = False)



###############################################################################
###############################################################################
### Dowload GEOJSON for Moscow Boroughs
###############################################################################
###############################################################################
# download geojson file
url = 'http://gis-lab.info/data/mos-adm/mo.geojson'
download_file = requests.get(url)
mo_geojson_utf8 = 'mo.geojson.utf8'
mo_geojson = 'mo.geojson'
open(mo_geojson_utf8, 'wb').write(download_file.content)    
print('GeoJSON file downloaded!')

# Encode file from utf8 to cp1251 as my computer use Russian locale
f = open(mo_geojson, "wb")
for line in open(mo_geojson_utf8, "rb"):
    f.write(line.decode('u8').encode('cp1251', 'ignore'))
f = open(mo_geojson, "wb")
for line in open(mo_geojson_utf8, "rb"):
    f.write(line.decode('u8').encode('cp1251', 'ignore'))


# validate geojson file    
with open(mo_geojson) as json_file:
    data = json_file.read()
    try:
        data = json.loads(data)
    except ValueError as e:
        print('invalid json: %s' % e)








# Calculate index with highest populstions and lower housing price = Population / Housing_Price
Moscow_Borough_df['Borough_Population_Housing_Price'] = Moscow_Borough_df['Borough_Population'] / Moscow_Borough_df['Borough_Housing_Price']
