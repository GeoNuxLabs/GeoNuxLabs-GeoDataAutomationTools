"""
Extract hydrological line segments between paired points using QGIS and 
topology‑aware geometry processing.

This script:
- Reads two point layers representing start and stop locations along watercourses.
- Matches point pairs using a shared ID field.
- Identifies the correct watercourse for each point based on spatial proximity.
- Dissolves all line features sharing the same watercourse ID into a single 
  continuous geometry.
- Projects both points onto the dissolved watercourse geometry.
- Extracts the exact line segment between the projected positions, even across 
  feature boundaries and junctions.
- Skips pairs where points fall on different watercourses or outside tolerance.
- Outputs all extracted segments as a new in‑memory LineString layer.

Author: GeoNuxLabs
Repository: https://github.com/GeoNuxLabs/GeoNuxLabs-GeoDataAutomationTools
Requirements:
    - QGIS Python environment
    - QGIS geometry engine (curveSubstring, spatial index)
"""

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsFeatureRequest,
    QgsSpatialIndex,
    QgsMessageLog
)

# Config
ID_FIELD = "ID"          # point ID field
WATER_ID_FIELD = "VDRID"  # watercourse ID field 
MAX_POINT_LINE_DIST = 0.5  # max distance (m) to accept point as "on" line

# Input layers
point_layer_1 = QgsProject.instance().mapLayersByName(
    "path"
)[0]
point_layer_2 = QgsProject.instance().mapLayersByName(
    "path"
)[0]
water_layer = QgsProject.instance().mapLayersByName("path")[0]

# Output layer (memory)
output_layer = QgsVectorLayer(
    f"LineString?crs={water_layer.crs().authid()}",
    "segmented_waterlines",
    "memory"
)
provider = output_layer.dataProvider()
provider.addAttributes(point_layer_1.fields())
output_layer.updateFields()

# Spatial index for water layer
water_index = QgsSpatialIndex(water_layer.getFeatures())

# Index for point layer 2 by stable ID
point2_index = {f[ID_FIELD]: f for f in point_layer_2.getFeatures()}


def extract_subcurve(geom, start_m, end_m):
    """
    Extract a subcurve between two m-values from any line geometry.
    Supports LineString, MultiLineString, CompoundCurve and MultiCurve.
    """
    result_parts = []

    for part in geom.constParts():
        curve = part
        part_length = curve.length()

        if end_m <= 0:
            break

        if start_m >= part_length:
            start_m -= part_length
            end_m -= part_length
            continue

        local_start = max(0, start_m)
        local_end = min(part_length, end_m)

        subcurve = curve.curveSubstring(local_start, local_end)
        result_parts.append(QgsGeometry(subcurve))

        start_m -= part_length
        end_m -= part_length

    if not result_parts:
        return QgsGeometry()

    if len(result_parts) == 1:
        return result_parts[0]

    return QgsGeometry.unaryUnion(result_parts)


def find_water_id_for_point(point_geom):
    """
    Find water ID for the line the point lies on (or very close to).
    Uses spatial index and distance check.
    """
    bbox = point_geom.boundingBox()
    candidate_ids = water_index.intersects(bbox)

    best_feat = None
    best_dist = float("inf")

    for fid in candidate_ids:
        request = QgsFeatureRequest(fid)
        for feat in water_layer.getFeatures(request):
            dist = feat.geometry().distance(point_geom)
            if dist < best_dist:
                best_dist = dist
                best_feat = feat

    if best_feat is None:
        return None, None

    if best_dist > MAX_POINT_LINE_DIST:
        return None, best_dist

    return best_feat[WATER_ID_FIELD], best_dist


# Build dissolved geometry per watercourse ID
water_geoms_by_id = {}

for feat in water_layer.getFeatures():
    wid = feat[WATER_ID_FIELD]
    geom = feat.geometry()
    if wid not in water_geoms_by_id:
        water_geoms_by_id[wid] = QgsGeometry(geom)
    else:
        water_geoms_by_id[wid] = water_geoms_by_id[wid].combine(geom)


for point_feature_1 in point_layer_1.getFeatures():
    if ID_FIELD not in point_feature_1.fields().names():
        msg = f"[ERROR] ID field '{ID_FIELD}' not found in point layer 1."
        QgsMessageLog.logMessage(msg)
        print(msg)
        break

    feature_id = point_feature_1[ID_FIELD]

    if feature_id not in point2_index:
        msg = (
            f"[WARNING] ID {feature_id} missing in point layer 2. "
            f"Skipping pair."
        )
        QgsMessageLog.logMessage(msg)
        print(msg)
        continue

    point_feature_2 = point2_index[feature_id]

    geom1 = point_feature_1.geometry()
    geom2 = point_feature_2.geometry()

    if geom1 is None or geom1.isEmpty() or geom2 is None or geom2.isEmpty():
        msg = (
            f"[WARNING] Empty geometry for ID {feature_id} in point layers. "
            f"Skipping pair."
        )
        QgsMessageLog.logMessage(msg)
        print(msg)
        continue

    water_id_1, dist1 = find_water_id_for_point(geom1)
    water_id_2, dist2 = find_water_id_for_point(geom2)

    if water_id_1 is None or water_id_2 is None:
        msg = (
            f"[WARNING] No valid water ID found for ID {feature_id} "
            f"(dist1={dist1}, dist2={dist2}). Skipping pair."
        )
        QgsMessageLog.logMessage(msg)
        print(msg)
        continue

    if water_id_1 != water_id_2:
        msg = (
            f"[WARNING] Start/stop for ID {feature_id} lie on different "
            f"water IDs ({water_id_1} vs {water_id_2}). Skipping pair."
        )
        QgsMessageLog.logMessage(msg)
        print(msg)
        continue

    water_geom = water_geoms_by_id.get(water_id_1)
    if water_geom is None or water_geom.isEmpty():
        msg = (
            f"[WARNING] Empty dissolved water geometry for water ID "
            f"{water_id_1} (point ID {feature_id}). Skipping."
        )
        QgsMessageLog.logMessage(msg)
        print(msg)
        continue

    p1 = QgsPointXY(geom1.asPoint())
    p2 = QgsPointXY(geom2.asPoint())

    proj1 = water_geom.lineLocatePoint(QgsGeometry.fromPointXY(p1))
    proj2 = water_geom.lineLocatePoint(QgsGeometry.fromPointXY(p2))

    if proj1 < 0 or proj2 < 0:
        msg = (
            f"[WARNING] Projection failed for ID {feature_id} on "
            f"water ID {water_id_1}. Skipping."
        )
        QgsMessageLog.logMessage(msg)
        print(msg)
        continue

    start_m = min(proj1, proj2)
    end_m = max(proj1, proj2)

    segment = extract_subcurve(water_geom, start_m, end_m)

    if segment is None or segment.isEmpty():
        msg = (
            f"[WARNING] Empty segment for ID {feature_id} on "
            f"water ID {water_id_1}. Skipping."
        )
        QgsMessageLog.logMessage(msg)
        print(msg)
        continue

    new_feature = QgsFeature(output_layer.fields())
    new_feature.setGeometry(segment)
    new_feature.setAttributes(point_feature_1.attributes())
    provider.addFeature(new_feature)

QgsProject.instance().addMapLayer(output_layer)
print("Line segments between points extracted.")