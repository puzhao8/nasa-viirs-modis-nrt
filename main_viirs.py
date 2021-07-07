# https://git.earthdata.nasa.gov/projects/LPDUR

from prettyprinter import pprint
from pathlib import Path

import h5py, os
import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal, gdal_array
import datetime as dt
import pandas as pd
from skimage import exposure



def get_geoInfo_and_projection(f):
    
    fileMetadata = f['HDFEOS INFORMATION']['StructMetadata.0'][()].split()   # Read file metadata
    fileMetadata = [m.decode('utf-8') for m in fileMetadata]                 # Clean up file metadata
    # fileMetadata[0:33]                                                       # Print a subset of the entire file metadata record

    ulc = [i for i in fileMetadata if 'UpperLeftPointMtrs' in i][0]    # Search file metadata for the upper left corner of the file
    ulcLon = float(ulc.split('=(')[-1].replace(')', '').split(',')[0]) # Parse metadata string for upper left corner lon value
    ulcLat = float(ulc.split('=(')[-1].replace(')', '').split(',')[1]) # Parse metadata string for upper left corner lat value

    yRes, xRes = -926.6254330555555,  926.6254330555555 # Define the x and y resolution   
    # yRes, xRes = -500,  500 # Define the x and y resolution   
    geoInfo = (ulcLon, xRes, 0, ulcLat, 0, yRes)        # Define geotransform parameters

    prj = 'PROJCS["unnamed",\
    GEOGCS["Unknown datum based upon the custom spheroid", \
    DATUM["Not specified (based on custom spheroid)", \
    SPHEROID["Custom spheroid",6371007.181,0]], \
    PRIMEM["Greenwich",0],\
    UNIT["degree",0.0174532925199433]],\
    PROJECTION["Sinusoidal"], \
    PARAMETER["longitude_of_center",0], \
    PARAMETER["false_easting",0], \
    PARAMETER["false_northing",0], \
    UNIT["Meter",1]]'

    return geoInfo, prj



if __name__ == "__main__":
    
    # "M3",     "M4",  "I1",  "I2",   "I3",    "M11",  "QF2"
    # "Blue", "Green", "Red", "NIR", "SWIR1", "SWIR2", "BitMask"
    BANDS = ["M3", "M4", "M5", 'M7', "M8"]


    inDir = "G:/PyProjects/nasa-viirs-modis-nrt/data"                               # Update to dir on your OS containing VIIRS files
    # os.chdir(inDir)                                                         # Change to working directory
    outDir = os.path.normpath(os.path.split(inDir)[0]+os.sep+'output')+'\\' # Set output directory
    if not os.path.exists(outDir): os.makedirs(outDir)                      # Create output directory


    fileList = [file for file in os.listdir(inDir) if file.endswith('.h5') and file.startswith('VNP09GA')] # Search for .h5 files in current directory
    for f in fileList: print(f)                                                                       # Print files in list

    date = [] # Create empty list to store dates of each file
    i = 0     # Set up iterator for automation in cell block below

    for t in fileList:
        yeardoy = t.split('.')[1][1:]                                                                  # Split name,retrieve ob date
        outName = t.rsplit('.', 1)[0]                                                                  # Keep filename for outname
        date1 = dt.datetime.strptime(yeardoy,'%Y%j').strftime('%m/%d/%Y')                              # Convert date
        date.append(date1)                                                                             # Append to list of dates
        f = h5py.File(os.path.normpath(Path(inDir) / t), "r")                                                             # Read in VIIRS HDF-EOS5 file
        
        # geoInfo and Projection
        geoInfo, prj = get_geoInfo_and_projection(f)

        h5_objs = []                                                                                   # Create empty list
        f.visit(h5_objs.append)                                                                        # Retrieve obj append to list
        
        # Search for SDS with 1km or 500m grid
        grids = list(f['HDFEOS']['GRIDS']) # List contents of GRIDS directory                                      # Clean up file metadata
    

        allSDS = [o for grid in grids for o in h5_objs if isinstance(f[o],h5py.Dataset) and grid in o] # Create list of SDS in file
        
        r = f[[a for a in allSDS if 'M5' in a][0]] 
        scaleFactor = r.attrs['Scale'][0]    # Set scale factor to a variable
        fillValue = r.attrs['_FillValue'][0] # Set fill value to a variable  

        print(f"scaleFactor: {scaleFactor}")

        band_dict = {}
        for band_name in BANDS:
            band = f[[a for a in allSDS if band_name in a][0]]                                                     # Open SDS M5 = Red
            band_scaled = band[()] #* scaleFactor
            band_dict[band_name] = band_scaled                                                   

        data = np.dstack(tuple(band_dict.values()))
        print(data.shape)

        data[data == fillValue * scaleFactor] = 0 # Set fill value equal to nan
        
        qf = f[[a for a in allSDS if 'QF5' in a][0]][()]                                               # Import QF5 SDS
        qf2 = f[[a for a in allSDS if 'QF2' in a][0]][()]                                              # Import QF2 SDS                                                                  # Append to list
        
        params = {
                'all':{'data':data, 'band': 'all'}
            }
        for p in params:
            try: 
                data = params[p]['data']                                                               # Define array to be exported
                data[data.mask == True] = fillValue                                                    # Masked values = fill value
            except: AttributeError
            outputName = os.path.normpath('{}{}_{}.tif'.format(outDir, outName, params[p]['band']))    # Generate output filename
            nRow, nCol = data.shape[0], data.shape[1]                                                  # Define row/col from array
            dataType = gdal_array.NumericTypeCodeToGDALTypeCode(data.dtype)                            # Define output data type
            driver = gdal.GetDriverByName('GTiff')                                                     # Select GDAL GeoTIFF driver
                                                                        # Diff for exporting RGBs
            data = params[p]['data']                                                               # Define the array to export
            dataType = gdal_array.NumericTypeCodeToGDALTypeCode(data.dtype)                        # Define output data type
            options = [
                        # 'PHOTOMETRIC=RGB', 
                        # 'PROFILE=GeoTIFF'
                        "TILED=YES",
                        "COMPRESS=LZW",
                        "INTERLEAVE=BAND"]                                       # Set options to RGB TIFF
            outFile = driver.Create(outputName, nCol, nRow, len(BANDS), dataType, options=options)          # Specify parameters of GTIFF
            for idx, band in enumerate(BANDS):  
                print(idx, band)                                                       # loop through each band (3)
                outFile.GetRasterBand(idx+1).WriteArray(data[..., i])                                  # Write to output bands 1-3
                outFile.GetRasterBand(idx+1).SetNoDataValue(0)                                       # Set fill val for each band
                outFile.GetRasterBand(idx+1).SetDescription(band)
                
            outFile.SetGeoTransform(geoInfo)                                                           # Set Geotransform
            outFile.SetProjection(prj)                                                                 # Set projection
            outFile = None                                                                             # Close file

        print('Processed file: {} of {}'.format(i+1, len(fileList)))                                    # Print the progress
        i += 1                                                                                         # increase iterator by one