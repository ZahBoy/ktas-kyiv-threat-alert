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
        val sampleEvents = remember { mutableStateListOf<ThreatEvent>() }

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
                        onToggleBallistics = { enabled ->
                            coroutineScope.launch { prefsRepo.setBallisticsEnabled(enabled) }
                        },
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
                        onTestBallistic = {
                            alertManager.triggerBallisticAlert(
                                "⚠️ ТЕСТ: Балістична загроза!",
                                "Перевірка пробивання беззвучного режиму DND для балістики."
                            )
                        },
                        onTestUav = {
                            alertManager.triggerUavSiren(
                                "🚨 ТЕСТ: Сирена БПЛА!",
                                "Перевірка хвилеподібної сирени району."
                            )
                        },
                        onTestClear = {
                            alertManager.triggerAllClear(
                                "✅ ТЕСТ: Відбій загрози",
                                "Перевірка спокійного сигналу відбою."
                            )
                        },
                        onStopSound = {
                            alertManager.stopSound()
                        }
                    )
                    Screen.ThreatFeed -> ThreatFeedScreen(events = sampleEvents)
                }
            }
        }
    }
}
