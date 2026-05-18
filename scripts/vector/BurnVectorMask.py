from osgeo import ogr
from shapely.geometry import shape
from shapely.ops import unary_union
import rasterio
import rasterio.features
import numpy as np
import json

# ============================================================
# CONFIG
# ============================================================

DEM_FILE = "/home/geonux/lantmateriet_downloads/mhm-63_4_tile_15.tif"
VECTOR_FILE = "/home/geonux/PyProj/BiotopKartering/jalman_biotapkart_segments.shp"
ATTRIBUTE = "Strömmand"
BUFFER = 5
OUTPUT = "/home/geonux/PyProj/BiotopKartering/temp/mask.tif"

# ============================================================
# LOAD DEM
# ============================================================

with rasterio.open(DEM_FILE) as dem:
    meta = dem.meta.copy()
    transform = dem.transform
    height, width = dem.height, dem.width
    crs = dem.crs

# ============================================================
# LOAD VECTOR WITH OGR (robust)
# ============================================================

driver = ogr.GetDriverByName("ESRI Shapefile")
ds = driver.Open(VECTOR_FILE, 0)
layer = ds.GetLayer()

# ============================================================
# EXTRACT + BUFFER GEOMETRIES (ALL VALUES)
# ============================================================

shapes = []   # list of (geometry, value)

for feat in layer:
    val = feat.GetField(ATTRIBUTE)

    # Skip None or invalid values
    if val is None:
        continue

    # Convert geometry
    geom_json = json.loads(feat.GetGeometryRef().ExportToJson())
    geom = shape(geom_json)

    # Buffer geometry
    buffered = geom.buffer(BUFFER)

    # Append tuple (geometry, attribute_value)
    shapes.append((buffered, int(val)))

if not shapes:
    raise RuntimeError("No valid geometries found in attribute field.")

# ============================================================
# RASTERIZE ALL VALUES
# ============================================================

mask = rasterio.features.rasterize(
    shapes,
    out_shape=(height, width),
    transform=transform,
    fill=0,            # background = 0
    dtype="uint8"
)

# ============================================================
# SAVE MASK
# ============================================================

meta.update({
    "dtype": "uint8",
    "count": 1,
    "nodata": None
})

with rasterio.open(OUTPUT, "w", **meta) as dst:
    dst.write(mask, 1)

print("Mask created:", OUTPUT)
