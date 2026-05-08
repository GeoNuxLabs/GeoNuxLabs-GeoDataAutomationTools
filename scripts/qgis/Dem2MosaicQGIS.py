"""
Create a DEM mosaic from multiple GeoTIFF files using QGIS Processing (GDAL merge).

This script:
- Scans a folder for .tif raster files.
- Validates that rasters exist before processing.
- Runs GDAL's merge algorithm via QGIS Processing.
- Applies consistent NoData values.
- Saves the final mosaic to a specified output path.
- Logs warnings if no rasters are found.

Author: GeoNuxLabs
Repository: https://github.com/GeoNuxLabs/GeoNuxLabs-GeoDataAutomationTools
Requirements:
    - QGIS Python environment
    - GDAL (via QGIS Processing)
"""

import os
from qgis.core import QgsMessageLog
import processing


# ---------------------------------------------------------------------------
# Input folder and output path
# ---------------------------------------------------------------------------
folder = r"InputFolderPath"
output = r"OutputFolderPath/DEM_mosaic.tif"

# Collect all .tif rasters in folder
rasters = [
    os.path.join(folder, f)
    for f in os.listdir(folder)
    if f.lower().endswith(".tif")
]

# Validate raster list
if not rasters:
    msg = f"[ERROR] No .tif files found in folder: {folder}"
    QgsMessageLog.logMessage(msg, "DEM_Mosaic")
    print(msg)
    raise FileNotFoundError(msg)

print(f"Found {len(rasters)} raster files to merge.")


# ---------------------------------------------------------------------------
# Run GDAL merge via QGIS Processing
# ---------------------------------------------------------------------------
try:
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
except Exception as exc:
    msg = f"[ERROR] GDAL merge failed: {exc}"
    QgsMessageLog.logMessage(msg, "DEM_Mosaic")
    print(msg)
    raise


# ---------------------------------------------------------------------------
# Completion message
# ---------------------------------------------------------------------------
msg = f"Mosaic complete: {output}"
QgsMessageLog.logMessage(msg, "DEM_Mosaic")
print(msg)
