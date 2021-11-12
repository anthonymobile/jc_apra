import pandas as pd
import geopandas as gpd

# import folium
# from geopy.geocoders import Nominatim
# from geopy.geocoders import MapQuest
# from geopandas.tools import geocode

# import json
import datetime
# import contextily as cx
import numpy as np

def write_excel_data(gdf):
    picklefile = f'./data/gdf_patched.pkl'
    excel_file = f'./data/gdf_patched.xlsx'
    gdf.to_excel(excel_file, index=False)
    return

def read_excel_data():
    excel_file = f'./data/gdf_patched.xlsx'
    df = pd.read_excel(excel_file)
    df = df.drop(columns=['geometry'])
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat))
    print(f'Read gdf with shape {gdf.shape} from {excel_file}')
    return gdf

def generate_trend_metrics(gdf):
    
    # INTERPOLATION METHOD
    
    
    ################################################################################################
    # VACANTS

    # create a time series index from earliest to latest
    start=np.sort(gdf['date'].unique())[0]
    end=np.sort(gdf['date'].unique())[-1]
    index = pd.date_range(start=start, end=end, freq='D')
    columns = ['value_to_drop']
    date_range = pd.DataFrame(index=index, columns=columns)
    date_range = date_range.fillna(0)

    # create a new gdf of vacants
    gdf_tmp = gdf.loc[gdf['type'] == 'Vacant' ]
    group_vacant_annual = gdf_tmp.groupby(gdf_tmp['date'])
    series_vacant_annual = group_vacant_annual['date'].agg('count')
    gdf_vacant_annual = series_vacant_annual.to_frame(name='num_vacant')

    # and join them
    annual_vacants = date_range.join(gdf_vacant_annual)
    annual_vacants = annual_vacants.drop(columns=['value_to_drop'])

    # fill by interpolation
    # https://towardsdatascience.com/how-to-interpolate-time-series-data-in-apache-spark-and-python-pandas-part-1-pandas-cff54d76a2ea
    annual_vacants_interpolated = annual_vacants.resample('D')\
                    .mean()
    annual_vacants_interpolated['num_vacant'] = annual_vacants_interpolated['num_vacant'].interpolate()

    # compute value for 1 year before the last recorded data point.
    from datetime import timedelta
    datetime.datetime.now() - timedelta(days=365)
    ## for future use 
    # one_year_ago_today = datetime.datetime.now() - timedelta(days=365)
    one_year_ago_last_observed = annual_vacants_interpolated.index[-1] - timedelta(days=365)

    delta_v = annual_vacants_interpolated['num_vacant'][-1] - annual_vacants_interpolated.loc[one_year_ago_last_observed]
    
    ################################################################################################
    # ABANDONED
    
    # create a time series index from earliest to latest
    start=np.sort(gdf['date'].unique())[0]
    end=np.sort(gdf['date'].unique())[-1]
    index = pd.date_range(start=start, end=end, freq='D')
    columns = ['value_to_drop']
    date_range = pd.DataFrame(index=index, columns=columns)
    date_range = date_range.fillna(0)

    # create a new gdf of vacants
    gdf_tmp = gdf.loc[gdf['type'] == 'Abandoned' ]
    group_abandoned_annual = gdf_tmp.groupby(gdf_tmp['date'])
    series_abandoned_annual = group_abandoned_annual['date'].agg('count')
    gdf_abandoned_annual = series_abandoned_annual.to_frame(name='num_abandoned')

    # and join them
    annual_abandoned = date_range.join(gdf_abandoned_annual)
    annual_abandoned = annual_abandoned.drop(columns=['value_to_drop'])

    # fill by interpolation
    # https://towardsdatascience.com/how-to-interpolate-time-series-data-in-apache-spark-and-python-pandas-part-1-pandas-cff54d76a2ea
    annual_abandoned_interpolated = annual_abandoned.resample('D')\
                    .mean()
    annual_abandoned_interpolated['num_abandoned'] = annual_abandoned_interpolated['num_abandoned'].interpolate()

    # compute value for 1 year before the last recorded data point.
    from datetime import timedelta
    datetime.datetime.now() - timedelta(days=365)
    ## for future use 
    # one_year_ago_today = datetime.datetime.now() - timedelta(days=365)
    one_year_ago_last_observed = annual_abandoned_interpolated.index[-1] - timedelta(days=365)

    delta_a = annual_abandoned_interpolated['num_abandoned'][-1] - annual_abandoned_interpolated.loc[one_year_ago_last_observed]
    
    num_a = annual_abandoned_interpolated['num_abandoned'][-1]
    num_v = annual_vacants_interpolated['num_vacant'][-1]
    
    return num_a, num_v, delta_a[0], delta_v[0]