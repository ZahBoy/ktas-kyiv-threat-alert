package com.ktas.alert.data

import android.content.Context
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.floatPreferencesKey
import androidx.datastore.preferences.core.stringSetPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

val Context.dataStore by preferencesDataStore(name = "ktas_user_prefs")

class UserPreferencesRepository(private val context: Context) {

    companion object {
        val KEY_BALLISTICS_ENABLED = booleanPreferencesKey("ballistics_enabled")
        val KEY_SELECTED_DISTRICTS = stringSetPreferencesKey("selected_districts")
        val KEY_RADIUS_KM = floatPreferencesKey("radius_km")
        val KEY_RESPECT_HEADING = booleanPreferencesKey("respect_heading")
    }

    val ballisticsEnabled: Flow<Boolean> = context.dataStore.data.map { preferences ->
        preferences[KEY_BALLISTICS_ENABLED] ?: true
    }

    val selectedDistricts: Flow<Set<String>> = context.dataStore.data.map { preferences ->
        preferences[KEY_SELECTED_DISTRICTS] ?: setOf("Obolonskyi")
    }

    val radiusKm: Flow<Float> = context.dataStore.data.map { preferences ->
        preferences[KEY_RADIUS_KM] ?: 5.0f
    }

    val respectHeading: Flow<Boolean> = context.dataStore.data.map { preferences ->
        preferences[KEY_RESPECT_HEADING] ?: true
    }

    suspend fun setBallisticsEnabled(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[KEY_BALLISTICS_ENABLED] = enabled
        }
    }

    suspend fun setSelectedDistricts(districts: Set<String>) {
        context.dataStore.edit { preferences ->
            preferences[KEY_SELECTED_DISTRICTS] = districts
        }
    }

    suspend fun setRadiusKm(radius: Float) {
        context.dataStore.edit { preferences ->
            preferences[KEY_RADIUS_KM] = radius
        }
    }

    suspend fun setRespectHeading(respect: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[KEY_RESPECT_HEADING] = respect
        }
    }
}
