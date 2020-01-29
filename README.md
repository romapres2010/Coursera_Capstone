# Venues Data Analysis of Moscow City

# Introduction <a name="Introduction"></a>

## Background <a name="Background"></a>

Moscow, one of the largest metropolises in the world with a population of more than 12 million people, covers an area of ​​more than 2561.5 km² with an average density of inheritance of 4924.96 people / km² [1](https://ru.wikipedia.org/wiki/%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0).

Moscow is divided into 12 districts (125 boroughs, 2 urban boroughs, 19 settlement boroughs).

Moscow has a very uneven population density from 30429 people / km² for the "Зябликово" borough, to 560 people / km² for the "Молжаниновский" borough [2](https://ru.wikipedia.org/wiki/%D0%A0%D0%B0%D0%B9%D0%BE%D0%BD%D1%8B_%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D1%8B).

The average cost of real estate varies from 68,768 rubles / m² for the "Кленовское" borough to 438,568 rubles / m² for the "Арбат" borough [3](https://www.mirkvartir.ru/journal/analytics/2018/02/25/reiting-raionov-moskvi-po-stoimosti-kvartir).

## Business Problem <a name="Business Problem"></a>

Owners of cafes, fitness centers and other social facilities are expected to prefer boroughs with a high population density. Investors will prefer areas with low housing costs and low competitiveness.

On the part of residents, the preference is expected for a boroughs with a low cost of housing and good accessibility of social places.

In my research, I will try to determine the optimal places for the location of fitness centers in Moscow boroughs, taking into account the number of people, the cost of real estate and the density of other fitness facilities.

The key criteria for selecting suitable locations for fitness centers will be:
- High density of the borough population
- Low cost of real estate in the area
- The absence in the immediate vicinity of other fitness facilities of a similar profile

I will use the approaches and methods of machine learning to determine the location of fitness centers in accordance with the specified criteria.

The main stakeholders of my research will be investors interested in opening new fitness centers.

# Data acquisition and cleaning <a name="data"></a>

## Data requirements

Based on the problem and the established selection criteria, to conduct the research, I will need the following information: 

1. main dataset with the list of Moscow Borough, containing the following attributes:
    - name of the each Moscow Borough
    - type of the each Moscow Borough
    - name of the each Moscow District in which Borough is belong to
    - area of the each Moscow Borough in square kilometers
    - the population of the each Moscow Borough
    - housing area of the each Moscow Borough in square meters
    - average housing price of the each Moscow Borough
2. geographical coordinates of the each Moscow Borough
3. shape of the each Moscow Borough in GEOJSON format
4. list of venues placed in the each Moscow Borough with their geographical coordinates and categories

## Decribe data sources 

### Moscow Boroughs dataset

Data for Moscow Boroughs dataset were downloaded from multiple HTTP page combined into one pandas dataframe.
- List of Moscow District and they Boroughs were downloaded from the page [Moscow Boroughs](https://gis-lab.info/qa/moscow-atd.html)
- Information about area of the each Moscow Borough in square kilometers, their population and housing area in square meters were downloaded from the page [Moscow Boroughs Population Density](https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D1%80%D0%B0%D0%B9%D0%BE%D0%BD%D0%BE%D0%B2_%D0%B8_%D0%BF%D0%BE%D1%81%D0%B5%D0%BB%D0%B5%D0%BD%D0%B8%D0%B9_%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D1%8B)
- Information about housing price of the each Moscow Borough were downloaded from the page [Moscow Boroughs Housing Price](https://www.mirkvartir.ru/journal/analytics/2018/02/25/reiting-raionov-moskvi-po-stoimosti-kvartir)

A special Python function has been developed for HTML table parse. This function help me:
- to find number of rows and columns in a HTML table
- to get cloumns titles, if posible
- to convert string to float, if posible
- return result in form of the Pandas dataframe

### Moscow Boroughs geographical coordinates

Geographical coordinates of the each Moscow Borough were queried through Nominatim service.   
As the Nominatim service are quite unstable it was quite a challenge to request coordinate in several iterations.

### Moscow Boroughs shape in GEOJSON format

Shape of the each Moscow Borough in GEOJSON format was downloaded from the page [Moscow Boroughs GEOJSON](http://gis-lab.info/data/mos-adm/mo.geojson)

### Moscow Boroughs venues

To determine **venues** the service **Forsquare API** was used.  
The API of **Forsquare** service have the restriction of 100 **venues**, which it can return in one request.  
To obtain list of all **venues** I used the following approach:  
  - present Moscow area in the form of a regular grid of circles of quite small diameter, no more than 100 **venues** in each circle  
  - perform exploration using **Forsquare API** with quite bigger radius than circle of a grid to make sure it overlaps/full coverage to don't miss any venues
  - cleaning list of venues from duplicates.  

This approach and some of the Python code was taken from the work presented here. https://cocl.us/coursera_capstone_notebook

Circle of 28 000 meter in radius cover all Moscow Boroughs.  
In my research grid of circles contains 7899 cells with radius 300 meter.  
Foursquare API have a certain limitation for API call in one day to explore venues.  
In my case it was about 2000 calls per day.  
So in addition I have to divide grid dataset into subset and call Foursquare API for several days. 

## Decribe data cleansing 

### Moscow Boroughs dataset cleansing

As data for Moscow Boroughs dataset were downloaded from multiple HTTP page it was necessary to perform a data cleaning. Such as:  
- remove some unused colums 
- strip text columns from additional information like ' \n\t'
- replace some Borough_Name as of russian letters "е" and "ё" 
- change places of some words in Borough_Name
- clear Borough Name from additional information, such as ', поселение ', ', городской округ '
- replace '\n', ' ↗' and '↘' in some columns
- delete extra spaces in numeric columns
- replace ',' to '.' for float columns
- convert from float to int for integer columns
- convert from string to float for numeric columns

As the result I had a dataset with all 146 Moscow Boroughs. Result dataset contains columns:
- **Borough_Name** - name of the Moscow Borough - is a unique key of the dataset
- **District_Name** - name of the Moscow District in which Borough is belong to
- **Borough_Type** - type of the Moscow Borough
- **OKATO_Borough_Code** - numeric code of the Moscow Borough
- **OKTMO_District_Code** - numeric code of the Moscow District
- **Borough_Area** - area of the Moscow Borough in square kilometers
- **Borough_Population** - population of the Moscow Borough
- **Borough_Population_Density** - population density of the Moscow Borough
- **Borough_Housing_Area** - housing area of the Moscow Borough in square meters
- **Borough_Housing_Area_Per_Person** - housing area per person of the Moscow Borough in square meters
- **Latitude** - geograprical Latitude of the Moscow Borough
- **Longitude** - geograprical Longitude of the Moscow Borough
- **Borough_Housing_Price** - average housing price of the Moscow Borough

I had a problem to found proper statistics about “housing prices” and “housing area” for some Moscow boroughs, so I had to exclude 26 boroughs from my analysis.   
Fortunately, they all had a low population density, which meat criteria of my research and did not reduce it quality.

#### The result Moscow Boroughs dataset

![Moscow Boroughs dataset](https://raw.githubusercontent.com/romapres2010/Coursera_Capstone/master/img/Moscow_borough_df.png)


### Moscow Boroughs geographical coordinates cleansing

Nominatim service not only quite unstable.  
It also have a occasionally problem with russian leter **ё**. So I have to manyaly obtain coordinates for such boroughs as:
 - Дес**ё**новское, Поселение, Новомосковский  
 - Сав**ё**лки, Муниципальный округ, ЗелАО
 - Кл**ё**новское, Поселение, Троицкий  
 - And some others.

Another problem with Nominatim service is that it return not very accurate coordinate of some Boroughs.  
So I needed to adjust they manually in the map.

### Moscow Boroughs shape in GEOJSON format cleansing

GEOJSON file downloaded from the page [Moscow Boroughs GEOJSON](http://gis-lab.info/data/mos-adm/mo.geojson) was quite good and not requied any addition clearing.

#### Boroughs Population in Moscow City

![Boroughs Population in Moscow City](https://raw.githubusercontent.com/romapres2010/Coursera_Capstone/master/img/Moscow_borough_population_dans.png)


### Moscow Boroughs venues cleansing

Usning **Forsquare API** I obtrained 34460 venues in 7899 cells.  
As I used a quite bigger radius (350 meters) for venue explorations than circle of a grid (300 meters), there was a need to remove duplicates venus.  
After duplicates removal I had 27622 unique venues in the circle radius of 28 000 meters around the Moscow City.  

The second task was to bind each venue to Moscow Boroughs in which borders they were placed.  
To perform this task I created a polygons for each Moscow Borough from GEOJSON file and found wich venues coordinate included into each polygon.  

The third task was to remove all the venues that placed outside of the Moscow boroughs.  

The fourth tas was to get main category from the category list for each venue.  

As the result I had list of 20864 venues placed in the Moscow Boroughs with their geographical coordinates and categories

#### Example of the hexagonal grid of area candidates

![Example of the hexagonal grid of area candidates](https://raw.githubusercontent.com/romapres2010/Coursera_Capstone/master/img/hexagonal_grid_example.png)

#### Example of the some Moscow Boroughs and theis venues

![Example of the some Moscow Boroughs and theis venues](https://raw.githubusercontent.com/romapres2010/Coursera_Capstone/master/img/Borough_venues_example.png)
