"""
JalDrishti AI — Geospatial & Spatial Query Utility Engine
Handles coordinate validation, point-in-polygon containment,
bounding box intersection, and distance calculations via Shapely.
"""

import math
from typing import Tuple, Optional, List, Dict, Any
from shapely.geometry import shape, Point
from shapely.errors import ShapelyError

# Approximate Geographic Bounding Box for the Republic of India
# Latitude: 6.5° N (Indira Point) to 37.5° N (Siachen)
# Longitude: 68.0° E (Ghuar Mota, Gujarat) to 97.5° E (Kibithu, Arunachal)
INDIA_BBOX = {
    "min_lat": 6.5,
    "max_lat": 37.5,
    "min_lng": 68.0,
    "max_lng": 97.5,
}

def validate_coordinates(latitude: float, longitude: float) -> Tuple[bool, Optional[str]]:
    """
    Validates global geographic latitude (-90 to 90) and longitude (-180 to 180).
    Returns (is_valid, error_message).
    """
    if latitude is None or longitude is None:
        return False, "Latitude and longitude must not be null."
    
    if not (-90.0 <= latitude <= 90.0):
        return False, f"Invalid latitude: {latitude}. Latitude must be between -90.0 and 90.0 degrees."
    
    if not (-180.0 <= longitude <= 180.0):
        return False, f"Invalid longitude: {longitude}. Longitude must be between -180.0 and 180.0 degrees."
    
    return True, None

def is_in_india_bounds(latitude: float, longitude: float) -> bool:
    """Checks if coordinates fall within India's territorial bounding box."""
    return (
        INDIA_BBOX["min_lat"] <= latitude <= INDIA_BBOX["max_lat"] and
        INDIA_BBOX["min_lng"] <= longitude <= INDIA_BBOX["max_lng"]
    )

def point_in_geojson_geometry(latitude: float, longitude: float, geometry_dict: Dict[str, Any]) -> bool:
    """
    Determines whether GPS point (latitude, longitude) is contained within
    the provided GeoJSON Polygon or MultiPolygon geometry.
    Note: GeoJSON uses (longitude, latitude) coordinate order.
    """
    if not geometry_dict:
        return False
    
    try:
        geom = shape(geometry_dict)
        pt = Point(longitude, latitude)
        return geom.contains(pt) or geom.touches(pt)
    except (ShapelyError, ValueError, KeyError):
        return False

def bbox_intersects(bbox_a: List[float], bbox_b: List[float]) -> bool:
    """
    Checks if two bounding boxes intersect.
    Format: [min_lng, min_lat, max_lng, max_lat]
    """
    if len(bbox_a) < 4 or len(bbox_b) < 4:
        return False
    
    a_min_lng, a_min_lat, a_max_lng, a_max_lat = bbox_a
    b_min_lng, b_min_lat, b_max_lng, b_max_lat = bbox_b
    
    # Overlap test
    if a_max_lng < b_min_lng or a_min_lng > b_max_lng:
        return False
    if a_max_lat < b_min_lat or a_min_lat > b_max_lat:
        return False
    
    return True

def point_in_bbox(latitude: float, longitude: float, bbox: List[float]) -> bool:
    """Checks if GPS point is within [min_lng, min_lat, max_lng, max_lat]."""
    if len(bbox) < 4:
        return False
    min_lng, min_lat, max_lng, max_lat = bbox
    return (min_lng <= longitude <= max_lng) and (min_lat <= latitude <= max_lat)

def calculate_haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes Great Circle Haversine distance in kilometers between two GPS points.
    """
    R = 6371.0 # Earth mean radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 3)

def calculate_geojson_centroid(geometry_dict: Dict[str, Any]) -> Tuple[float, float]:
    """
    Computes the geometric centroid (latitude, longitude) of a GeoJSON Polygon/MultiPolygon.
    """
    try:
        geom = shape(geometry_dict)
        centroid = geom.centroid
        return round(centroid.y, 6), round(centroid.x, 6) # (lat, lng)
    except Exception:
        return 0.0, 0.0

def validate_geojson_geometry(geometry_dict: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[List[float]]]:
    """
    Validates a GeoJSON geometry dictionary using Shapely.
    Checks:
    - Valid dictionary structure and 'type' + 'coordinates'
    - Coordinate ranges (-180 to 180, -90 to 90)
    - Valid topology (self-intersections, closed rings)
    Returns: (is_valid, error_message, bounds [min_lng, min_lat, max_lng, max_lat])
    """
    if not isinstance(geometry_dict, dict):
        return False, "Geometry must be a valid GeoJSON dictionary object.", None
    
    geom_type = geometry_dict.get("type")
    coordinates = geometry_dict.get("coordinates")
    if not geom_type or coordinates is None:
        return False, "GeoJSON geometry missing 'type' or 'coordinates' property.", None

    valid_types = ["Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon", "GeometryCollection"]
    if geom_type not in valid_types:
        return False, f"Unsupported GeoJSON geometry type: {geom_type}. Must be one of {valid_types}.", None

    try:
        geom = shape(geometry_dict)
        if not geom.is_valid:
            # Check reason for invalidity
            from shapely.validation import explain_validity
            reason = explain_validity(geom)
            return False, f"Invalid geometry topology: {reason}", None
        
        if geom.is_empty:
            return False, "Geometry is empty.", None

        minx, miny, maxx, maxy = geom.bounds
        # Bounds check
        if not (-180.0 <= minx <= 180.0 and -180.0 <= maxx <= 180.0 and -90.0 <= miny <= 90.0 and -90.0 <= maxy <= 90.0):
            return False, f"Geometry coordinates out of geographic WGS84 range: [{minx}, {miny}, {maxx}, {maxy}]", None

        bounds = [round(minx, 6), round(miny, 6), round(maxx, 6), round(maxy, 6)]
        return True, None, bounds
    except Exception as e:
        return False, f"Failed to parse GeoJSON geometry: {str(e)}", None

def calculate_geometry_bounds(geometry_dict: Dict[str, Any]) -> List[float]:
    """Computes [min_lng, min_lat, max_lng, max_lat] for a GeoJSON geometry."""
    try:
        geom = shape(geometry_dict)
        minx, miny, maxx, maxy = geom.bounds
        return [round(minx, 6), round(miny, 6), round(maxx, 6), round(maxy, 6)]
    except Exception:
        return [0.0, 0.0, 0.0, 0.0]

def check_point_in_watershed(latitude: float, longitude: float, watershed_boundary: Dict[str, Any]) -> bool:
    """Checks if a point is contained within the watershed polygon boundary."""
    return point_in_geojson_geometry(latitude, longitude, watershed_boundary)

