"""Firebase Cloud Messaging (FCM) Dispatcher.

Handles broadcasting High-Priority Data-Only push notifications
to Android clients with Zero-Knowledge payloads.
"""
import json
import logging
from typing import Dict, Any, List, Optional
from .models import ThreatEvent

logger = logging.getLogger(__name__)


class FCMDispatcher:
    """Dispatches high-priority wake-up push notifications to Android devices."""

    def __init__(self, credentials_path: Optional[str] = None, mock_mode: bool = True):
        self.mock_mode = mock_mode
        self.credentials_path = credentials_path
        self.dispatched_history: List[Dict[str, Any]] = []
        self._firebase_app = None

        if not self.mock_mode and self.credentials_path:
            self._init_firebase()

    def _init_firebase(self):
        try:
            import firebase_admin
            from firebase_admin import credentials
            cred = credentials.Certificate(self.credentials_path)
            self._firebase_app = firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully.")
        except Exception as e:
            logger.warning("Could not initialize Firebase Admin SDK (%s). Falling back to mock dispatcher.", e)
            self.mock_mode = True

    def build_payload(self, threat: ThreatEvent) -> Dict[str, str]:
        """Convert ThreatEvent into string key-value pairs required by FCM data message."""
        return {
            "event_id": str(threat.event_id),
            "threat_type": str(threat.threat_type.value),
            "scope": str(threat.scope.value),
            "urgency": str(threat.urgency.value),
            "title": str(threat.title),
            "description": str(threat.description),
            "target_districts": json.dumps(threat.target_districts, ensure_ascii=False),
            "vector_bearing_deg": str(threat.vector_bearing_deg or 0.0),
            "corridor_polygon": json.dumps(threat.corridor_polygon or []),
            "source_channel": str(threat.source_channel),
            "timestamp_utc": str(threat.timestamp_utc)
        }

    async def broadcast_threat(self, threat: ThreatEvent, topic: str = "kyiv_threats") -> Dict[str, Any]:
        """Broadcast high-priority payload to all devices subscribed to the topic."""
        payload_data = self.build_payload(threat)
        dispatch_record = {
            "topic": topic,
            "threat_event_id": threat.event_id,
            "threat_type": threat.threat_type.value,
            "payload": payload_data,
            "mock": self.mock_mode
        }
        self.dispatched_history.append(dispatch_record)

        if self.mock_mode:
            logger.info(
                "[MOCK FCM BROADCAST] Topic='%s' | Type=%s | Urgency=%s | Title='%s'",
                topic, threat.threat_type.value, threat.urgency.value, threat.title
            )
            return {"status": "success", "mode": "mock", "message_id": f"mock_fcm_{threat.event_id}"}

        # Live FCM dispatch
        try:
            from firebase_admin import messaging
            message = messaging.Message(
                data=payload_data,
                topic=topic,
                android=messaging.AndroidConfig(
                    priority="high",
                    ttl=60  # 60 seconds time-to-live
                )
            )
            msg_id = messaging.send(message)
            logger.info("FCM broadcast sent successfully. ID: %s", msg_id)
            return {"status": "success", "mode": "live", "message_id": msg_id}
        except Exception as e:
            logger.error("Error broadcasting FCM message: %s", e)
            return {"status": "error", "message": str(e)}


# Global dispatcher instance
fcm_dispatcher = FCMDispatcher(mock_mode=True)
