import pytest
import time
from backend.app.nlp_parser import nlp_parser
from backend.app.models import ThreatType, ThreatScope, ThreatUrgency


def test_ballistic_threat_detection():
    cases = [
        "Київ — загроза балістики з Брянщини!",
        "Швидкісна ціль на Київ з півночі! В укриття!",
        "Зафіксовано пуск балістики (Іскандер-М) у бік столиці!",
        "Пуск Кинджала з МіГ-31К в напрямку Києва!"
    ]
    for text in cases:
        resp = nlp_parser.parse(text)
        assert resp.threat_event is not None, f"Failed to detect threat in: {text}"
        assert resp.threat_event.threat_type == ThreatType.BALLISTIC
        assert resp.threat_event.scope == ThreatScope.CITY_WIDE
        assert resp.threat_event.urgency == ThreatUrgency.CRITICAL
        assert "ALL" in resp.threat_event.target_districts


def test_uav_district_and_suburb_extraction():
    # Obolon + Vyshhorod
    resp1 = nlp_parser.parse("Шахед з Вишгорода курсом на Оболонь")
    assert resp1.threat_event is not None
    assert resp1.threat_event.threat_type == ThreatType.UAV_SHAHED
    assert "Obolonskyi" in resp1.threat_event.target_districts
    assert resp1.threat_event.corridor_polygon is not None
    assert resp1.threat_event.vector_bearing_deg == 180.0

    # Darnytsia + Brovary
    resp2 = nlp_parser.parse("2 БПЛА через Бровари на Дарницький район")
    assert resp2.threat_event is not None
    assert resp2.threat_event.threat_type == ThreatType.UAV_SHAHED
    assert "Darnytskyi" in resp2.threat_event.target_districts

    # Pozniaky / Osokorky + Boryspil
    resp3 = nlp_parser.parse("Шахед з Борисполя курсом на Позняки та Осокорки")
    assert resp3.threat_event is not None
    assert resp3.threat_event.threat_type == ThreatType.UAV_SHAHED
    assert "Darnytskyi" in resp3.threat_event.target_districts

    # Podil / Kurenivka
    resp4 = nlp_parser.parse("БПЛА з півночі рухається в напрямку Подолу та Куренівки")
    assert resp4.threat_event is not None
    assert resp4.threat_event.threat_type == ThreatType.UAV_SHAHED
    assert "Podilskyi" in resp4.threat_event.target_districts

    # Sviatoshyn + Irpin
    resp5 = nlp_parser.parse("Дрон через Ірпінь в напрямку Святошинського району")
    assert resp5.threat_event is not None
    assert resp5.threat_event.threat_type == ThreatType.UAV_SHAHED
    assert "Sviatoshynskyi" in resp5.threat_event.target_districts


def test_all_clear_detection():
    # City-wide all-clear
    resp_full = nlp_parser.parse("Відбій загрози по місту Києву")
    assert resp_full.threat_event is not None
    assert resp_full.threat_event.threat_type == ThreatType.ALL_CLEAR
    assert "ALL" in resp_full.threat_event.target_districts

    # Local district all-clear
    resp_local = nlp_parser.parse("Оболонь — чисто, ціль збито")
    assert resp_local.threat_event is not None
    assert resp_local.threat_event.threat_type == ThreatType.ALL_CLEAR
    assert "Obolonskyi" in resp_local.threat_event.target_districts

    # Pozniaky local clear
    resp_pozniaky = nlp_parser.parse("Позняки / Дарницький район — ціль ліквідовано, чисто")
    assert resp_pozniaky.threat_event is not None
    assert resp_pozniaky.threat_event.threat_type == ThreatType.ALL_CLEAR
    assert "Darnytskyi" in resp_pozniaky.threat_event.target_districts


def test_transit_outside_city():
    resp1 = nlp_parser.parse("БПЛА на півдні Київщини, курс на Білу Церкву")
    assert resp1.threat_event is not None
    assert resp1.threat_event.threat_type == ThreatType.UAV_SHAHED
    assert resp1.threat_event.target_districts == []

    resp2 = nlp_parser.parse("Шахеди повз Фастів на Житомирщину, для Києва загрози немає")
    assert resp2.threat_event is not None
    assert resp2.threat_event.threat_type == ThreatType.UAV_SHAHED
    assert resp2.threat_event.target_districts == []


def test_edge_cases():
    # Empty input
    resp_empty = nlp_parser.parse("")
    assert resp_empty.threat_event is None

    # Irrelevant chat
    resp_irrelevant = nlp_parser.parse("Доброго ранку всім, гарного спокійного дня!")
    assert resp_irrelevant.threat_event is None


def test_latency_performance_benchmark():
    test_phrase = "Шахед з Вишгорода курсом на Оболонь через Дніпро"
    
    # Warmup
    for _ in range(50):
        nlp_parser.parse(test_phrase)

    iterations = 500
    t0 = time.perf_counter()
    for _ in range(iterations):
        nlp_parser.parse(test_phrase)
    total_time = (time.perf_counter() - t0) * 1000.0  # ms
    avg_latency_ms = total_time / iterations

    print(f"\nAverage NLP parse latency: {avg_latency_ms:.4f} ms")
    assert avg_latency_ms < 5.0, f"Average latency {avg_latency_ms} ms exceeds 5ms threshold"
