import requests
import pandas as pd
import glob
import os
import numpy as np
import datetime
import pyart
# import boto
import tempfile
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import time
#suppress deprecation warnings
import warnings
warnings.simplefilter("ignore", category=DeprecationWarning)
# import moviepy.editor as mpy
#import dill

from pathlib import Path
from scipy import spatial



#######################################################################################################
def progressBar(current, total, barLength = 30):
    percent = float(current) * 100 / total
    arrow   = '-' * int(percent/100 * barLength - 1) + '>'
    spaces  = ' ' * (barLength - len(arrow))
    print('Progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')
########################################################################################################


def read_grid2xarray(path):
    grid = pyart.io.read_grid(path)
    xx = grid.get_point_longitude_latitude(1)[0]
    yy = grid.get_point_longitude_latitude(1)[1]
    coords = np.column_stack((yy.ravel(),xx.ravel()))
    ds_NEXRADgrid  = grid.to_xarray()
    ds_NEXRAD = ds_NEXRADgrid.assign_coords({"lon": (["y", "x"], xx)})
    ds_NEXRAD = ds_NEXRAD.assign_coords({"lat": (["y", "x"], yy)})
    ds_NEXRADZ0_1 = ds_NEXRAD.isel(z=[0,1])
    return coords,ds_NEXRADZ0_1


########################################################################################################


# function to get value from radar xarray. 
def find_value(newlats,newlons,dists,xarray,var,lyr):
    # Sitelat: The latitude list of the timetable
    # Sitelon: The longitude list of the timetale
    # xarray: The converted radar grid file with coordinates assigned
    # Variable: The field want to retrieve
    
    #start = time.time()
    values = []
    n = 0
    m=0
    k=0
    l=0
    p=0

    if lyr == "z01":
        xarray = xarray.max(dim="z")
    elif lyr == "fixGROUND":
        xarray = xarray.isel(z=0)
    elif lyr == "fix1KM":
        xarray = xarray.isel(z=1)
#     elif lyr == "2KM":
#         xarray = xarray.isel(z=2)
#     elif lyr == "3KM":
#         xarray = xarray.isel(z=3)
#     elif lyr == "4KM":
#         xarray = xarray.isel(z=4)
#     elif lyr == "5KM":
#         xarray = xarray.isel(z=5)
#     elif lyr == "6KM":
#         xarray = xarray.isel(z=6)
#     elif lyr == "7KM":
#         xarray = xarray.isel(z=7)
#     elif lyr == "8KM":
#         xarray = xarray.isel(z=8)
#     elif lyr == "9KM":
#         xarray = xarray.isel(z=9)
#     elif lyr == "10KM":
#         xarray = xarray.isel(z=10)
    elif lyr == "fixSTD":
        xarray = xarray.std(dim="z")


        
        
        
        
    for i in range(len(newlats)):
#         progressBar(i, len(newlats), barLength = 30)
        lat = newlats[i]
        lon = newlons[i]
        dist = dists[i]
        #print(lat, lon)
        

        if dist <= 0.1:
        # 1 deree = 85km in north south 40 degree
            value = xarray.where((xarray.lon==lon) & (xarray.lat==lat), drop=True)[var].values.squeeze() # select from list[0]
#             value = xarray.interp(y = lat,x = lon)[variable].values[0] # select from list[0]
#             print(value)
        else:
            l += 1
            value = None

        if value == value:
            #print(value)
            n += 1
            values.append(value)
        else:
            p += 1
            values.append(value)
            


#     for i in xarray[variable].data.squeeze():
#         for j in i:
#             if j == j:
#                 m += 1  
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
#     for i in range(len(Sitelat)):
#         progressBar(i, len(Sitelat), barLength = 30)
#         lat = Sitelat[i]
#         lon = Sitelon[i]
#         #print(lat, lon)
        
#         try:
#             print("KD tree searching")
#             dist, idx = spatial.KDTree(coords).query([lat,lon])
#             if dist <= 0.1:
#                 newlat,newlon = coords[idx]
#             # 1 deree = 85km in north south 40 degree
#                 value = xarray.where((xarray.lon==newlon) & (xarray.lat==newlat), drop=True)[variable].values.squeeze() # select from list[0]
#     #             value = xarray.interp(y = lat,x = lon)[variable].values[0] # select from list[0]
#             else:
#                 l += 1
#                 value = None

#             if value == value: 
#                 #print(value)
#                 n += 1
#                 values.append(value)
#             else:
#                 p += 1
#                 values.append(value)
            
#         except:
#             k += 1
#             value = None
#             values.append(value)

#     for i in xarray[variable].data.squeeze():
#         for j in i:
#             if j == j:
#                 m += 1
    #print(np.unique(values))
    print("There are %d records macthed with the Radar grid, %d records are beyond 0.1 tolerance, %d records retrived but are empty" %(n,l,p-l))
    #print("----------%d seconds -------" %(time.time()-start))
        
        
    return values
        


########################################################################################################


def match_nexrad(AirNow_df = "",variables = ['reflectivity','velocity','spectrum_width','differential_phase',
            'differential_reflectivity','cross_correlation_ratio'],layers = ['z01']):
    n=0
    flag=1
    time_stamps = sorted(list(AirNow_df["UTC"].unique()))
    for stamp in time_stamps:
        n+=1
        progressBar(n, len(time_stamps), barLength = 40)
        #Reformat the time stamp to match folder names
        theMonth = stamp.split("T")[0][:7]
        theDate = stamp.split("T")[0]
        theTime = stamp.split("T")[1].split(":")[0]+ "3000"
#         print(theMonth)
#         print(theDate)
#         print(theTime)
        gridPath =  glob.glob(os.path.join('NEXRAD',theMonth,theDate,theTime,'*.nc'))
        print(gridPath)
        if gridPath:

            gridPath = gridPath[0]
            print("===========================================================>")
            print("%s has been found " %(gridPath))
            coords,xr = read_grid2xarray(gridPath)
            print("Grid %s successfully read" %(gridPath))
            
            if flag:
                kdtree = spatial.KDTree(coords)
                flag = 0
                print("KDtree succefully build")
                

            Sitelat = list(AirNow_df.loc[AirNow_df['UTC'] == stamp,'Latitude'])
            Sitelon = list(AirNow_df.loc[AirNow_df['UTC'] == stamp,'Longitude'])
            Sites = np.column_stack((Sitelat,Sitelon))
            
            dists, idx = kdtree.query(Sites)
            
            newsites = coords[idx]
            newlats = newsites[:,0]
            newlons = newsites[:,1]
            
            
            for lyr in layers:
                for var in variables:
                    print("retrieving %s %s values" %(lyr,var))
                    AirNow_df.loc[AirNow_df['UTC'] == stamp, lyr+var] = find_value(
                        newlats,newlons,dists,xr,var,lyr)
        #     p = Path("/AirPool/DISK/share-drive/Mintscar/MBook/001e0610c2e7/2020/01/02")
#     AirNow_df.to_csv(os.path.join(saveName))

    #     print("-------%s seconds -------" %(time.time() - start_time))

########################################################################################################

# if __name__ == "__main__":
# #     raw_df = pd.read_csv("testinghead5000AOD.csv")
# #     match_grid2AirNow(AirNow_df = raw_df,saveName="z01testresult.csv")
                      
#     raw_df = pd.read_csv("Matched/AQS_Radar2ele01_ECMWFLANDFIX_Pop001_Cover_Soil_Glim_Lith4_GEBCO_160101_160630.csv")
#     match_grid2AirNow(AirNow_df = raw_df,saveName="AQS_Radar2ele01_ECMWFLANDFIX_Pop001_Cover_Soil_Glim_Lith4_GEBCO_Z01_160101_160630.csv")