import cdsapi
import xarray as xr
import rasterio
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pandas as pd
import time

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import numpy as np
import os


########################################################################################################


# Function to read geotiff
def combinetiff(fn15,fn20,plot="no"):
    da15 = xr.open_rasterio(fn15)
    da20 = xr.open_rasterio(fn20)
    print("Triming to US extent")
    usda15 = da15.where(da15.y<50,drop=True).where(da15.y>25,drop=True).where(da15.x>-125,drop=True).where(da15.x<-65,drop=True)
    usda20 = da20.where(da20.y<50,drop=True).where(da20.y>25,drop=True).where(da20.x>-125,drop=True).where(da20.x<-65,drop=True)
    usda = xr.concat([usda15,usda20],'year')
    if plot =="yes":
        fig = plt.figure(figsize=(16,8))
        ax = fig.add_subplot(111)
        im =ax.imshow(usda15.variable.data[0],vmin=-10,vmax=100)
        plt.colorbar(im)
        plt.show()
        plt.savefig("Popden2015")
        
        fig = plt.figure(figsize=(16,8))
        ax = fig.add_subplot(111)
        im =ax.imshow(usda20.variable.data[0],vmin=-10,vmax=100)
        plt.colorbar(im)
        plt.show()
        plt.savefig("Popden2020")
    return usda
#######################################################################################################
def progressBar(current, total, barLength = 30):
    percent = float(current) * 100 / total
    arrow   = '-' * int(percent/100 * barLength - 1) + '>'
    spaces  = ' ' * (barLength - len(arrow))

    print('Progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')
########################################################################################################
# function to get value from radar xarray. 
def find_value(Sitelat, Sitelon,xarray,year):
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
    if year in ['2020','2019','2018']:
        year=1
    elif year in ['2016','2017']:
        year=0
    else:
        print(year+"beyond range")
    for i in range(len(Sitelat)):
        progressBar(current,len(Sitelat))
        current+=1
        lat = Sitelat[i]
        lon = Sitelon[i]
        #print(lat, lon)
        try:
            value_location = xarray.sel(y = lat,x = lon, method='nearest',tolerance=0.01)
            value = value_location.sel(year=year).values[0]
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
    print("There are %d sites macthed with the population density raster, %d sites are out of coverage from Radar" %(n,k))
    #print("----------%d seconds -------" %(time.time()-start))
    return values




########################################################################################################

def match_popdens(df = "",POPDEN_xr = ""):
    df['YEAR'] = df['UTC'].str[:4]
    time_stamps = list(df["UTC"].unique())
    year_stamps=[]
    for stamp in time_stamps:
        year_stamps.append(stamp.split('-')[0])
    year_stamps = list(np.unique(year_stamps))
    for year in year_stamps:
        
        Sitelat = list(df.loc[df['YEAR'] == year,'Latitude'])
        Sitelon = list(df.loc[df['YEAR'] == year,'Longitude'])

        print("retrieving population density values in %s from CEDAC geotiff file ......" %(year))
        df.loc[df['YEAR'] == year, 'popden'] = find_value(Sitelat,Sitelon,POPDEN_xr,year)

#     AirNow_Radar_df.to_csv(os.path.join('Matched',outname))

    #     print("-------%s seconds -------" %(time.time() - start_time))




########################################################################################################

if __name__ == "__main__":
    usda = combinetiff("PopDens/gpw-v4-population-density-rev11_2015_30_sec_tif/gpw_v4_population_density_rev11_2015_30_sec.tif",
                      "PopDens/gpw-v4-population-density-rev11_2020_30_sec_tif/gpw_v4_population_density_rev11_2020_30_sec.tif")
    AirNow_Radar_df = pd.read_csv(os.path.join("Matched/AQS_Radar2elevation_ECMWFLAND_US_20170101_20170630_Tolerance01.csv"), index_col=0)
    match_Pop2AirNow(AirNow_Radar_df = AirNow_Radar_df,POPDEN_xr=usda,outname ='AQS_Radar2elevation01_ECMWFLAND01_Pop001_US_20170101_20170630.csv')