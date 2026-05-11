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
    QgsFeature,
    QgsGeometry,
    QgsField,
    QgsPointXY,
    QgsPoint,
    QgsMessageLog
)
from qgis.PyQt.QtCore import QVariant

# ---- CONFIG ----
ID_FIELD = "ID" # Stable ID field
MAX_DIST = 20 # Points further away will be dropped 
# Input layers
point_layer = QgsProject.instance().mapLayersByName("path")[0]
line_layer = QgsProject.instance().mapLayersByName("path")[0]
# ----------------

# Output layer (memory)
output_layer = QgsVectorLayer(
    f"Point?crs={point_layer.crs().authid()}",
    "snapped_points2",
    "memory"
)
provider = output_layer.dataProvider()
provider.addAttributes(point_layer.fields())
output_layer.updateFields()

# Debug line layer (memory)
debug_layer = QgsVectorLayer(
    f"LineString?crs={point_layer.crs().authid()}",
    "snap_debug_lines",
    "memory"
)
debug_provider = debug_layer.dataProvider()
debug_provider.addAttributes([
    QgsField("pt_id", QVariant.String),
    QgsField("line_fid", QVariant.Int),
    QgsField("seg_idx", QVariant.Int),
    QgsField("dist", QVariant.Double)
])
debug_layer.updateFields()

# Build spatial index for faster line lookup
spatial_index = QgsSpatialIndex(line_layer.getFeatures())


def nearest_segment_info(line_geom, point_geom):
    """
    Compute nearest segment and return:
    - snapped point geometry
    - distance
    - segment index (global index across all parts)
    - segment start/end coordinates
    """

    min_dist = float("inf")
    best_seg_index = None
    best_seg_coords = None
    best_point = None

    seg_counter = 0  # global segment index

    # Extract all parts (handles both LineString and MultiLineString)
    parts = line_geom.constParts()

    for part in parts:
        vertices = list(part.vertices())

        # Iterate through consecutive vertex pairs
        for i in range(len(vertices) - 1):
            # FORCE conversion to QgsPointXY (robust)
            p1 = QgsPointXY(vertices[i].x(), vertices[i].y())
            p2 = QgsPointXY(vertices[i + 1].x(), vertices[i + 1].y())

            segment_geom = QgsGeometry.fromPolylineXY([p1, p2])
            snapped = segment_geom.nearestPoint(point_geom)
            dist = snapped.distance(point_geom)

            if dist < min_dist:
                min_dist = dist
                best_seg_index = seg_counter
                best_seg_coords = (p1, p2)
                best_point = snapped

            seg_counter += 1

    return best_point, min_dist, best_seg_index, best_seg_coords


for point_feature in point_layer.getFeatures():
    point_geom = point_feature.geometry()

    # Fetch stable ID
    try:
        point_id_attr = str(point_feature[ID_FIELD])
    except KeyError:
        point_id_attr = str(point_feature.id())

    # Step 1: find candidate lines within buffer
    candidate_ids = spatial_index.intersects(
        point_geom.buffer(50, 8).boundingBox()
    )

    if not candidate_ids:
        msg = (
            f"[WARNING] Point ID {point_id_attr} had no nearby lines. "
            f"Point will be dropped."
        )
        QgsMessageLog.logMessage(msg)
        print(msg)
        continue

    # Step 2: compute nearest snapped point on candidate lines
    best_distance = float("inf")
    best_point_geom = None
    best_line_fid = None
    best_seg_index = None
    best_seg_coords = None

    for fid in candidate_ids:
        line_feature = next(
            line_layer.getFeatures(QgsFeatureRequest(fid))
        )
        line_geom = line_feature.geometry()

        snapped_point, dist, seg_index, seg_coords = nearest_segment_info(
            line_geom, point_geom
        )

        if dist < best_distance:
            best_distance = dist
            best_point_geom = snapped_point
            best_line_fid = fid
            best_seg_index = seg_index
            best_seg_coords = seg_coords

    # Debug output for each point
    if best_seg_coords and best_point_geom is not None:
        p1, p2 = best_seg_coords
        debug_msg = (
            f"[DEBUG] Point {point_id_attr} → Line {best_line_fid}, "
            f"Segment {best_seg_index}, Dist {best_distance:.2f} m\n"
            f"         Segment coords: ({p1.x():.3f}, {p1.y():.3f}) → "
            f"({p2.x():.3f}, {p2.y():.3f})"
        )
        QgsMessageLog.logMessage(debug_msg)
        print(debug_msg)

        # Convert to QgsPoint for debug line
        debug_geom = QgsGeometry.fromPolyline([
            QgsPoint(point_geom.asPoint().x(), point_geom.asPoint().y()),
            QgsPoint(best_point_geom.asPoint().x(), best_point_geom.asPoint().y())
        ])

        debug_feat = QgsFeature(debug_layer.fields())
        debug_feat.setGeometry(debug_geom)
        debug_feat.setAttributes([
            point_id_attr,
            best_line_fid,
            best_seg_index,
            best_distance
        ])
        debug_provider.addFeature(debug_feat)

    # Step 3: create new snapped feature (only if snapping was successful)
    if best_point_geom is not None and best_distance <= MAX_DIST:
        new_feature = QgsFeature(output_layer.fields())
        new_feature.setGeometry(best_point_geom)
        new_feature.setAttributes(point_feature.attributes())
        provider.addFeature(new_feature)
    else:
        msg = (
            f"[WARNING] Point ID {point_id_attr} is "
            f"{best_distance:.2f} m from nearest line. Dropped."
        )
        QgsMessageLog.logMessage(msg)
        print(msg)

# Add result layers to project
QgsProject.instance().addMapLayer(output_layer)
QgsProject.instance().addMapLayer(debug_layer)

print("Snapping done!")
print("Debug lines added.")
