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
    #Convert gcs to pcs beacause Lancover tiff use pcs
    pro = Proj('+proj=aea +lat_0=23 +lon_0=-96 +lat_1=29.5 +lat_2=45.5 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs=True')
    for i in range(len(Sitelat)):
        progressBar(current,len(Sitelat))
        current+=1
        lat = Sitelat[i]
        lon = Sitelon[i]
        lon,lat = pro(lon,lat)

        #print(lat, lon)
        try:
            value_location = xarray.sel(y = lat,x = lon, method='nearest',tolerance=990)
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
    print("There are %d sites macthed with the landcover raster, %d sites are out of coverage from Radar" %(n,k))
    #print("----------%d seconds -------" %(time.time()-start))
    return values




########################################################################################################

def match_landcover(df = "",LandCover_xr = ""):
    
        Sitelat = list(df.loc[:,'Latitude'])
        Sitelon = list(df.loc[:,'Longitude'])

        print("retrieving landcover values from  geotiff file ......")
        df['landcover'] = find_value(Sitelat,Sitelon,LandCover_xr)

#        df.to_csv(os.path.join('Matched',outname))

    #     print("-------%s seconds -------" %(time.time() - start_time))




########################################################################################################

if __name__ == "__main__":
    da = xr.open_rasterio("LandCover/Reclass_NLCD_Re1kmMajorit.tif")
    AirNow_Radar_df = pd.read_csv(os.path.join("Matched/AQS_Radar2elevation01_ECMWFLAND01_Pop001_US_20170701_20171231.csv"), index_col=0)
    match_Pop2AirNow(AirNow_Radar_df = AirNow_Radar_df,LandCover_xr=da,outname ='AQS_Radar2ele01_ECMWFLAND01_Pop001_Cover_US_20170701_20171231.csv')