import os

# Folder with DEMs
folder = r"/home/geonux/lantmateriet_downloads"

# Filter DEMs in folder 
rasters = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".tif")]

# Output storage location 
output = r"/home/geonux/PyProj/BiotopKartering/dem_jalman/DEM_mosaic2.tif"

# Run GDAL merge via QGIS Processing
processing.run(
    "gdal:merge",
    {
        "INPUT": rasters,
        "NODATA_INPUT": -9999,
        "NODATA_OUTPUT": -9999,
        "DATA_TYPE": 5,  # Float32
        "OUTPUT": output
    }
)


print("Mosaic done!:", output)