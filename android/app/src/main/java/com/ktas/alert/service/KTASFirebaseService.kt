package com.ktas.alert.service

import android.os.PowerManager
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.ktas.alert.data.*
import com.ktas.alert.engine.ThreatEvaluator
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

class KTASFirebaseService : FirebaseMessagingService() {

    private val gson = Gson()
    private val scope = CoroutineScope(Dispatchers.IO)

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        super.onMessageReceived(remoteMessage)

        val powerManager = getSystemService(POWER_SERVICE) as PowerManager
        val wakeLock = powerManager.newWakeLock(
            PowerManager.PARTIAL_WAKE_LOCK,
            "ktas:ThreatEvaluationWakeLock"
        )
        wakeLock.acquire(10000) // Hold wakelock for up to 10 seconds

        try {
            val data = remoteMessage.data
            if (data.isEmpty()) return

            val threat = parseThreatEvent(data) ?: return

            scope.launch {
                val prefsRepo = UserPreferencesRepository(applicationContext)
                val ballisticsEnabled = prefsRepo.ballisticsEnabled.first()
                val selectedDistricts = prefsRepo.selectedDistricts.first()
                val radiusKm = prefsRepo.radiusKm.first()
                val respectHeading = prefsRepo.respectHeading.first()

                val result = ThreatEvaluator.evaluate(
                    threat = threat,
                    userDistricts = selectedDistricts,
                    userLocation = null, // Can be supplemented with cached fine location
                    ballisticsEnabled = ballisticsEnabled,
                    dangerRadiusKm = radiusKm,
                    respectVector = respectHeading
                )

                val notifManager = AlertNotificationManager(applicationContext)
                when (result.action) {
                    ActionType.TRIGGER_URGENT_ALARM -> {
                        notifManager.triggerBallisticAlert(threat.title, threat.description)
                    }
                    ActionType.TRIGGER_DISTRICT_ALARM -> {
                        notifManager.triggerUavSiren(threat.title, threat.description)
                    }
                    ActionType.TRIGGER_ALL_CLEAR -> {
                        notifManager.triggerAllClear(threat.title, threat.description)
                    }
                    ActionType.TRIGGER_WARNING -> {
                        // Information notification
                        notifManager.triggerUavSiren("🔔 " + threat.title, threat.description)
                    }
                    ActionType.IGNORE_OUT_OF_ZONE,
                    ActionType.SILENCE_MUTED_BY_USER -> {
                        // Silent discard (Zero-Knowledge filtering)
                    }
                }
            }
        } finally {
            if (wakeLock.isHeld) {
                wakeLock.release()
            }
        }
    }

    private fun parseThreatEvent(data: Map<String, String>): ThreatEvent? {
        return try {
            val eventId = data["event_id"] ?: return null
            val threatType = ThreatType.valueOf(data["threat_type"] ?: "UNKNOWN")
            val scope = ThreatScope.valueOf(data["scope"] ?: "SPATIAL_POLYGON")
            val urgency = ThreatUrgency.valueOf(data["urgency"] ?: "CRITICAL")
            val title = data["title"] ?: "Загроза!"
            val description = data["description"] ?: ""

            val targetDistrictsJson = data["target_districts"]
            val districtsType = object : TypeToken<List<String>>() {}.type
            val targetDistricts: List<String> = if (!targetDistrictsJson.isNullOrEmpty()) {
                gson.fromJson(targetDistrictsJson, districtsType)
            } else emptyList()

            val corridorPolygonJson = data["corridor_polygon"]
            val polygonType = object : TypeToken<List<List<Double>>>() {}.type
            val corridorPolygon: List<List<Double>>? = if (!corridorPolygonJson.isNullOrEmpty()) {
                gson.fromJson(corridorPolygonJson, polygonType)
            } else null

            val bearing = data["vector_bearing_deg"]?.toDoubleOrNull()
            val timestamp = data["timestamp_utc"]?.toLongOrNull() ?: (System.currentTimeMillis() / 1000)

            ThreatEvent(
                eventId = eventId,
                threatType = threatType,
                scope = scope,
                urgency = urgency,
                title = title,
                description = description,
                targetDistricts = targetDistricts,
                vectorBearingDeg = bearing,
                corridorPolygon = corridorPolygon,
                sourceChannel = data["source_channel"] ?: "@monitor_war",
                timestampUtc = timestamp
            )
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
}
