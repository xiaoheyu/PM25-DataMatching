# from flowNEXRAD_Match_2elevation import *
from flowGOES_Match import *
from flowECMWF_Match_Land import *
from flowSA_Match import *
from flowPopDen_Match import *
from flowLandcover_Match import *
from flowStatic_Match import *

## This code is used to matching PM2.5 tables with variables. Data inclduing ECMWF, AOD, and ancillary data should
## be downloaded first through the code in PM25_DataSource folder
###################################################dynamic layers######################################################
# read raw data and match nexrad

source_file = "AQS_US_PM25_20200102_20200102.csv"

df = pd.read_csv(os.path.join("AQSDownload",source_file))
# print("Matching NEXRAD")
# match_nexrad(df)
# # df.to_csv(os.path.join("flowMatched","nex.csv"))

## match AOD
# df = pd.read_csv(os.path.join("flowMatched","nex.csv"))
print("Matching GOES AOD")
match_goes(df = df)
# df.to_csv(os.path.join("flowMatched","nexz01_goes.csv"),index=False)


## match ECMWF
print("Reading ecmwf grib")
da_ecmwf = xr.load_dataset('ECMWF_Monthly/era5_US_Land_2020_01.grib', engine='cfgrib')
# df = pd.read_csv(os.path.join("flowMatched","nexz01_goes.csv"))
print("Matching ecmwf")
match_ecmwf(df,da_ecmwf)
# df.to_csv(os.path.join("flowMatched","nexz01_goes_ecmwf.csv"),index=False)



## match SA
# df = pd.read_csv(os.path.join("flowMatched","nexz01_goes_ecmwf.csv"))
print("Matching sa")
match_sa(df)
# df.to_csv(os.path.join("flowMatched","nexz01_goes_ecmwf_sa.csv"),index=False)



## match Popdens
usda = combinetiff("PopDens/gpw-v4-population-density-rev11_2015_30_sec_tif/gpw_v4_population_density_rev11_2015_30_sec.tif",
                   "PopDens/gpw-v4-population-density-rev11_2020_30_sec_tif/gpw_v4_population_density_rev11_2020_30_sec.tif")
# df = pd.read_csv(os.path.join("flowMatched","nexz01_goes_ecmwf_sa.csv"))
print("Matching pop")
match_popdens(df,usda)
# df.to_csv(os.path.join("flowMatched","nexz01_goes_ecmwf_sa_pop.csv"),index=False)

####################################################static layers#######################################################


## match Landcover
# df = pd.read_csv(os.path.join("flowMatched","nexz01_goes_ecmwf_sa_pop.csv"))
da = xr.open_rasterio("LandCover/Reclass_NLCD_Re1kmMajorit.tif")
print("Matching landcover")
match_landcover(df,da)
# df.to_csv(os.path.join("flowMatched","nexz01_goes_ecmwf_sa_pop_landcover.csv"),index=False)



## match Soil
# df = pd.read_csv(os.path.join("flowMatched","nexz01_goes_ecmwf_sa_pop_landcover.csv"))
da = xr.open_rasterio("Soil/so2015v2.tif")
print("Triming to US extent")
da = da.where(da.y<50,drop=True).where(da.y>25,drop=True).where(da.x>-125,drop=True).where(da.x<-65,drop=True)
print("Matching soil")
match_static(df,da,"soil")
# df.to_csv(os.path.join("flowMatched","nexz01_goes_ecmwf_sa_pop_landcover_soil.csv"),index=False)




## match Glim
# df = pd.read_csv(os.path.join("flowMatched","nexz01_goes_ecmwf_sa_pop_landcover_soil.csv"))
da = xr.open_rasterio("GLiM/glim_wgs84_0point5deg.tif")
print("Triming to US extent")
da = da.where(da.y<50,drop=True).where(da.y>25,drop=True).where(da.x>-125,drop=True).where(da.x<-65,drop=True)
print("Matching glim")
match_static(df,da,"glim")
# df.to_csv(os.path.join("flowMatched","nexz01_goes_ecmwf_sa_pop_landcover_soil_glim.csv"),index=False)




# ## match lith4
# df = pd.read_csv(os.path.join("flowMatched","nexz01_goes_ecmwf_sa_pop_landcover_soil_glim.csv"))
# da = xr.open_rasterio("Lithology4Class/fullareagmnarocktypedecde.tif")
# print("Matching lith")
# match_static(df,da,"lith4")
# df.to_csv(os.path.join("flowMatched","nexz01_goes_ecmwf_sa_pop_landcover_soil_glim_lith4.csv"),index=False)




## match gebco
# df = pd.read_csv(os.path.join("flowMatched","nexz01_goes_ecmwf_sa_pop_landcover_soil_glim.csv"))
da = xr.open_rasterio("GEBCO_2020_tif/gebco_2020_n50.0_s25.0_w-125.0_e-65.0.tif")
print("Matching gebco")
match_static(df,da,"gebco")
print("Saving file to csv")
df.to_csv(os.path.join("flowMatched",source_file.split(".")[0] + "goes_ecmwf_sa_pop_landcover_soil_glim_gebco.csv"),index=False)