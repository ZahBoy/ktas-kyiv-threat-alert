from enum import Enum
from typing import Optional, List
import time
from pydantic import BaseModel, Field


class ThreatType(str, Enum):
    """Classification of the threat."""
    BALLISTIC = "BALLISTIC"
    UAV_SHAHED = "UAV_SHAHED"
    CRUISE_MISSILE = "CRUISE_MISSILE"
    ALL_CLEAR = "ALL_CLEAR"
    UNKNOWN = "UNKNOWN"


class ThreatScope(str, Enum):
    """Scope of notification targeting."""
    CITY_WIDE = "CITY_WIDE"
    SPATIAL_POLYGON = "SPATIAL_POLYGON"


class ThreatUrgency(str, Enum):
    """Urgency level."""
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


class ActionType(str, Enum):
    """Client device reaction action."""
    TRIGGER_URGENT_ALARM = "TRIGGER_URGENT_ALARM"
    TRIGGER_DISTRICT_ALARM = "TRIGGER_DISTRICT_ALARM"
    TRIGGER_WARNING = "TRIGGER_WARNING"
    TRIGGER_ALL_CLEAR = "TRIGGER_ALL_CLEAR"
    IGNORE_OUT_OF_ZONE = "IGNORE_OUT_OF_ZONE"
    SILENCE_MUTED_BY_USER = "SILENCE_MUTED_BY_USER"


class Coordinate(BaseModel):
    """Geographic coordinate in WGS-84."""
    lat: float
    lon: float


class ThreatEvent(BaseModel):
    """Standardized canonical threat event payload."""
    event_id: str
    threat_type: ThreatType
    scope: ThreatScope
    urgency: ThreatUrgency
    title: str
    description: str
    target_districts: List[str] = Field(default_factory=list)
    vector_bearing_deg: Optional[float] = None
    corridor_polygon: Optional[List[List[float]]] = None  # [[lat, lon], ...]
    source_channel: str = "@monitor_war"
    timestamp_utc: int = Field(default_factory=lambda: int(time.time()))
    raw_text: Optional[str] = None


class ParseRequest(BaseModel):
    """Request to parse a raw text message."""
    text: str
    source_channel: str = "@monitor_war"
    timestamp_utc: Optional[int] = None


class ParseResponse(BaseModel):
    """Response containing parsed ThreatEvent and diagnostic metrics."""
    threat_event: Optional[ThreatEvent]
    parse_time_ms: float
    matched_rules: List[str] = Field(default_factory=list)


class UserEvaluationRequest(BaseModel):
    """Request simulating client-side Zero-Knowledge evaluation."""
    threat_event: ThreatEvent
    user_districts: List[str] = Field(default_factory=list)
    user_location: Optional[Coordinate] = None
    ballistics_enabled: bool = True
    danger_radius_km: float = 5.0
    respect_vector: bool = True


class EvaluationResult(BaseModel):
    """Result of client-side threat evaluation."""
    action: ActionType
    reason: str
    distance_km: Optional[float] = None
    sound_channel: Optional[str] = None  # BALLISTIC_ALERT_CHANNEL, UAV_SIREN_CHANNEL, or None
