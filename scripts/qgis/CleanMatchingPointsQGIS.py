"""
Cleans two point layers by keeping only features that exist in both layers
based on matching attribute pairs.

This script:
- Loads two point layers from the current QGIS project.
- Extracts key tuples from two specified attribute fields.
- Computes the intersection of keys (i.e., points that exist in both layers).
- Creates two new in‑memory layers containing only the matching features.
- Ensures both output layers are identical in content.

Author: GeoNuxLabs
Repository: https://github.com/GeoNuxLabs/GeoDataAutomationTools
Requirements: QGIS Python API (PyQGIS)
"""

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature
)

# Input layers and comparison fields
layer1_name = "PointLayer1"
layer2_name = "PointLayer2"

compare_field1 = "CompareField1"
compare_field2 = "CompareField2"   # can be "" or None to match only on compare_field1

# Match key
def make_key(f):
    if not compare_field2:  # empty string, None, False → match only on field1
        return (f[compare_field1],)
    return (f[compare_field1], f[compare_field2])

# Load layers
proj = QgsProject.instance()
layer1 = proj.mapLayersByName(layer1_name)[0]
layer2 = proj.mapLayersByName(layer2_name)[0]

# Step 1: collect key tuples from each layer
keys_l1 = set()
for f in layer1.getFeatures():
    keys_l1.add(make_key(f))

keys_l2 = set()
for f in layer2.getFeatures():
    keys_l2.add(make_key(f))

# Step 2: compute intersection (points present in both layers)
common_keys = keys_l1.intersection(keys_l2)

print(f"Common points found: {len(common_keys)}")

# Step 3: function to create a cleaned memory layer
def create_clean_layer(src_layer, name):
    crs = src_layer.crs().authid()
    fields = src_layer.fields()

    out_layer = QgsVectorLayer(f"Point?crs={crs}", name, "memory")
    provider = out_layer.dataProvider()
    provider.addAttributes(fields)
    out_layer.updateFields()

    for f in src_layer.getFeatures():
        key = make_key(f)
        if key in common_keys:
            provider.addFeature(f)

    out_layer.updateExtents()
    proj.addMapLayer(out_layer)
    return out_layer

# Step 4: create two identical cleaned layers
clean_l1 = create_clean_layer(layer1, f"{layer1_name}_clean")
clean_l2 = create_clean_layer(layer2, f"{layer2_name}_clean")

print("Cleaning complete. Both output layers contain identical matched features.")
