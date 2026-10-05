"""Main FastAPI Application Entrypoint for Kyiv Threat Alert System (KTAS)."""
import time
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .models import (
    ParseRequest,
    ParseResponse,
    ThreatEvent,
    UserEvaluationRequest,
    EvaluationResult
)
from .nlp_parser import nlp_parser
from .spatial_engine import evaluate_threat_for_user
from .gazetteer import KYIV_DISTRICTS, KYIV_SUBURBS
from .fcm_dispatcher import fcm_dispatcher

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="High-speed real-time threat parsing, spatial corridor generation, and Zero-Knowledge broadcast server."
)

# CORS middleware for local dashboard and tooling access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory buffer of recent threats (last 50 events)
recent_threats_buffer: List[ThreatEvent] = []


@app.get("/health")
def health_check() -> Dict[str, Any]:
    """Server health status and operational parameters."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.version,
        "mock_mode": settings.mock_mode,
        "active_districts_count": len(KYIV_DISTRICTS),
        "cached_threats_count": len(recent_threats_buffer)
    }


@app.post("/api/v1/parse", response_model=ParseResponse)
def parse_text(request: ParseRequest) -> ParseResponse:
    """Parse raw Ukrainian monitoring channel post in sub-5ms."""
    response = nlp_parser.parse(
        text=request.text,
        source_channel=request.source_channel,
        timestamp_utc=request.timestamp_utc
    )
    return response


@app.post("/api/v1/broadcast")
async def broadcast_message(request: ParseRequest) -> Dict[str, Any]:
    """Parse raw post and immediately broadcast to all Android devices."""
    parse_result = nlp_parser.parse(
        text=request.text,
        source_channel=request.source_channel,
        timestamp_utc=request.timestamp_utc
    )

    if not parse_result.threat_event:
        return {
            "status": "ignored",
            "reason": "Text did not match any threat or all-clear pattern",
            "matched_rules": parse_result.matched_rules,
            "parse_time_ms": parse_result.parse_time_ms
        }

    threat = parse_result.threat_event
    recent_threats_buffer.insert(0, threat)
    if len(recent_threats_buffer) > 50:
        recent_threats_buffer.pop()

    fcm_result = await fcm_dispatcher.broadcast_threat(threat)

    return {
        "status": "dispatched",
        "threat_event": threat,
        "parse_time_ms": parse_result.parse_time_ms,
        "fcm_dispatch": fcm_result
    }


@app.post("/api/v1/evaluate", response_model=EvaluationResult)
def evaluate_device_reaction(request: UserEvaluationRequest) -> EvaluationResult:
    """Simulate client-side Zero-Knowledge evaluation for a virtual device."""
    user_coords = (request.user_location.lat, request.user_location.lon) if request.user_location else None
    
    result = evaluate_threat_for_user(
        threat=request.threat_event,
        user_districts=request.user_districts,
        user_location=user_coords,
        ballistics_enabled=request.ballistics_enabled,
        danger_radius_km=request.danger_radius_km,
        respect_vector=request.respect_vector
    )
    return result


@app.get("/api/v1/districts")
def get_kyiv_districts() -> Dict[str, Any]:
    """List all 10 Kyiv administrative districts, microdistricts, and suburbs."""
    return {
        "districts": [
            {
                "id": code,
                "name_ukr": info["ukr_name"],
                "aliases": info["aliases"],
                "center": {"lat": info["center"][0], "lon": info["center"][1]},
                "polygon": info["polygon"]
            }
            for code, info in KYIV_DISTRICTS.items()
        ],
        "suburbs": [
            {
                "id": code,
                "name_ukr": info["ukr_name"],
                "primary_districts": info["primary_districts"],
                "entry_point": {"lat": info["entry_point"][0], "lon": info["entry_point"][1]},
                "bearing_deg": info["bearing_deg"]
            }
            for code, info in KYIV_SUBURBS.items()
        ]
    }


@app.get("/api/v1/recent_threats", response_model=List[ThreatEvent])
def get_recent_threats() -> List[ThreatEvent]:
    """Retrieve history of recently parsed threats."""
    return recent_threats_buffer
