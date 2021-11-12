import requests
import pandas as pd
import xarray as xr
from pyproj import Proj
import glob
import os
import numpy as np
import datetime
from datetime import datetime
# import pyart
import boto
import tempfile
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import time
#suppress deprecation warnings
import warnings
warnings.simplefilter("ignore", category=DeprecationWarning)
import moviepy.editor as mpy
#import dill

from pathlib import Path


#######################################################################################################
def progressBar(current, total, barLength = 30):
    percent = float(current) * 100 / total
    arrow   = '-' * int(percent/100 * barLength - 1) + '>'
    spaces  = ' ' * (barLength - len(arrow))
    print('Progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')

########################################################################################################


def read_goesnc2xr(path):
    ds = xr.open_dataset(path,decode_times=False)
    sat_h = ds.variables['goes_imager_projection'].attrs["perspective_point_height"]
    
    # Assign coordinates
    xrcor = ds.assign_coords(x=(ds.x)*sat_h,y=(ds.y)*sat_h)
    return sat_h, xrcor


########################################################################################################


# function to get value from radar xarray. 
def find_value(Sitelat, Sitelon,xarray,sat_h,var):
    # Sitelat: The latitude list of the timetable
    # Sitelon: The longitude list of the timetale
    # xarray: The AOD nc file
    # Var: The field want to retrieve  
    
    #start = time.time()
    values = []
    n = 0
    m=0
    k=0

    
    #Convert gcs to pcs 
    pro = Proj("+proj=geos +lon_0=-75 +h=" +str(round(sat_h)) + " +x_0=0 +y_0=0 +ellps=GRS80 +units=m +no_defs=True") 
    for i in range(len(Sitelat)):

        lat = Sitelat[i]
        lon = Sitelon[i]
        lon,lat = pro(lon,lat)

        #print(lat, lon)
        try:
            value_location = xarray.sel(y = lat,x = lon, method='nearest',tolerance=2000)
            value = value_location[var].data
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
    print("There are %d sites matched with the current data file, %d sites are out of coverage" %(n,k))
    #print("----------%d seconds -------" %(time.time()-start))
    return values





########################################################################################################


def match_goes(df = "",vars = ['AOD','DQF']):
    missing_file = 0
    missing_stamp =[]
    UTC_format = '%Y-%m-%dT%H:%M'
    #Serching will all modes
    aodfn_prefix= "OR_ABI-L2-AODC-*_G16_s"
    aodfolder_prefix = "noaa-goes16/ABI-L2-AODC/"
    current=1
    time_stamps = list(df["UTC"].unique())
    for stamp in time_stamps:
        progressBar(current,len(time_stamps))
        current+=1
        dt_object = datetime.strptime(stamp,UTC_format)
        aod_timepath = datetime.strftime(dt_object, "%Y/%j/%H/")
        aod_fn = datetime.strftime(dt_object, aodfn_prefix + "%Y%j%H")
        mins = "3"
        aod_searchpath = os.path.join(aodfolder_prefix,aod_timepath,aod_fn + mins + '*')
#         print(aod_searchpath)
        nc_path =  glob.glob(aod_searchpath)
        if nc_path:
            nc_path = nc_path
        else:
            aod_searchpath = os.path.join(aodfolder_prefix,aod_timepath,aod_fn + '*')
            nc_path = glob.glob(aod_searchpath)
#         print(nc_path)
        if nc_path:
            try:
            # Select file from lst, if more than one exist, select the first one which is closest to **:30 the mid time of an hour
                nc_path = nc_path[0]
                print("===========================================================>")
                print("%s has been found " %(nc_path))
                print("Reading ......")
                sat_h, xrcor = read_goesnc2xr(nc_path)
                print("Grid successfully read")

                Sitelat = list(df.loc[df['UTC'] == stamp,'Latitude'])
                Sitelon = list(df.loc[df['UTC'] == stamp,'Longitude'])
                for var in vars:
                    print("retrieving %s values" %(var))
                    df.loc[df['UTC'] == stamp, var] = find_value(Sitelat,Sitelon,xrcor,sat_h,var)
            except:
                    missing_file +=1
                    missing_stamp.append(aod_searchpath)
        else:
            missing_file +=1
            missing_stamp.append(aod_searchpath)
    print("The are %d timestamps faild to find files" %(missing_file))
    print(missing_stamp)
#     df.to_csv(os.path.join('Matched',saveName))

    #     print("-------%s seconds -------" %(time.time() - start_time))

########################################################################################################

if __name__ == "__main__":
    raw_df = pd.read_csv(os.path.join("Matched","AQS_Radar2ele01_ECMWFLANDFIX_Pop001_Cover_Soil_Glim_Lith4_GEBCO_GOES_Z01_200701_201231.csv"))
    match_goes(df = raw_df,saveName="AQS_Radar2ele01_ECMWFLANDFIX_Pop001_Cover_Soil_Glim_Lith4_GEBCO_GOES2_Z01_200701_201231.csv")