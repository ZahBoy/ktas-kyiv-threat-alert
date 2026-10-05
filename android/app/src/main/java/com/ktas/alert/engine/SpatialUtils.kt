package com.ktas.alert.engine

import kotlin.math.*

object SpatialUtils {

    /**
     * Determines whether a given point (lat, lon) is located inside a polygon using ray casting.
     * Polygon vertices are expected in [lat, lon] order.
     */
    fun isPointInPolygon(lat: Double, lon: Double, polygon: List<List<Double>>?): Boolean {
        if (polygon == null || polygon.size < 3) return false

        var inside = false
        val n = polygon.size
        var j = n - 1

        for (i in 0 until n) {
            val p1Lat = polygon[i][0]
            val p1Lon = polygon[i][1]
            val p2Lat = polygon[j][0]
            val p2Lon = polygon[j][1]

            if ((p1Lon > lon) != (p2Lon > lon) &&
                lat < (p2Lat - p1Lat) * (lon - p1Lon) / (p2Lon - p1Lon) + p1Lat
            ) {
                inside = !inside
            }
            j = i
        }

        return inside
    }

    /**
     * Calculates the geodesic distance between two points in kilometers via the Haversine formula.
     */
    fun haversineDistanceKm(lat1: Double, lon1: Double, lat2: Double, lon2: Double): Double {
        val r = 6371.0 // Radius of Earth in km
        val dLat = Math.toRadians(lat2 - lat1)
        val dLon = Math.toRadians(lon2 - lon1)

        val a = sin(dLat / 2).pow(2.0) +
                cos(Math.toRadians(lat1)) * cos(Math.toRadians(lat2)) *
                sin(dLon / 2).pow(2.0)

        val c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return r * c
    }

    /**
     * Calculates the initial bearing from point 1 to point 2 in degrees (0..360).
     */
    fun calculateBearing(lat1: Double, lon1: Double, lat2: Double, lon2: Double): Double {
        val phi1 = Math.toRadians(lat1)
        val phi2 = Math.toRadians(lat2)
        val deltaLambda = Math.toRadians(lon2 - lon1)

        val y = sin(deltaLambda) * cos(phi2)
        val x = cos(phi1) * sin(phi2) - sin(phi1) * cos(phi2) * cos(deltaLambda)
        val bearing = Math.toDegrees(atan2(y, x))
        return (bearing + 360.0) % 360.0
    }
}
