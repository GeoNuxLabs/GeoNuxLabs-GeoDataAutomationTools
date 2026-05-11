"""
Snap point features to the nearest location on a line layer using GeoPandas.

This script:
- Loads point and line layers from disk.
- Ensures both layers use the same CRS.
- Builds a spatial index for efficient nearest-line lookup.
- Snaps each point to the closest line using Shapely's nearest_points().
- Logs point IDs that cannot be snapped (rare but possible with invalid geometries).
- Saves the snapped points as a new shapefile.

Author: GeoNuxLabs
Repository: https://github.com/GeoNuxLabs/GeoNuxLabs-GeoDataAutomationTools
Requirements:
    - GeoPandas
    - Shapely
    - PyGEOS (optional, improves spatial index performance)
"""

import geopandas as gpd
from shapely.ops import nearest_points
from shapely.geometry import Point


# ---------------------------------------------------------------------------
# Load input layers
# ---------------------------------------------------------------------------
points = gpd.read_file("points.shp")
lines = gpd.read_file("lines.shp")

if points.empty:
    raise ValueError("Point layer contains no features.")

if lines.empty:
    raise ValueError("Line layer contains no features.")

# Ensure CRS match
points = points.to_crs(lines.crs)

# Build spatial index
line_sindex = lines.sindex


# ---------------------------------------------------------------------------
# Snapping function
# ---------------------------------------------------------------------------
def snap_point_to_nearest_line(point: Point):
    """
    Snap a single Shapely Point to the nearest line geometry.

    Parameters
    ----------
    point : shapely.geometry.Point
        The point to snap.

    Returns
    -------
    shapely.geometry.Point
        The snapped point on the nearest line.
    """

    # Find nearest line candidate using spatial index
    try:
        nearest_idx = list(line_sindex.nearest(point.bounds, 1))
    except Exception as exc:
        print(f"[ERROR] Spatial index lookup failed for point: {exc}")
        return None

    if not nearest_idx:
        print(f"[ERROR] No candidate line found for point: {point}")
        return None

    nearest_line = lines.iloc[nearest_idx[0]].geometry

    # Compute nearest point on the line
    try:
        snapped_point = nearest_points(point, nearest_line)[1]
    except Exception as exc:
        print(f"[ERROR] nearest_points() failed for point: {point} — {exc}")
        return None

    return snapped_point


# ---------------------------------------------------------------------------
# Apply snapping
# ---------------------------------------------------------------------------
snapped_geometries = []

for idx, geom in enumerate(points.geometry):
    snapped = snap_point_to_nearest_line(geom)

    if snapped is None:
        print(f"[WARNING] Point with index {idx} could NOT be snapped.")
        snapped_geometries.append(geom)  # keep original or set None
    else:
        snapped_geometries.append(snapped)

points["geometry"] = snapped_geometries


# ---------------------------------------------------------------------------
# Save result
# ---------------------------------------------------------------------------
points.to_file("snapped_points.shp")
print("Snapping complete!")

