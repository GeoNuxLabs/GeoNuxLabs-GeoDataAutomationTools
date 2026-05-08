"""
Snaps point features to the nearest position on a line layer.

This script:
- Loads a point layer and a line layer from the current QGIS project.
- Builds a spatial index for efficient nearest‑line lookup.
- For each point, finds candidate lines within a search radius (10 m buffer).
- Falls back to nearest‑neighbor search if no candidates are found.
- Computes the true nearest point on each candidate line.
- Creates a new in‑memory point layer containing the snapped points.
- Copies all attribute values from the original point layer.

Author: GeoNuxLabs
Repository: https://github.com/GeoNuxLabs/GeoNuxLabs-GeoDataAutomationTools
Requirements: QGIS Python API (PyQGIS)
"""

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsSpatialIndex,
    QgsFeatureRequest,
    QgsFeature
)

# Input layers
point_layer = QgsProject.instance().mapLayersByName("PointLayer")[0]
line_layer = QgsProject.instance().mapLayersByName("LineLayer")[0]

# Output layer (memory)
output_layer = QgsVectorLayer(
    f"Point?crs={point_layer.crs().authid()}",
    "snapped_points",
    "memory"
)
provider = output_layer.dataProvider()
provider.addAttributes(point_layer.fields())
output_layer.updateFields()

# Build spatial index for faster line lookup
spatial_index = QgsSpatialIndex(line_layer.getFeatures())

for point_feature in point_layer.getFeatures():
    point_geom = point_feature.geometry()
    point = point_geom.asPoint()

    # Step 1: find candidate lines within a 10 m buffer
    candidate_ids = spatial_index.intersects(
        point_geom.buffer(10, 8).boundingBox()
    )

    if not candidate_ids:
        messagee = f"[WARNING] Point ID {point_feature.id()} had no nearby lines. Point will be dropped."
        QgsMessageLog.logMessage(messagee)
        print(messagee)
        continue  # point is removed 

    # Step 2: compute nearest snapped point on candidate lines
    best_distance = float("inf")
    best_point_geom = None

    for fid in candidate_ids:
        line_feature = next(
            line_layer.getFeatures(QgsFeatureRequest(fid))
        )
        line_geom = line_feature.geometry()

        snapped_point = line_geom.nearestPoint(point_geom)
        distance = snapped_point.distance(point_geom)

        if distance < best_distance:
            best_distance = distance
            best_point_geom = snapped_point

    # Step 3: create new snapped feature (endast om snapping lyckats)
    if best_point_geom is not None:  # <-- litet säkerhetsbälte
        new_feature = QgsFeature(output_layer.fields())
        new_feature.setGeometry(best_point_geom)
        new_feature.setAttributes(point_feature.attributes())
        provider.addFeature(new_feature)

# Add result to project
QgsProject.instance().addMapLayer(output_layer)
print("Snapping done!")
