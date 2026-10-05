package com.ktas.alert.engine

import com.ktas.alert.data.*

object ThreatEvaluator {

    /**
     * Client-side Zero-Knowledge Threat Evaluator.
     * Evaluates incoming threat payload against local user preferences without sharing user location.
     */
    fun evaluate(
        threat: ThreatEvent,
        userDistricts: Set<String>,
        userLocation: Coordinate? = null,
        ballisticsEnabled: Boolean = true,
        dangerRadiusKm: Float = 5.0f,
        respectVector: Boolean = true
    ): EvaluationResult {

        // 1. BALLISTIC ALERT: City-Wide Instant Broadcast
        if (threat.threatType == ThreatType.BALLISTIC) {
            return if (ballisticsEnabled) {
                EvaluationResult(
                    action = ActionType.TRIGGER_URGENT_ALARM,
                    reason = "Миттєва загальноміська загроза балістики по Києву!",
                    soundChannel = "BALLISTIC_ALERT_CHANNEL"
                )
            } else {
                EvaluationResult(
                    action = ActionType.SILENCE_MUTED_BY_USER,
                    reason = "Користувач вимкнув сповіщення про балістику в налаштуваннях",
                    soundChannel = null
                )
            }
        }

        // 2. ALL CLEAR SIGNAL
        if (threat.threatType == ThreatType.ALL_CLEAR) {
            if (threat.targetDistricts.contains("ALL") || threat.targetDistricts.isEmpty()) {
                return EvaluationResult(
                    action = ActionType.TRIGGER_ALL_CLEAR,
                    reason = "Загальний відбій загрози по місту Києву",
                    soundChannel = "ALL_CLEAR_CHANNEL"
                )
            }

            val matchingDistricts = threat.targetDistricts.filter { it in userDistricts }
            if (matchingDistricts.isNotEmpty()) {
                return EvaluationResult(
                    action = ActionType.TRIGGER_ALL_CLEAR,
                    reason = "Локальний відбій для вашого району: ${matchingDistricts.joinToString(", ")}",
                    soundChannel = "ALL_CLEAR_CHANNEL"
                )
            }

            if (userLocation != null && threat.corridorPolygon != null &&
                SpatialUtils.isPointInPolygon(userLocation.lat, userLocation.lon, threat.corridorPolygon)
            ) {
                return EvaluationResult(
                    action = ActionType.TRIGGER_ALL_CLEAR,
                    reason = "Локальний відбій у вашому секторі",
                    soundChannel = "ALL_CLEAR_CHANNEL"
                )
            }

            return EvaluationResult(
                action = ActionType.IGNORE_OUT_OF_ZONE,
                reason = "Локальний відбій для іншого району міста",
                soundChannel = null
            )
        }

        // 3. UAV / SHAHED HYPERLOCAL THREAT
        if (threat.threatType == ThreatType.UAV_SHAHED || threat.threatType == ThreatType.CRUISE_MISSILE) {
            // Check if threat is an outside transit event with no targets
            if (threat.targetDistricts.isEmpty() && threat.corridorPolygon == null) {
                return EvaluationResult(
                    action = ActionType.IGNORE_OUT_OF_ZONE,
                    reason = "Транзит за межами Києва, загрози місту немає",
                    soundChannel = null
                )
            }

            // A. Direct District Match
            val matchingDistricts = threat.targetDistricts.filter { it in userDistricts }
            if (matchingDistricts.isNotEmpty()) {
                return EvaluationResult(
                    action = ActionType.TRIGGER_DISTRICT_ALARM,
                    reason = "БПЛА курсом на ваш район (${matchingDistricts.joinToString(", ")})",
                    soundChannel = "UAV_SIREN_CHANNEL"
                )
            }

            // B. Geodesic & Polygon Check (when GPS is available)
            if (userLocation != null) {
                // Inside corridor polygon
                if (threat.corridorPolygon != null &&
                    SpatialUtils.isPointInPolygon(userLocation.lat, userLocation.lon, threat.corridorPolygon)
                ) {
                    return EvaluationResult(
                        action = ActionType.TRIGGER_DISTRICT_ALARM,
                        reason = "Ваші координати знаходяться всередині коридору загрози",
                        soundChannel = "UAV_SIREN_CHANNEL"
                    )
                }

                // Distance to target district centroids
                var minDistance = Double.MAX_VALUE
                for (targetD in threat.targetDistricts) {
                    val districtObj = KyivDistrictsData.ALL.find { it.id == targetD }
                    if (districtObj != null) {
                        val dist = SpatialUtils.haversineDistanceKm(
                            userLocation.lat, userLocation.lon,
                            districtObj.centerLat, districtObj.centerLon
                        )
                        if (dist < minDistance) minDistance = dist
                    }
                }

                if (minDistance <= dangerRadiusKm) {
                    return EvaluationResult(
                        action = ActionType.TRIGGER_DISTRICT_ALARM,
                        reason = "Ціль у критичному радіусі (%.1f км)".format(minDistance),
                        distanceKm = minDistance,
                        soundChannel = "UAV_SIREN_CHANNEL"
                    )
                } else if (minDistance <= 15.0 && respectVector) {
                    return EvaluationResult(
                        action = ActionType.TRIGGER_WARNING,
                        reason = "Ціль наближається в сусідній сектор (%.1f км)".format(minDistance),
                        distanceKm = minDistance,
                        soundChannel = "WARNING_CHANNEL"
                    )
                }
            }

            return EvaluationResult(
                action = ActionType.IGNORE_OUT_OF_ZONE,
                reason = "Ціль в іншому секторі міста, для вас небезпеки немає",
                soundChannel = null
            )
        }

        return EvaluationResult(
            action = ActionType.IGNORE_OUT_OF_ZONE,
            reason = "Невідомий тип загрози",
            soundChannel = null
        )
    }
}
