import pytest
from backend.app.spatial_engine import (
    haversine_distance_km,
    calculate_bearing_deg,
    is_point_in_polygon,
    generate_corridor_polygon,
    evaluate_threat_for_user
)
from backend.app.models import ThreatEvent, ThreatType, ThreatScope, ThreatUrgency, ActionType
from backend.app.gazetteer import KYIV_DISTRICTS


def test_haversine_distance():
    kyiv_center = (50.4501, 30.5234)
    obolon_center = (50.505, 30.498)
    
    dist_same = haversine_distance_km(kyiv_center, kyiv_center)
    assert dist_same == 0.0

    dist = haversine_distance_km(kyiv_center, obolon_center)
    assert 5.0 < dist < 8.0  # ~6.3 km


def test_calculate_bearing():
    point_north = (51.0, 30.0)
    point_south = (50.0, 30.0)
    
    # Heading South
    bearing_south = calculate_bearing_deg(point_north, point_south)
    assert pytest.approx(bearing_south, abs=1.0) == 180.0

    # Heading North
    bearing_north = calculate_bearing_deg(point_south, point_north)
    assert pytest.approx(bearing_north, abs=1.0) == 0.0


def test_point_in_polygon():
    obolon_poly = KYIV_DISTRICTS["Obolonskyi"]["polygon"]
    obolon_point = (50.505, 30.498)
    pozniaky_point = (50.398, 30.635)

    assert is_point_in_polygon(obolon_point, obolon_poly) is True
    assert is_point_in_polygon(pozniaky_point, obolon_poly) is False


def test_corridor_polygon_generation():
    vyshhorod = (50.584, 30.489)
    obolon = (50.505, 30.498)
    corridor = generate_corridor_polygon(vyshhorod, obolon, buffer_km=3.0)

    assert len(corridor) >= 4
    # Test midpoint is inside corridor
    midpoint = ((vyshhorod[0] + obolon[0]) / 2, (vyshhorod[1] + obolon[1]) / 2)
    assert is_point_in_polygon(midpoint, corridor) is True


def test_user_evaluation_ballistics():
    ballistic_threat = ThreatEvent(
        event_id="evt_test_ballistic",
        threat_type=ThreatType.BALLISTIC,
        scope=ThreatScope.CITY_WIDE,
        urgency=ThreatUrgency.CRITICAL,
        title="Загроза балістики: Київ!",
        description="Пуск балістики",
        target_districts=["ALL"],
        timestamp_utc=1000
    )

    # User with ballistics enabled
    res1 = evaluate_threat_for_user(
        threat=ballistic_threat,
        user_districts=["Obolonskyi"],
        ballistics_enabled=True
    )
    assert res1.action == ActionType.TRIGGER_URGENT_ALARM
    assert res1.sound_channel == "BALLISTIC_ALERT_CHANNEL"

    # User with ballistics disabled
    res2 = evaluate_threat_for_user(
        threat=ballistic_threat,
        user_districts=["Darnytskyi"],
        ballistics_enabled=False
    )
    assert res2.action == ActionType.SILENCE_MUTED_BY_USER
    assert res2.sound_channel is None


def test_user_evaluation_uav_district_isolation():
    uav_obolon = ThreatEvent(
        event_id="evt_uav_obolon",
        threat_type=ThreatType.UAV_SHAHED,
        scope=ThreatScope.SPATIAL_POLYGON,
        urgency=ThreatUrgency.CRITICAL,
        title="БПЛА на Оболонь",
        description="Шахед з Вишгорода курсом на Оболонь",
        target_districts=["Obolonskyi"],
        timestamp_utc=1000
    )

    # User A (Obolon)
    res_a = evaluate_threat_for_user(
        threat=uav_obolon,
        user_districts=["Obolonskyi"],
        user_location=(50.505, 30.498)
    )
    assert res_a.action == ActionType.TRIGGER_DISTRICT_ALARM
    assert res_a.sound_channel == "UAV_SIREN_CHANNEL"

    # User B (Pozniaky) -> MUST BE SILENT
    res_b = evaluate_threat_for_user(
        threat=uav_obolon,
        user_districts=["Darnytskyi"],
        user_location=(50.398, 30.635)
    )
    assert res_b.action == ActionType.IGNORE_OUT_OF_ZONE
    assert res_b.sound_channel is None


def test_user_evaluation_all_clear():
    # Local Clear for Obolon
    clear_obolon = ThreatEvent(
        event_id="evt_clear_obolon",
        threat_type=ThreatType.ALL_CLEAR,
        scope=ThreatScope.SPATIAL_POLYGON,
        urgency=ThreatUrgency.INFO,
        title="Оболонь чисто",
        description="Ціль збито",
        target_districts=["Obolonskyi"],
        timestamp_utc=1000
    )

    res_a = evaluate_threat_for_user(clear_obolon, user_districts=["Obolonskyi"])
    assert res_a.action == ActionType.TRIGGER_ALL_CLEAR

    res_b = evaluate_threat_for_user(clear_obolon, user_districts=["Darnytskyi"])
    assert res_b.action == ActionType.IGNORE_OUT_OF_ZONE

    # General Clear for Kyiv
    clear_general = ThreatEvent(
        event_id="evt_clear_all",
        threat_type=ThreatType.ALL_CLEAR,
        scope=ThreatScope.CITY_WIDE,
        urgency=ThreatUrgency.INFO,
        title="Відбій по Києву",
        description="Відбій тривоги",
        target_districts=["ALL"],
        timestamp_utc=1000
    )

    assert evaluate_threat_for_user(clear_general, ["Obolonskyi"]).action == ActionType.TRIGGER_ALL_CLEAR
    assert evaluate_threat_for_user(clear_general, ["Darnytskyi"]).action == ActionType.TRIGGER_ALL_CLEAR
