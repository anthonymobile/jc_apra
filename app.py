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

gdf = read_excel_data().set_crs(epsg=4326)
df_v = gdf[gdf['type']== 'Vacant'].copy()
df_v['year'] = df_v['date'].dt.year
df_a = gdf[gdf['type']== 'Abandoned'].copy()
df_a['year'] = df_a['date'].dt.year
             
###################################################################
# header and footer 
# https://discuss.streamlit.io/t/remove-made-with-streamlit-from-bottom-of-app/1370/6
hide_streamlit_style = """
            <style>
                #MainMenu {visibility: hidden;}
                footer {
        
                        visibility: hidden;
                        
                        }
                    footer:after {
                        content:'2021, 2002 by Chilltown Labs.'; 
                        visibility: visible;
                        display: block;
                        position: relative;
                        #background-color: red;
                        padding: 5px;
                        top: 2px;
                    }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 



###################################################################
# header


st.header('Jersey City still has a big problem with vacant and abandoned buildings.')

st.markdown('The Jersey City housing market has gone through many changes in recent years. Yet one thing has remained constant—neglect and warehousing of property by speculators and absentee landlords. Despite a reduction in the overall number of vacant and abandoned buildings, this is a stubborn and widespread problem.') 

###################################################################
# METRICS + CHARTS
###################################################################

###################################################################
# Metrics

# st.subheader(f"How are we doing in {datetime.datetime.now().year}?")
# st.markdown('Progress on vacant buildings has been slow.')

num_a, num_v, delta_a, delta_v = generate_trend_metrics(gdf)

col1, col2 = st.columns(2)

###################################################################
# Abandoned
# col1.subheader('Abandoned Properties')
col1.metric("Abandoned Properties", f'{num_a:.0f}', f"{delta_a:.0f} this year", delta_color="inverse")

## streamlit version
# col1.line_chart(df_a['year'].value_counts())

# altair version
source = df_a.value_counts(subset=['year']).to_frame(name='num')
source = source.reset_index()
alt.renderers.set_embed_options(actions=False) #BUG doesnt work outside Jupyter notebook
c = alt.Chart(source).mark_line().encode(
    x=alt.X('year', axis=alt.Axis(format='.0f', title='Year', labelAngle=270)),
    y=alt.Y('num', axis=alt.Axis(format='.0f', title='No. of abandoned buildings')),
    tooltip=['year', 'num']
)
col1.altair_chart(c, use_container_width=True)



###################################################################
# Vacant
# col2.subheader('Vacant Properties')
col2.metric("Vacant Properties", f'{num_v:.0f}', f"{delta_v:.0f} this year", delta_color="inverse")

## streamlit version
# col1.line_chart(df_v['year'].value_counts())

# altair version
source = df_v.value_counts(subset=['year']).to_frame(name='num')
source = source.reset_index()

c = alt.Chart(source).mark_line().encode(
    x=alt.X('year', axis=alt.Axis(format='.0f', title='Year', labelAngle=270)),
    y=alt.Y('num', axis=alt.Axis(format='.0f', title='No. of vacant buildings')),
    tooltip=['year', 'num']
)
col2.altair_chart(c, use_container_width=True)




###################################################################
# DISTRICT TABLES
###################################################################
st.subheader(f'Vacant and abandoned buildings are everywhere.')


# ###################################################################
# # Ward Table

# ward_expander = st.expander(label='How many vacant and abandoned buildings are in my ward?')
# with ward_expander:
    
#     st.header('ADD A SMALL CHLOROPLETH MAP HERE')
    
#     ward_map = gpd.read_file('./maps/wards/ward2012.shp')
#     ward_map = ward_map.to_crs(epsg=4326)
#     gdf_by_ward=gpd.sjoin(gdf, ward_map, how='left', predicate="within")
#     gdf_by_ward['year'] = gdf_by_ward['date'].dt.year
#     result = pd.pivot_table(
#         gdf_by_ward, 
#         values='street_address', 
#         index=['WARD2'],           
#         columns=['year'], 
#         aggfunc=np.size
#     )
#     result[2019] = ''
#     result[2020] = ''
#     result = result.sort_index(axis=1)
#     st.table(result)

###################################################################
# Ward Table (alt, using neighborhood map)

# ward_expander = st.expander(label='How many vacant and abandoned buildings are in my ward?')
# with ward_expander:

st.markdown('Every ward has vacant and abandoned buildings throughout. There are vacant and abandoned buildings on almost every block. *Missing data for 2019 and 2020 will be filled in as it is made available by city officials.')

# load shapefile and set crs
neighborhood_map = gpd.read_file('./maps/neighborhoods/Neighborhoods3.shp')
neighborhood_map = neighborhood_map.to_crs(epsg=4326)

# spatial join
gdf_by_neighborhood=gpd.sjoin(gdf, neighborhood_map, how='left', predicate="within")


# make pivot table
table = pd.pivot_table(gdf_by_neighborhood, values='street_address', index=['Nghbhd'],
                    columns=['date'], aggfunc=np.size)
# clean up and render

gdf_by_neighborhood['year'] = gdf_by_neighborhood['date'].dt.year

result = pd.pivot_table(gdf_by_neighborhood, values='street_address', index=['District'],
                    columns=['year'], aggfunc=np.size)
result[2019] = '*'
result[2020] = '*'
result = result.sort_index(axis=1).fillna('')

# TODO format the float to 0 places
# pd.options.display.float_format = '{:.0f}'.format
st.table(result)


# ###################################################################
# # Neighborhood Table
# hood_expander = st.expander(label='How many vacant and abandoned buildings are in my neighborhood?')
# with hood_expander:
    
#     st.header('ADD A SMALL CHLOROPLETH MAP HERE')
    
#     # load shapefile and set crs
#     neighborhood_map = gpd.read_file('./maps/neighborhoods/Neighborhoods3.shp')
#     neighborhood_map = neighborhood_map.to_crs(epsg=4326)

#     # spatial join
#     gdf_by_neighborhood=gpd.sjoin(gdf, neighborhood_map, how='left', predicate="within")


#     # make pivot table
#     table = pd.pivot_table(gdf_by_neighborhood, values='street_address', index=['Nghbhd'],
#                         columns=['date'], aggfunc=np.size)
#     # clean up and render

#     gdf_by_neighborhood['year'] = gdf_by_neighborhood['date'].dt.year

#     result = pd.pivot_table(gdf_by_neighborhood, values='street_address', index=['Nghbhd'],
#                         columns=['year'], aggfunc=np.size)
#     result[2019] = ''
#     result[2020] = ''
#     result = result.sort_index(axis=1).fillna('')
    
#     # TODO format the float to 0 places
#     # pd.options.display.float_format = '{:.0f}'.format
#     st.table(result)

    
###################################################################
# Citywide Map
# map_expander = st.expander(label='Are there vacant and abandoned buildings on my block?')
# with map_expander:

# use streamlit-folium
# https://discuss.streamlit.io/t/ann-streamlit-folium-a-component-for-rendering-folium-maps/4367

# Stamen Toner
map = folium.Map(
    location=[40.725,-74.075],
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
# NOTICE
###################################################################

import os
import base64
def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href



st.subheader('Where does this data come from?')
st.markdown('The Abandoned Property Rehabilitation Act (APRA), adopted by the State of New Jersey in 2004, requires municipalities to maintain a list of vacant and abandoned properties. The data on this site are collated from lists published by the City of Jersey City since 2014. We are currently awaiting 2019 and 2020 figures through an Open Public Records Act (OPRA) request. A copy of the collated, cleaned, and geocoded data can be downloaded here.')

st.markdown(get_binary_file_downloader_html('./data/gdf_patched.xlsx', ' Data'), unsafe_allow_html=True)


image = Image.open('./www/163-clerk-st.png')
grayscale = image.convert('LA')
st.image(grayscale, caption='163 Clerk Street, Jersey City, New Jersey, January 2015. Photo by Jersey Digs.')


