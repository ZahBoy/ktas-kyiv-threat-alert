"""Spatial calculation engine using Shapely and WGS-84 geodesic math.

Handles corridor polygon generation, point-in-polygon containment,
distance, and Zero-Knowledge client evaluation logic.
"""
import math
from typing import List, Tuple, Optional
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import unary_union

from .models import ThreatEvent, ThreatType, ActionType, EvaluationResult, Coordinate
from .gazetteer import KYIV_DISTRICTS, KYIV_CENTER, KYIV_SUBURBS


def haversine_distance_km(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """Calculate the great-circle distance between two points in km (Haversine formula)."""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    r = 6371.0  # Earth's radius in kilometers
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def calculate_bearing_deg(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """Calculate the initial compass bearing from coord1 to coord2 in degrees (0..360)."""
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    
    d_lon = lon2 - lon1
    y = math.sin(d_lon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)
    bearing = math.degrees(math.atan2(y, x))
    return (bearing + 360.0) % 360.0


def is_point_in_polygon(point: Tuple[float, float], polygon_coords: List[List[float]]) -> bool:
    """Check if (lat, lon) is strictly inside or on the boundary of polygon."""
    if not polygon_coords or len(polygon_coords) < 3:
        return False
    # In Shapely (x, y) = (lon, lat)
    shapely_poly = Polygon([(p[1], p[0]) for p in polygon_coords])
    shapely_point = Point(point[1], point[0])
    return shapely_poly.contains(shapely_point) or shapely_poly.touches(shapely_point)


def generate_corridor_polygon(
    start_point: Tuple[float, float],
    end_point: Tuple[float, float],
    buffer_km: float = 3.0
) -> List[List[float]]:
    """Generate a buffered flight corridor polygon between start and end coordinates.
    
    Returns list of [lat, lon] coordinates.
    """
    # Approximate degree conversion at lat 50.45N
    # 1 deg lat ~ 111.2 km, 1 deg lon ~ 70.8 km
    km_per_lat = 111.2
    km_per_lon = 70.8
    
    buffer_deg_lat = buffer_km / km_per_lat
    buffer_deg_lon = buffer_km / km_per_lon
    avg_deg_buffer = (buffer_deg_lat + buffer_deg_lon) / 2.0
    
    # Shapely LineString with (lon, lat)
    line = LineString([(start_point[1], start_point[0]), (end_point[1], end_point[0])])
    buffered = line.buffer(avg_deg_buffer, cap_style=1, join_style=1)
    
    # Extract coordinates in [lat, lon] order
    coords = []
    for lon, lat in buffered.exterior.coords:
        coords.append([round(lat, 5), round(lon, 5)])
    return coords


def get_district_polygon(district_name: str) -> Optional[List[List[float]]]:
    """Retrieve bounding polygon for a given district name."""
    if district_name in KYIV_DISTRICTS:
        return KYIV_DISTRICTS[district_name]["polygon"]
    return None


def get_combined_polygon_for_districts(district_names: List[str]) -> List[List[float]]:
    """Compute union polygon of specified districts."""
    polys = []
    for d in district_names:
        if d in KYIV_DISTRICTS:
            poly_coords = [(p[1], p[0]) for p in KYIV_DISTRICTS[d]["polygon"]]
            polys.append(Polygon(poly_coords))
    
    if not polys:
        return []
    
    union_poly = unary_union(polys)
    if union_poly.geom_type == 'MultiPolygon':
        # Return exterior of the largest polygon
        largest = max(union_poly.geoms, key=lambda p: p.area)
        return [[round(lat, 5), round(lon, 5)] for lon, lat in largest.exterior.coords]
    elif union_poly.geom_type == 'Polygon':
        return [[round(lat, 5), round(lon, 5)] for lon, lat in union_poly.exterior.coords]
    return []


def evaluate_threat_for_user(
    threat: ThreatEvent,
    user_districts: List[str],
    user_location: Optional[Tuple[float, float]] = None,
    ballistics_enabled: bool = True,
    danger_radius_km: float = 5.0,
    respect_vector: bool = True
) -> EvaluationResult:
    """Client-side Zero-Knowledge Threat Evaluator.
    
    Evaluates whether the device should trigger an alarm, warning, clear, or remain silent.
    """
    # 1. BALLISTIC Threat: City-Wide Instant Broadcast
    if threat.threat_type == ThreatType.BALLISTIC:
        if not ballistics_enabled:
            return EvaluationResult(
                action=ActionType.SILENCE_MUTED_BY_USER,
                reason="Користувач вимкнув сповіщення про балістику в налаштуваннях",
                sound_channel=None
            )
        return EvaluationResult(
            action=ActionType.TRIGGER_URGENT_ALARM,
            reason="Миттєва загальноміська загроза балістики по Києву!",
            sound_channel="BALLISTIC_ALERT_CHANNEL"
        )
    
    # 2. ALL_CLEAR Signal
    if threat.threat_type == ThreatType.ALL_CLEAR:
        # Full city all-clear
        if "ALL" in threat.target_districts or not threat.target_districts:
            return EvaluationResult(
                action=ActionType.TRIGGER_ALL_CLEAR,
                reason="Загальний відбій тривоги по місту Києву",
                sound_channel="ALL_CLEAR_CHANNEL"
            )
        # Local district all-clear
        matched_clear = [d for d in threat.target_districts if d in user_districts]
        if matched_clear:
            return EvaluationResult(
                action=ActionType.TRIGGER_ALL_CLEAR,
                reason=f"Локальний відбій для вашого району: {', '.join(matched_clear)}",
                sound_channel="ALL_CLEAR_CHANNEL"
            )
        # Location in polygon for clear
        if user_location and threat.corridor_polygon and is_point_in_polygon(user_location, threat.corridor_polygon):
            return EvaluationResult(
                action=ActionType.TRIGGER_ALL_CLEAR,
                reason="Локальний відбій у вашій зоні",
                sound_channel="ALL_CLEAR_CHANNEL"
            )
        return EvaluationResult(
            action=ActionType.IGNORE_OUT_OF_ZONE,
            reason="Локальний відбій для іншого району міста",
            sound_channel=None
        )
    
    # 3. UAV / Shahed Threats (Hyperlocal Filtering)
    if threat.threat_type in (ThreatType.UAV_SHAHED, ThreatType.CRUISE_MISSILE):
        # Check if transit threat outside city
        if not threat.target_districts and not threat.corridor_polygon:
            return EvaluationResult(
                action=ActionType.IGNORE_OUT_OF_ZONE,
                reason="Ціль рухається за межами Києва транзитом, загрози місту немає",
                sound_channel=None
            )
        
        # Check district match
        matched_districts = [d for d in threat.target_districts if d in user_districts]
        if matched_districts:
            return EvaluationResult(
                action=ActionType.TRIGGER_DISTRICT_ALARM,
                reason=f"БПЛА зафіксовано курсом на ваш район ({', '.join(matched_districts)})",
                sound_channel="UAV_SIREN_CHANNEL"
            )
        
        # Check GPS coordinate evaluation (Zero-Knowledge)
        if user_location:
            # Check inside corridor polygon
            if threat.corridor_polygon and is_point_in_polygon(user_location, threat.corridor_polygon):
                return EvaluationResult(
                    action=ActionType.TRIGGER_DISTRICT_ALARM,
                    reason="Ваша локація знаходиться безпосередньо у векторі загрози",
                    sound_channel="UAV_SIREN_CHANNEL"
                )
            
            # Check proximity to nearest target district center
            min_dist = float('inf')
            for target_d in threat.target_districts:
                if target_d in KYIV_DISTRICTS:
                    dist = haversine_distance_km(user_location, KYIV_DISTRICTS[target_d]["center"])
                    if dist < min_dist:
                        min_dist = dist
            
            if min_dist <= danger_radius_km:
                return EvaluationResult(
                    action=ActionType.TRIGGER_DISTRICT_ALARM,
                    reason=f"Ціль у критичному радіусі ({min_dist:.1f} км <= {danger_radius_km} км)",
                    distance_km=round(min_dist, 2),
                    sound_channel="UAV_SIREN_CHANNEL"
                )
            elif min_dist <= 15.0 and respect_vector:
                return EvaluationResult(
                    action=ActionType.TRIGGER_WARNING,
                    reason=f"Ціль на підльоті в сусідній сектор ({min_dist:.1f} км)",
                    distance_km=round(min_dist, 2),
                    sound_channel="WARNING_CHANNEL"
                )
        
        # Out of zone
        return EvaluationResult(
            action=ActionType.IGNORE_OUT_OF_ZONE,
            reason="Ціль в іншому районі міста, для вашого сектора небезпеки немає",
            sound_channel=None
        )
    
    return EvaluationResult(
        action=ActionType.IGNORE_OUT_OF_ZONE,
        reason="Невідомий або непостійний тип загрози",
        sound_channel=None
    )
