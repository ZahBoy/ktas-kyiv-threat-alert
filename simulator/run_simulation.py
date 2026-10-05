"""Interactive End-to-End Simulation Harness for Kyiv Threat Alert System (KTAS).

Demonstrates fast-path NLP parsing (< 5ms), spatial corridor generation,
and Zero-Knowledge client-side threat isolation for Agentic AI School defense.
"""
import sys
import os
import json
import time
from pathlib import Path

# Ensure root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.nlp_parser import FastNLPParser
from backend.app.spatial_engine import evaluate_threat_for_user
from backend.app.models import ActionType, ThreatType


# Ensure UTF-8 output on Windows terminal
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ANSI Colors for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def format_action(action: ActionType) -> str:
    """Format action enum into colorized human-readable label."""
    if action == ActionType.TRIGGER_URGENT_ALARM:
        return f"{RED}{BOLD}[URGENT ALARM]{RESET}"
    elif action == ActionType.TRIGGER_DISTRICT_ALARM:
        return f"{YELLOW}{BOLD}[DISTRICT SIREN]{RESET}"
    elif action == ActionType.TRIGGER_WARNING:
        return f"{CYAN}[WARNING]{RESET}"
    elif action == ActionType.TRIGGER_ALL_CLEAR:
        return f"{GREEN}[ALL CLEAR]{RESET}"
    elif action == ActionType.SILENCE_MUTED_BY_USER:
        return f"{RESET}[MUTED (USER)]"
    else:
        return f"{RESET}[SILENT (OUT)]"



def main():
    print(f"\n{BOLD}{CYAN}================================================================================={RESET}")
    print(f"{BOLD}{CYAN}      KYIV THREAT ALERT SYSTEM (KTAS) — END-TO-END SIMULATION HARNESS           {RESET}")
    print(f"{BOLD}{CYAN}            Zero-Knowledge Spatial Threat Isolation & Latency Benchmark          {RESET}")
    print(f"{BOLD}{CYAN}================================================================================={RESET}\n")

    dataset_path = ROOT_DIR / "simulator" / "test_dataset.json"
    if not dataset_path.exists():
        print(f"{RED}Error: Dataset not found at {dataset_path}{RESET}")
        sys.exit(1)

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    parser = FastNLPParser()

    # Define Virtual Users for Isolation Testing
    user_a = {
        "name": "Користувач А (Оболонь)",
        "district": ["Obolonskyi"],
        "gps": (50.505, 30.498),
        "ballistics": True,
        "radius_km": 5.0
    }
    user_b = {
        "name": "Користувач Б (Позняки)",
        "district": ["Darnytskyi"],
        "gps": (50.398, 30.635),
        "ballistics": False,  # Muted by user choice
        "radius_km": 5.0
    }

    print(f"{BOLD}Тестові віртуальні профілі:{RESET}")
    print(f"  • {BOLD}{user_a['name']}:{RESET} Район: Оболонь | Балістика: УВІМКНЕНО | GPS: {user_a['gps']}")
    print(f"  • {BOLD}{user_b['name']}:{RESET} Район: Дарницький (Позняки) | Балістика: ВИМКНЕНО | GPS: {user_b['gps']}")
    print("-" * 85)

    latencies = []
    results = []

    print(f"\n{BOLD}{'#':<3} {'Джерело':<16} {'Тип загрози':<16} {'Час':<8} {'Користувач А (Оболонь)':<24} {'Користувач Б (Позняки)':<24}{RESET}")
    print("-" * 95)

    for item in dataset:
        post_id = item["id"]
        text = item["text"]
        channel = item["channel"]

        # 1. Parse using FastNLPParser
        t0 = time.perf_counter()
        parse_resp = parser.parse(text, source_channel=channel)
        dt_ms = (time.perf_counter() - t0) * 1000.0
        latencies.append(dt_ms)

        threat = parse_resp.threat_event
        threat_type_str = threat.threat_type.value if threat else "UNKNOWN"

        # 2. Evaluate for User A (Obolon)
        eval_a = evaluate_threat_for_user(
            threat=threat,
            user_districts=user_a["district"],
            user_location=user_a["gps"],
            ballistics_enabled=user_a["ballistics"],
            danger_radius_km=user_a["radius_km"]
        )

        # 3. Evaluate for User B (Pozniaky)
        eval_b = evaluate_threat_for_user(
            threat=threat,
            user_districts=user_b["district"],
            user_location=user_b["gps"],
            ballistics_enabled=user_b["ballistics"],
            danger_radius_km=user_b["radius_km"]
        )

        action_a_str = format_action(eval_a.action)
        action_b_str = format_action(eval_b.action)

        print(f"{post_id:<3} {channel:<16} {threat_type_str:<16} {dt_ms:5.2f}ms {action_a_str:<32} {action_b_str:<32}")
        print(f"    {BOLD}Текст:{RESET} \"{text}\"")
        if threat and threat.target_districts:
            print(f"    {CYAN}Сектор:{RESET} {', '.join(threat.target_districts)}")
        print()

        results.append({
            "id": post_id,
            "threat": threat,
            "eval_a": eval_a,
            "eval_b": eval_b,
            "latency_ms": dt_ms
        })

    # Performance Metrics
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    min_latency = min(latencies)

    print("=" * 95)
    print(f"\n{BOLD}РЕЗУЛЬТАТИ ТА МЕТРИКИ ПРОДУКТИВНОСТІ:{RESET}")
    print(f"  • Оброблено повідомлень:       {BOLD}{len(dataset)}{RESET}")
    print(f"  • Середній час парсингу NLP:   {GREEN}{BOLD}{avg_latency:.3f} мс{RESET} (Вимога: < 5.0 мс — {'✅ ПРОЙДЕНО' if avg_latency < 5.0 else '❌ ПРОВАЛЕНО'})")
    print(f"  • Максимальний сплеск часу:    {CYAN}{max_latency:.3f} мс{RESET}")
    print(f"  • Мінімальний час:             {CYAN}{min_latency:.3f} мс{RESET}")

    # Functional Invariants Verification
    print(f"\n{BOLD}ВЕРИФІКАЦІЯ КЛЮЧОВИХ БІЗНЕС-ПРАВИЛ:{RESET}")
    
    # Check Ballistics
    ballistics_detected = sum(1 for r in results if r["threat"] and r["threat"].threat_type == ThreatType.BALLISTIC)
    assert ballistics_detected == 4, f"Expected 4 ballistic events, got {ballistics_detected}"
    print(f"  [{GREEN}PASS{RESET}] Виявлення балістики: 4/4 (100% точність, 0 хибних пропусків)")

    # Check Ballistics User Isolation (User A alarm, User B muted by toggle)
    for r in results[:4]:
        assert r["eval_a"].action == ActionType.TRIGGER_URGENT_ALARM, f"User A failed to alarm on ballistic #{r['id']}"
        assert r["eval_b"].action == ActionType.SILENCE_MUTED_BY_USER, f"User B should be muted for ballistic #{r['id']}"
    print(f"  [{GREEN}PASS{RESET}] Балістичне правило: Користувач А отримав УРГЕНТНУ СИРЕНУ; Користувач Б — повна тиша (вимкнув у налаштуваннях)")

    # Check UAV Isolation: Obolon threats (posts 5, 6)
    for r in results[4:6]:
        assert r["eval_a"].action == ActionType.TRIGGER_DISTRICT_ALARM, f"User A failed to alarm on Obolon UAV #{r['id']}"
        assert r["eval_b"].action == ActionType.IGNORE_OUT_OF_ZONE, f"User B wrongly alarmed on Obolon UAV #{r['id']}"
    print(f"  [{GREEN}PASS{RESET}] Ізоляція сектору Оболонь: Користувач А отримав сирену району; Користувач Б не турбувався")

    # Check UAV Isolation: Pozniaky/Darnytsia threats (posts 8, 9)
    for r in results[7:9]:
        assert r["eval_b"].action == ActionType.TRIGGER_DISTRICT_ALARM, f"User B failed to alarm on Darnytsia UAV #{r['id']}"
        assert r["eval_a"].action == ActionType.IGNORE_OUT_OF_ZONE, f"User A wrongly alarmed on Darnytsia UAV #{r['id']}"
    print(f"  [{GREEN}PASS{RESET}] Ізоляція сектору Позняки: Користувач Б отримав сирену району; Користувач А не турбувався")

    # Check Transit threats (posts 12, 13)
    for r in results[11:13]:
        assert r["eval_a"].action == ActionType.IGNORE_OUT_OF_ZONE
        assert r["eval_b"].action == ActionType.IGNORE_OUT_OF_ZONE
    print(f"  [{GREEN}PASS{RESET}] Транзит за межами Києва: обидва користувачі залишилися у тиші")

    # Check Local Clear (post 14)
    r_local_clear = results[13]
    assert r_local_clear["eval_a"].action == ActionType.TRIGGER_ALL_CLEAR
    assert r_local_clear["eval_b"].action == ActionType.IGNORE_OUT_OF_ZONE
    print(f"  [{GREEN}PASS{RESET}] Гіперлокальний відбій (Оболонь): Користувач А отримав відбій; Користувач Б не турбувався")

    # Check Full Clear (post 15)
    r_full_clear = results[14]
    assert r_full_clear["eval_a"].action == ActionType.TRIGGER_ALL_CLEAR
    assert r_full_clear["eval_b"].action == ActionType.TRIGGER_ALL_CLEAR
    print(f"  [{GREEN}PASS{RESET}] Загальноміський відбій: обидва користувачі отримали сигнал про завершення загрози")

    print(f"\n{BOLD}{GREEN}================================================================================={RESET}")
    print(f"{BOLD}{GREEN}           ВСІ ТЕСТИ СИМУЛЯЦІЇ УСПІШНО ПРОЙДЕНО! ГОТОВО ДО ДЕМОНСТРАЦІЇ           {RESET}")
    print(f"{BOLD}{GREEN}================================================================================={RESET}\n")


if __name__ == "__main__":
    main()
