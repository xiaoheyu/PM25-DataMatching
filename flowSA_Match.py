import pandas as pd
import numpy as np
from pysolar.solar import *
import datetime
import pytz


#######################################################################################################
def progressBar(current, total, barLength = 30):
    percent = float(current) * 100 / total
    arrow   = '-' * int(percent/100 * barLength - 1) + '>'
    spaces  = ' ' * (barLength - len(arrow))
    print('Progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')
######################################################################################################
# print("Reading source file")
# df= pd.read_csv("/AirPool/DISK/share-drive/NEXRAD/Model/MatlabModel/AQS_Radar2ele01_ECMWFLANDFIX_Pop001_Cover_Soil_Glim_Lith4_GEBCO_GOES2_Z01_17_20_fix_matlab_model2.csv")

def match_sa(df):
    LAT = df["Latitude"]
    LON = df["Longitude"]
    UTC = df["UTC"]
    n = len(LAT)

    #where:
    #θe = local zenith angle (in degrees)
    #β = arccos(cos(φ – φ0) * cos(λ - λ0)) (in degrees)
    #(φ0, λ0) = satellite subpoint latitude and longitude on Earth (in degrees)
    #(φ, λ) = view point latitude and longitude on Earth (in degrees)
    #H = 42164.16 (satellite height from the center of the Earth, in kilometers)
    #req = 6378.137 (length of semi-major axis of the Earth, in kilometers, assuming a GRS80 ellipsoid for the Earth)

    # # Define parameters
    # print("Calculating LZA")
    # (lat0, lon0,h,req) = 0, -75, 42164.16, 6378.137
    # # Vectorize
    # LAT0 = np.full((n, ), lat0)
    # LON0 = np.full((n, ), lon0)
    # H = np.full((n, ), h)
    # REQ = np.full((n, ), req)
    # BETA = np.arccos(np.cos(LAT - LAT0)*np.cos(LON - LON0))
    # THETA = np.arcsin(H*np.sin(BETA)/np.sqrt(H**2 + REQ**2 - 2*H*REQ*np.cos(BETA)))

    # df["LZA"] = THETA



    # Calculate Solar zenith angle and solar azimath angle
    UTC_format = '%Y-%m-%dT%H:%M'
    SZA = []
    SAA = []
    print("Calculating SA ")
    for index, stamp in enumerate(UTC):
        progressBar(index+1,len(UTC))
        dt = datetime.datetime.strptime(stamp,UTC_format)
        timezone = pytz.timezone("UTC")
        dt_tz = timezone.localize(dt)
        SZA.append(float(90) - get_altitude(LAT[index],LON[index], dt_tz))
        SAA.append(get_azimuth(LAT[index],LON[index], dt_tz))


    df["SZA"] = SZA
    df["SAA"] = SAA

#     print("Saving file...")
#     df.to_csv("/AirPool/DISK/share-drive/NEXRAD/Model/MatlabModel/AQS_Radar2ele01_ECMWFLANDFIX_Pop001_Cover_Soil_Glim_Lith4_GEBCO_GOES2_Z01_SA_17_20_fix_matlab_model2.csv")
#     print("Done!")