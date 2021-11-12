# run with 
# streamlit run app.py --global.dataFrameSerialization="legacy"

from geo_functions import *

import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import datetime
import altair as alt
import pickle
from PIL import Image

import streamlit as st
from streamlit_folium import folium_static
import folium

###################################################################
# load and prepare data

gdf = read_excel_data()
df_v = gdf[gdf['type']== 'Vacant']
df_v['year'] = df_v['date'].dt.year
df_a = gdf[gdf['type']== 'Abandoned']
df_a['year'] = df_a['date'].dt.year
                  

###################################################################
# header

image = Image.open('./www/photo.jpg')
grayscale = image.convert('LA')
st.image(grayscale, caption='170 Grant Avenue, circa 2017. Photo by Jersey Digs.')

st.header('Jersey City has a big problem with vacant buildings.')

st.markdown('The Jersey City housing market has gone through many changes in recent years. Yet one thing has remained constant—neglect and warehousing of property by speculators and absentee landlords. Despite a reduction in the overall number of vacant and abandoned buildings, this is a stubborn and widespread problem.') 

st.markdown('The Abandoned Property Rehabilitation Act (APRA), adopted by the State of New Jersey in 2004, requires municipalities to maintain a list of vacant and abandoned properties. The data on this site are collated from lists published by the City of Jersey City since 2014. A copy of the collated, cleaned, and geocoded data can be downloaded here.')




###################################################################
# Map

# use streamlit-folium
# https://discuss.streamlit.io/t/ann-streamlit-folium-a-component-for-rendering-folium-maps/4367

st.subheader('Vacant buildings are a citywide problem.')

st.markdown('Vacant buildings are a citywide problem. Lores mumps dolor sit mate, nominal id xiv. Dec ore offend it man re, est no dolor es explicate, re dicta elect ram demo critic duo. Que mundane dissents ed ea, est virus ab torrent ad, en sea momentum patriot. Erato dolor em omit tam quo no, per leg ere argument um re. Romanesque acclimates investiture.')

# # center on Liberty Bell
# m = folium.Map(location=[39.949610, -75.150282], zoom_start=16)

# # add marker for Liberty Bell
# tooltip = "Liberty Bell"
# folium.Marker(
#     [39.949610, -75.150282], popup="Liberty Bell", tooltip=tooltip
# ).add_to(m)

# # call to render Folium map in Streamlit
# folium_static(m)

###################################################################
# Map

# MAKE MAP
# https://geopandas.readthedocs.io/en/latest/gallery/plotting_with_folium.html



# Stamen Toner
map = folium.Map(
    location=[40.7128,-74.1],
    tiles='Stamen Toner',
    zoom_start=13)

# Create a geometry list from the GeoDataFrame
geo_df_list_tmp = [[point.xy[1][0], point.xy[0][0]] for point in gdf.geometry ]

# drop NaNs
import math

geo_df_list = [t for t in geo_df_list_tmp if not any(isinstance(n, float) and math.isnan(n) for n in t)]

# Iterate through list and add a marker for each address, color-coded by its type.
i = 0
for coordinates in geo_df_list:
    #assign a color marker for the type
    if gdf['type'].iloc[i] == "Abandoned":
        type_color = "red"
    elif gdf['type'].iloc[i] == "Vacant":
        type_color = "orange"
    else:
        type_color = "gray"

        
    # alternate symbol
    # adapted from
    # https://stackoverflow.com/questions/33575053/change-marker-in-folium-map
    # and https://stackoverflow.com/questions/63152298/updating-folium-changed-the-popup-box-width
    
    html = "Address: " + str(gdf.street_address.iloc[i]) + '<br>' + \
           "Date: " + str(gdf.date.iloc[i]) + '<br>' + \
           "Status: " + str(gdf['type'].iloc[i])
    iframe = folium.IFrame(html)
    popup = folium.Popup(iframe,
                         min_width=250,
                         max_width=250)
        
    map.add_child(folium.CircleMarker(location = coordinates, 
                                      radius = 5, 
                                      popup = popup,
                                      fill_color=type_color,
                                      color=type_color, 
                                      fill_opacity=0.7))
    
    i = i + 1


folium_static(map)


















###################################################################
# Metrics


num_a, num_v, delta_a, delta_v = generate_trend_metrics(gdf)

st.subheader(f'How are we doing in {datetime.datetime.now().year}?')

st.markdown('Progress on vacant buildings has been slow.')


col1, col2 = st.columns(2)

###################################################################
# Abandoned
# col1.subheader('Abandoned Properties')
col1.metric("Abandoned Properties", num_a, f"{delta_a} this year", delta_color="inverse")
col1.line_chart(df_a['year'].value_counts())

###################################################################
# Vacant
# col2.subheader('Vacant Properties')
col2.metric("Vacant Properties", num_v, f"{delta_v} this year", delta_color="inverse")
col2.line_chart(df_v['year'].value_counts())


st.subheader(f'How has the stock of vacants changed across the city over time?')

st.markdown('Progress on vacant buildings has also been uneven.')



###################################################################
# Ward Table
ward_expander = st.expander(label='History by Ward')
with ward_expander:
    'Hello there!'
    click_ward = st.button('Click me!')

###################################################################
# Neighborhood Table
hood_expander = st.expander(label='History by Neighborhood')
with hood_expander:
    'Hello there!'
    click_hood = st.button('Click me muther $@$@#$!')



# ###################################################################
# # Long-term Vacants
# st.subheader('Long-term Vacancies')


# ###################################################################
# # Map
# st.subheader('Where are the Vacant and Abandoned Properties?')


# year = st.select_slider(
#     'Select a year to view properties',
#     options=[2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021])
# st.write('You picked', year)



###################################################################
# Combined
# st.map(gdf_av)
