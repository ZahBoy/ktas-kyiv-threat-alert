"""High-speed deterministic NLP & Toponymic Parser (< 5ms).

Extracts threat types, urgency, trajectory vectors, corridor polygons,
and target Kyiv districts from raw Ukrainian monitor channel posts.
"""
import re
import time
import uuid
from typing import Tuple, List, Optional, Set

from .models import ThreatEvent, ThreatType, ThreatScope, ThreatUrgency, ParseResponse
from .gazetteer import KYIV_DISTRICTS, KYIV_SUBURBS, KYIV_CENTER
from .spatial_engine import generate_corridor_polygon, get_district_polygon, calculate_bearing_deg


# --- PRE-COMPILED REGEX PATTERNS FOR SUB-MILLISECOND MATCHING ---

RE_BALLISTIC = re.compile(
    r"(?:балістик[аиуое]|іскандер(?:-м)?|кинджал|kn-23|швидкісн[а-я]+\s+ціл[ьяі]|загроз[аи]\s+балістики)",
    re.IGNORECASE
)

RE_UAV = re.compile(
    r"(?:шахед[иів]?|шахід[иів]?|бпла|дрон[иів]?|мопед[иів]?|гербер[аи]|безпілотник[иів]?|geran)",
    re.IGNORECASE
)

RE_CRUISE_MISSILE = re.compile(
    r"(?:крилат[аі]\s+ракет[аи]|х-101|х-555|калібр)",
    re.IGNORECASE
)

RE_ALL_CLEAR = re.compile(
    r"(?:відбій|чисто|локаційно\s+втрачено|ціл[ьяі]\s+збит[оа]|ліквідован[оа]|всі\s+цілі\s+знищен[оа])",
    re.IGNORECASE
)

RE_GENERAL_CLEAR = re.compile(
    r"(?:відбій\s+загрози\s+по\s+місту\s+києву|відбій\s+тривоги|відбій\s+по\s+києву|чисто\s+по\s+києву|чисто\s+в\s+києві)",
    re.IGNORECASE
)

# Ukrainian district stems supporting all grammatical cases
DISTRICT_STEMS = {
    "Obolonskyi": [r"оболон\w*", r"мінськ\w*", r"пріорк\w*", r"пущ[а-і]-водиц\w*"],
    "Podilskyi": [r"поділ\w*", r"подол\w*", r"куренівк\w*", r"виноградар\w*", r"вітрян\w*"],
    "Shevchenkivskyi": [r"шевченківськ\w*", r"лук['’]?янівк\w*", r"луцьянівк\w*", r"сирець\w*", r"нивк\w*", r"татарк\w*"],
    "Pecherskyi": [r"печерськ\w*", r"печерськ", r"липк\w*", r"звіринець\w*"],
    "Holosiivskyi": [r"голосі[єі]в\w*", r"теремк\w*", r"демі[єі]вк\w*", r"корчуват\w*", r"пирог[іі]в\w*", r"кита[єі]в\w*"],
    "Solomianskyi": [r"солом['’]?ян\w*", r"соломк\w*", r"відрадн\w*", r"жулян\w*", r"чоколівк\w*"],
    "Sviatoshynskyi": [r"святошин\w*", r"борщагівк\w*", r"академмістечк\w*", r"білич\w*"],
    "Desnianskyi": [r"деснянськ\w*", r"троєщин\w*", r"лісов\w*", r"биківн\w*"],
    "Dniprovskyi": [r"дніпровськ\w*", r"русанівк\w*", r"воскресенк\w*", r"березняк\w*", r"радужн\w*", r"лівобережн\w*"],
    "Darnytskyi": [r"дарниц\w*", r"дарницьк\w*", r"позняк\w*", r"осокорк\w*", r"харківськ\w*", r"бортнич\w*", r"червон\w*\s+хутір\w*"]
}

SUBURB_STEMS = {
    "vyshhorod": [r"вишгород\w*"],
    "khotianivka": [r"хотянівк\w*"],
    "brovary": [r"бровар\w*"],
    "boryspil": [r"борисп[іі]л\w*"],
    "vasylkiv": [r"васильк[іі]в\w*"],
    "obukhiv": [r"обух[іі]в\w*", r"козин\w*"],
    "irpin": [r"ірп[іі]н\w*", r"буч\w*", r"гостомел\w*"],
    "hlevakha": [r"глевах\w*"]
}

TRANSIT_STEMS = [
    r"біл\w*\s+церк\w*", r"фастів\w*", r"фастов\w*", r"переяслав\w*", r"яготин\w*",
    r"миронівк\w*", r"богуслав\w*", r"сквир\w*", r"теті[єі]в\w*",
    r"житомирщин\w*", r"черкащин\w*", r"вінниччин\w*", r"полтавщин\w*", r"чернігівщин\w*"
]


class FastNLPParser:
    """Deterministic fast-path regex and gazetteer parser."""

    def __init__(self):
        # Pre-compile district patterns
        self.district_patterns = {}
        for code, stems in DISTRICT_STEMS.items():
            pattern = r"\b(?:" + "|".join(stems) + r")\b"
            self.district_patterns[code] = re.compile(pattern, re.IGNORECASE)

        # Pre-compile suburb patterns
        self.suburb_patterns = {}
        for code, stems in SUBURB_STEMS.items():
            pattern = r"\b(?:" + "|".join(stems) + r")\b"
            self.suburb_patterns[code] = re.compile(pattern, re.IGNORECASE)

        # Pre-compile transit patterns
        transit_pattern = r"\b(?:" + "|".join(TRANSIT_STEMS) + r")\b"
        self.transit_re = re.compile(transit_pattern, re.IGNORECASE)

    def parse(self, text: str, source_channel: str = "@monitor_war", timestamp_utc: Optional[int] = None) -> ParseResponse:
        """Parse raw text message and return ParseResponse with timing."""
        start_time = time.perf_counter()
        matched_rules: List[str] = []
        clean_text = text.strip()
        ts = timestamp_utc or int(time.time())
        event_id = f"evt_{ts}_{uuid.uuid4().hex[:6]}"

        if not clean_text:
            return ParseResponse(
                threat_event=None,
                parse_time_ms=(time.perf_counter() - start_time) * 1000.0,
                matched_rules=["EMPTY_INPUT"]
            )

        # 1. CHECK ALL_CLEAR FIRST
        if RE_ALL_CLEAR.search(clean_text):
            matched_rules.append("RULE_ALL_CLEAR")
            
            # Check if this is a general city-wide clear
            if RE_GENERAL_CLEAR.search(clean_text) or ("відбій" in clean_text.lower() and "київ" in clean_text.lower()):
                threat = ThreatEvent(
                    event_id=event_id,
                    threat_type=ThreatType.ALL_CLEAR,
                    scope=ThreatScope.CITY_WIDE,
                    urgency=ThreatUrgency.INFO,
                    title="Відбій загрози: Київ",
                    description=clean_text,
                    target_districts=["ALL"],
                    source_channel=source_channel,
                    timestamp_utc=ts,
                    raw_text=clean_text
                )
                return ParseResponse(
                    threat_event=threat,
                    parse_time_ms=(time.perf_counter() - start_time) * 1000.0,
                    matched_rules=matched_rules
                )

            # Check if district-specific clear
            detected_districts = self._extract_districts(clean_text)
            if detected_districts:
                threat = ThreatEvent(
                    event_id=event_id,
                    threat_type=ThreatType.ALL_CLEAR,
                    scope=ThreatScope.SPATIAL_POLYGON,
                    urgency=ThreatUrgency.INFO,
                    title=f"Локальний відбій: {', '.join(detected_districts)}",
                    description=clean_text,
                    target_districts=detected_districts,
                    corridor_polygon=get_district_polygon(detected_districts[0]),
                    source_channel=source_channel,
                    timestamp_utc=ts,
                    raw_text=clean_text
                )
                return ParseResponse(
                    threat_event=threat,
                    parse_time_ms=(time.perf_counter() - start_time) * 1000.0,
                    matched_rules=matched_rules
                )
            
            # Fallback general clear
            threat = ThreatEvent(
                event_id=event_id,
                threat_type=ThreatType.ALL_CLEAR,
                scope=ThreatScope.CITY_WIDE,
                urgency=ThreatUrgency.INFO,
                title="Відбій загрози",
                description=clean_text,
                target_districts=["ALL"],
                source_channel=source_channel,
                timestamp_utc=ts,
                raw_text=clean_text
            )
            return ParseResponse(
                threat_event=threat,
                parse_time_ms=(time.perf_counter() - start_time) * 1000.0,
                matched_rules=matched_rules
            )

        # 2. CHECK BALLISTIC THREAT
        if RE_BALLISTIC.search(clean_text):
            matched_rules.append("RULE_BALLISTIC")
            threat = ThreatEvent(
                event_id=event_id,
                threat_type=ThreatType.BALLISTIC,
                scope=ThreatScope.CITY_WIDE,
                urgency=ThreatUrgency.CRITICAL,
                title="⚠️ ЗАГРОЗА БАЛІСТИКИ: КИЇВ!",
                description=clean_text,
                target_districts=["ALL"],
                source_channel=source_channel,
                timestamp_utc=ts,
                raw_text=clean_text
            )
            return ParseResponse(
                threat_event=threat,
                parse_time_ms=(time.perf_counter() - start_time) * 1000.0,
                matched_rules=matched_rules
            )

        # 3. CHECK TRANSIT OUTSIDE KYIV & UAV
        is_transit = bool(self.transit_re.search(clean_text))

        # 4. CHECK UAV / SHAHED THREAT
        if RE_UAV.search(clean_text):
            matched_rules.append("RULE_UAV")
            
            detected_districts = self._extract_districts(clean_text)
            detected_suburb = self._extract_suburb(clean_text)

            # If transit outside city and no explicit Kyiv municipal district
            if is_transit and not detected_districts:
                matched_rules.append("RULE_TRANSIT_OUTSIDE")
                threat = ThreatEvent(
                    event_id=event_id,
                    threat_type=ThreatType.UAV_SHAHED,
                    scope=ThreatScope.SPATIAL_POLYGON,
                    urgency=ThreatUrgency.INFO,
                    title="Транзит БПЛА за межами міста",
                    description=clean_text,
                    target_districts=[],
                    source_channel=source_channel,
                    timestamp_utc=ts,
                    raw_text=clean_text
                )
                return ParseResponse(
                    threat_event=threat,
                    parse_time_ms=(time.perf_counter() - start_time) * 1000.0,
                    matched_rules=matched_rules
                )

            # Determine target districts and vector
            corridor_poly: Optional[List[List[float]]] = None
            bearing: Optional[float] = None
            
            if detected_suburb:
                suburb_info = KYIV_SUBURBS[detected_suburb]
                bearing = suburb_info["bearing_deg"]
                
                # If no district explicitly mentioned, use primary suburb corridor district
                if not detected_districts:
                    detected_districts = suburb_info["primary_districts"]
                
                # Build flight corridor from suburb entry point to target district center
                target_center = KYIV_DISTRICTS[detected_districts[0]]["center"]
                corridor_poly = generate_corridor_polygon(
                    suburb_info["entry_point"],
                    target_center,
                    buffer_km=4.0
                )
            elif detected_districts:
                # District mentioned without suburb entry point
                corridor_poly = get_district_polygon(detected_districts[0])
                target_center = KYIV_DISTRICTS[detected_districts[0]]["center"]
                bearing = calculate_bearing_deg(KYIV_CENTER, target_center)

            threat = ThreatEvent(
                event_id=event_id,
                threat_type=ThreatType.UAV_SHAHED,
                scope=ThreatScope.SPATIAL_POLYGON,
                urgency=ThreatUrgency.CRITICAL if detected_districts else ThreatUrgency.WARNING,
                title=f"⚠️ БПЛА: {', '.join(detected_districts) if detected_districts else 'Київщина'}",
                description=clean_text,
                target_districts=detected_districts,
                vector_bearing_deg=bearing,
                corridor_polygon=corridor_poly,
                source_channel=source_channel,
                timestamp_utc=ts,
                raw_text=clean_text
            )
            return ParseResponse(
                threat_event=threat,
                parse_time_ms=(time.perf_counter() - start_time) * 1000.0,
                matched_rules=matched_rules
            )

        # 5. CHECK CRUISE MISSILE
        if RE_CRUISE_MISSILE.search(clean_text):
            matched_rules.append("RULE_CRUISE_MISSILE")
            threat = ThreatEvent(
                event_id=event_id,
                threat_type=ThreatType.CRUISE_MISSILE,
                scope=ThreatScope.CITY_WIDE,
                urgency=ThreatUrgency.CRITICAL,
                title="⚠️ КРИЛАТА РАКЕТА: КИЇВ",
                description=clean_text,
                target_districts=["ALL"],
                source_channel=source_channel,
                timestamp_utc=ts,
                raw_text=clean_text
            )
            return ParseResponse(
                threat_event=threat,
                parse_time_ms=(time.perf_counter() - start_time) * 1000.0,
                matched_rules=matched_rules
            )

        # Default / Unknown
        return ParseResponse(
            threat_event=None,
            parse_time_ms=(time.perf_counter() - start_time) * 1000.0,
            matched_rules=["NO_MATCH"]
        )

    def _extract_districts(self, text: str) -> List[str]:
        """Match text against Kyiv 10 district aliases."""
        results: List[str] = []
        for code, pattern in self.district_patterns.items():
            if pattern.search(text):
                results.append(code)
        return results

    def _extract_suburb(self, text: str) -> Optional[str]:
        """Match text against Kyiv approaching suburbs."""
        for code, pattern in self.suburb_patterns.items():
            if pattern.search(text):
                return code
        return None


# Global parser instance
nlp_parser = FastNLPParser()
