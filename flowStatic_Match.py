import cdsapi
import xarray as xr
import rasterio
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pandas as pd
import time
from pyproj import Proj

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import numpy as np
import os



#######################################################################################################
def progressBar(current, total, barLength = 30):
    percent = float(current) * 100 / total
    arrow   = '-' * int(percent/100 * barLength - 1) + '>'
    spaces  = ' ' * (barLength - len(arrow))

    print('Progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')
########################################################################################################
# function to get value from radar xarray. 
def find_value(Sitelat, Sitelon,xarray):
    # Sitelat: The latitude list of the timetable
    # Sitelon: The longitude list of the timetale
    # xarray: The converted radar grid file with coordinates assigned
    # Variable: The field want to retrieve
    
    #start = time.time()
    values = []
    n = 0
    m=0
    k=0
    current=1

    for i in range(len(Sitelat)):
        progressBar(current,len(Sitelat))
        current+=1
        lat = Sitelat[i]
        lon = Sitelon[i]
        #print(lat, lon)
        try:
            value_location = xarray.sel(y = lat,x = lon, method='nearest',tolerance=0.5)
            value = value_location.values[0]
            if value == value:
                #print(value)
                n += 1
            values.append(value)
        except:
            k +=1
            value=None
            values.append(value)
#     try:
#         for i in xarray.sel(year=year).data:
#             for j in i:
#                 if j == j:
#                     m += 1
#     except:
#         print("%s does not exist" %(stamp))
    #print(np.unique(values))
    print("There are %d sites macthed with the raster, %d sites are out of coverage" %(n,k))
    #print("----------%d seconds -------" %(time.time()-start))
    return values




########################################################################################################

def match_static(df,xr,var):
    
        Sitelat = list(df.loc[:,'Latitude'])
        Sitelon = list(df.loc[:,'Longitude'])

        print("retrieving soild values from  geotiff file ......")
        df[var] = find_value(Sitelat,Sitelon,xr)

#         AirNow_Radar_df.to_csv(os.path.join('Matched',outname))

    #     print("-------%s seconds -------" %(time.time() - start_time))




########################################################################################################