import cdsapi
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pandas as pd
import time
import datetime

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import numpy as np
import os




########################################################################################################

# function to get value from radar xarray. 
def find_value(Sitelat, Sitelon,xarray,stamp,variable):
    # Sitelat: The latitude list of the timetable
    # Sitelon: The longitude list of the timetale
    # xarray: The converted radar grid file with coordinates assigned
    # Variable: The field want to retrieve
    
    #start = time.time()
    values = []
    n = 0
    m=0
    k=0

    for i in range(len(Sitelat)):
        lat = Sitelat[i]
        lon = Sitelon[i]
        #print(lat, lon)

        try:
            value_location = xarray.sel(latitude = lat,longitude = lon, method='nearest',tolerance=0.25)[variable]
            value = value_location.sel(time=stamp).values

            if value == value:
                #print(value)
                n += 1
            values.append(value)
        except:
            print(lat,lon)
            k +=1
            value=None
            values.append(value)

#     try:
#         for i in xarray[variable].sel(time=stamp.split("T")[0],step=str(stamp.split("T")[1] +":00")).data:
#             for j in i:
#                 if j == j:
#                     m += 1
#     except:
#         print("%s does not exist" %(stamp))
    #print(np.unique(values))
    print("There are %d sites macthed with the ECMWF, %d sites are out of coverage from ECMWF" %(n, k))
    #print("----------%d seconds -------" %(time.time()-start))
    return values




########################################################################################################
# The old variable name
def match_ECMWF2AirNow(AirNow_Radar_df = "",ECMWF_xr = "", variables = ['blh']):

    time_stamps = list(AirNow_Radar_df["UTC"].unique())
    for stamp in time_stamps:
        Sitelat = list(AirNow_Radar_df.loc[AirNow_Radar_df['UTC'] == stamp,'Latitude'])
        Sitelon = list(AirNow_Radar_df.loc[AirNow_Radar_df['UTC'] == stamp,'Longitude'])

        for var in variables:
            print("retrieving %s values at %s from ECMWF grid file ......" %(var, stamp))
            AirNow_Radar_df.loc[AirNow_Radar_df['UTC'] == stamp, var] = find_value(Sitelat,Sitelon,ECMWF_xr,stamp,var)
    AirNow_Radar_df.to_csv(os.path.join('flowMatched',
                                        "AQS_US_PM25_20200102_20200102goes_ecmwf_sa_pop_landcover_soil_glim_gebco_blh.csv"))

########################################################################################################

if __name__ == "__main__":
    start_time=time.time()
    ds = xr.load_dataset('PBLH/era5_US_Single_2020_1.grib', engine='cfgrib')
    print("-------%s seconds to load GRIB file -------" %(time.time() - start_time))
    start_time=time.time()
    AirNow_Radar_df = pd.read_csv(os.path.join("flowMatched","AQS_US_PM25_20200102_20200102goes_ecmwf_sa_pop_landcover_soil_glim_gebco.csv"), index_col=0)
    match_ECMWF2AirNow(AirNow_Radar_df = AirNow_Radar_df,ECMWF_xr=ds)
    print("-------%s seconds to match GRIB file -------" %(time.time() - start_time))