package com.ktas.alert.data

enum class ThreatType {
    BALLISTIC,
    UAV_SHAHED,
    CRUISE_MISSILE,
    ALL_CLEAR,
    UNKNOWN
}

enum class ThreatScope {
    CITY_WIDE,
    SPATIAL_POLYGON
}

enum class ThreatUrgency {
    CRITICAL,
    WARNING,
    INFO
}

enum class ActionType {
    TRIGGER_URGENT_ALARM,
    TRIGGER_DISTRICT_ALARM,
    TRIGGER_WARNING,
    TRIGGER_ALL_CLEAR,
    IGNORE_OUT_OF_ZONE,
    SILENCE_MUTED_BY_USER
}

data class Coordinate(
    val lat: Double,
    val lon: Double
)

data class ThreatEvent(
    val eventId: String,
    val threatType: ThreatType,
    val scope: ThreatScope,
    val urgency: ThreatUrgency,
    val title: String,
    val description: String,
    val targetDistricts: List<String> = emptyList(),
    val vectorBearingDeg: Double? = null,
    val corridorPolygon: List<List<Double>>? = null,
    val sourceChannel: String = "@monitor_war",
    val timestampUtc: Long = System.currentTimeMillis() / 1000
)

data class EvaluationResult(
    val action: ActionType,
    val reason: String,
    val distanceKm: Double? = null,
    val soundChannel: String? = null
)

data class District(
    val id: String,
    val nameUkr: String,
    val centerLat: Double,
    val centerLon: Double
)

object KyivDistrictsData {
    val ALL = listOf(
        District("Obolonskyi", "Оболонський", 50.505, 30.498),
        District("Podilskyi", "Подільський", 50.472, 30.468),
        District("Shevchenkivskyi", "Шевченківський", 50.458, 30.465),
        District("Pecherskyi", "Печерський", 50.428, 30.548),
        District("Holosiivskyi", "Голосіївський", 50.380, 30.515),
        District("Solomianskyi", "Солом'янський", 50.425, 30.445),
        District("Sviatoshynskyi", "Святошинський", 50.455, 30.365),
        District("Desnianskyi", "Деснянський", 50.515, 30.605),
        District("Dniprovskyi", "Дніпровський", 50.455, 30.600),
        District("Darnytskyi", "Дарницький", 50.398, 30.635)
    )
}
