package com.ktas.alert.ui

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Radar
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.core.content.ContextCompat
import com.ktas.alert.data.ThreatEvent
import com.ktas.alert.data.ThreatScope
import com.ktas.alert.data.ThreatType
import com.ktas.alert.data.ThreatUrgency
import com.ktas.alert.data.UserPreferencesRepository
import com.ktas.alert.service.AlertNotificationManager
import com.ktas.alert.ui.screens.AudioTestScreen
import com.ktas.alert.ui.screens.DashboardScreen
import com.ktas.alert.ui.screens.SettingsScreen
import com.ktas.alert.ui.screens.ThreatFeedScreen
import com.ktas.alert.ui.theme.AccentAmber
import com.ktas.alert.ui.theme.BgDark
import com.ktas.alert.ui.theme.KTASTheme
import com.ktas.alert.ui.theme.SurfaceDark
import com.ktas.alert.ui.theme.TextPrimary
import com.ktas.alert.ui.theme.TextSecondary
import kotlinx.coroutines.launch

sealed class Screen(val route: String, val title: String, val icon: ImageVector) {
    object Dashboard : Screen("dashboard", "Радар", Icons.Default.Radar)
    object Settings : Screen("settings", "Фільтри", Icons.Default.Settings)
    object AudioTest : Screen("audio_test", "Тест звуку", Icons.Default.VolumeUp)
    object ThreatFeed : Screen("threat_feed", "Події", Icons.Default.List)
}

class MainActivity : ComponentActivity() {

    private lateinit var prefsRepo: UserPreferencesRepository
    private lateinit var alertManager: AlertNotificationManager

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { _ -> }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        prefsRepo = UserPreferencesRepository(applicationContext)
        alertManager = AlertNotificationManager(applicationContext)

        checkAndRequestPermissions()

        setContent {
            KTASTheme {
                MainApp()
            }
        }
    }

    private fun checkAndRequestPermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(
                    this,
                    Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                requestPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
            }
        }
    }

    @Composable
    fun MainApp() {
        val coroutineScope = rememberCoroutineScope()
        var currentScreen by remember { mutableStateOf<Screen>(Screen.Dashboard) }

        val ballisticsEnabled by prefsRepo.ballisticsEnabled.collectAsState(initial = true)
        val selectedDistricts by prefsRepo.selectedDistricts.collectAsState(initial = setOf("Obolonskyi"))
        val radiusKm by prefsRepo.radiusKm.collectAsState(initial = 5.0f)
        val respectHeading by prefsRepo.respectHeading.collectAsState(initial = true)

        var activeThreat by remember { mutableStateOf<ThreatEvent?>(null) }

        val sampleEvents = remember {
            mutableStateListOf(
                ThreatEvent(
                    eventId = "hist_1",
                    threatType = ThreatType.BALLISTIC,
                    scope = ThreatScope.CITY_WIDE,
                    urgency = ThreatUrgency.CRITICAL,
                    title = "Загроза балістики: Київ!",
                    description = "Швидкісна ціль з півночі в напрямку столиці. Всім негайно в укриття!",
                    targetDistricts = listOf("Весь Київ"),
                    sourceChannel = "@kpszsu",
                    timestampUtc = System.currentTimeMillis() / 1000 - 1800
                ),
                ThreatEvent(
                    eventId = "hist_2",
                    threatType = ThreatType.UAV_SHAHED,
                    scope = ThreatScope.SPATIAL_POLYGON,
                    urgency = ThreatUrgency.WARNING,
                    title = "Шахед з Вишгорода курсом на Оболонь",
                    description = "БПЛА заходить у північний сектор Києва. Робота ППО.",
                    targetDistricts = listOf("Оболонський"),
                    sourceChannel = "@monitor_war",
                    timestampUtc = System.currentTimeMillis() / 1000 - 3600
                ),
                ThreatEvent(
                    eventId = "hist_3",
                    threatType = ThreatType.ALL_CLEAR,
                    scope = ThreatScope.SPATIAL_POLYGON,
                    urgency = ThreatUrgency.INFO,
                    title = "Оболонь — чисто, ціль збито",
                    description = "Локальний відбій небезпеки для вашого району.",
                    targetDistricts = listOf("Оболонський"),
                    sourceChannel = "@vanek_nikolaev",
                    timestampUtc = System.currentTimeMillis() / 1000 - 3200
                )
            )
        }

        fun triggerDemoBallistic() {
            val event = ThreatEvent(
                eventId = "demo_bal_${System.currentTimeMillis()}",
                threatType = ThreatType.BALLISTIC,
                scope = ThreatScope.CITY_WIDE,
                urgency = ThreatUrgency.CRITICAL,
                title = "⚠️ БАЛІСТИКА: КИЇВ!",
                description = "Зафіксовано пуск балістичної ракети. Негайно в безпечне місце!",
                targetDistricts = listOf("Весь Київ"),
                sourceChannel = "@monitor_war",
                timestampUtc = System.currentTimeMillis() / 1000
            )
            activeThreat = event
            sampleEvents.add(0, event)
            if (ballisticsEnabled) {
                alertManager.triggerBallisticAlert(event.title, event.description)
            }
        }

        fun triggerDemoUav() {
            val event = ThreatEvent(
                eventId = "demo_uav_${System.currentTimeMillis()}",
                threatType = ThreatType.UAV_SHAHED,
                scope = ThreatScope.SPATIAL_POLYGON,
                urgency = ThreatUrgency.CRITICAL,
                title = "🚨 БПЛА: ОБОЛОНЬ",
                description = "Шахед наближається до Оболонського району. Дистанція 4 км.",
                targetDistricts = listOf("Оболонський"),
                sourceChannel = "@vanek_nikolaev",
                timestampUtc = System.currentTimeMillis() / 1000
            )
            activeThreat = event
            sampleEvents.add(0, event)
            if (selectedDistricts.contains("Obolonskyi")) {
                alertManager.triggerUavSiren(event.title, event.description)
            }
        }

        fun triggerDemoClear() {
            val event = ThreatEvent(
                eventId = "demo_clear_${System.currentTimeMillis()}",
                threatType = ThreatType.ALL_CLEAR,
                scope = ThreatScope.SPATIAL_POLYGON,
                urgency = ThreatUrgency.INFO,
                title = "✅ ВІДБІЙ: ЧИСТО",
                description = "Загроза минула. Небезпеки для вашого району немає.",
                targetDistricts = listOf("Оболонський"),
                sourceChannel = "@monitor_war",
                timestampUtc = System.currentTimeMillis() / 1000
            )
            activeThreat = null
            sampleEvents.add(0, event)
            alertManager.triggerAllClear(event.title, event.description)
        }

        Scaffold(
            containerColor = BgDark,
            bottomBar = {
                NavigationBar(containerColor = SurfaceDark) {
                    val screens = listOf(
                        Screen.Dashboard,
                        Screen.Settings,
                        Screen.AudioTest,
                        Screen.ThreatFeed
                    )
                    screens.forEach { screen ->
                        NavigationBarItem(
                            icon = { Icon(screen.icon, contentDescription = screen.title) },
                            label = { Text(screen.title) },
                            selected = currentScreen == screen,
                            onClick = { currentScreen = screen },
                            colors = NavigationBarItemDefaults.colors(
                                selectedIconColor = AccentAmber,
                                selectedTextColor = AccentAmber,
                                unselectedIconColor = TextSecondary,
                                unselectedTextColor = TextSecondary,
                                indicatorColor = Color.Transparent
                            )
                        )
                    }
                }
            }
        ) { paddingValues ->
            Box(modifier = Modifier.padding(paddingValues)) {
                when (currentScreen) {
                    Screen.Dashboard -> DashboardScreen(
                        ballisticsEnabled = ballisticsEnabled,
                        selectedDistricts = selectedDistricts,
                        activeThreat = activeThreat,
                        onToggleBallistics = { enabled ->
                            coroutineScope.launch { prefsRepo.setBallisticsEnabled(enabled) }
                        },
                        onTriggerBallistic = { triggerDemoBallistic() },
                        onTriggerUav = { triggerDemoUav() },
                        onTriggerClear = { triggerDemoClear() },
                        onStopSound = { alertManager.stopSound() },
                        onNavigateToAudioTest = { currentScreen = Screen.AudioTest }
                    )
                    Screen.Settings -> SettingsScreen(
                        ballisticsEnabled = ballisticsEnabled,
                        selectedDistricts = selectedDistricts,
                        radiusKm = radiusKm,
                        respectHeading = respectHeading,
                        onUpdateBallistics = { enabled ->
                            coroutineScope.launch { prefsRepo.setBallisticsEnabled(enabled) }
                        },
                        onUpdateDistricts = { districts ->
                            coroutineScope.launch { prefsRepo.setSelectedDistricts(districts) }
                        },
                        onUpdateRadius = { radius ->
                            coroutineScope.launch { prefsRepo.setRadiusKm(radius) }
                        },
                        onUpdateRespectHeading = { respect ->
                            coroutineScope.launch { prefsRepo.setRespectHeading(respect) }
                        }
                    )
                    Screen.AudioTest -> AudioTestScreen(
                        onTestBallistic = { triggerDemoBallistic() },
                        onTestUav = { triggerDemoUav() },
                        onTestClear = { triggerDemoClear() },
                        onStopSound = { alertManager.stopSound() }
                    )
                    Screen.ThreatFeed -> ThreatFeedScreen(events = sampleEvents)
                }
            }
        }
    }
}
