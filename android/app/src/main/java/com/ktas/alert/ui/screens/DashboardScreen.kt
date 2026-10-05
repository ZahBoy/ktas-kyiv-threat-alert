package com.ktas.alert.ui.screens

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Dangerous
import androidx.compose.material.icons.filled.NotificationsActive
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material.icons.filled.StopCircle
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ktas.alert.data.ThreatEvent
import com.ktas.alert.data.ThreatType
import com.ktas.alert.ui.theme.*

@Composable
fun DashboardScreen(
    ballisticsEnabled: Boolean,
    selectedDistricts: Set<String>,
    activeThreat: ThreatEvent?,
    onToggleBallistics: (Boolean) -> Unit,
    onTriggerBallistic: () -> Unit,
    onTriggerUav: () -> Unit,
    onTriggerClear: () -> Unit,
    onStopSound: () -> Unit,
    onNavigateToAudioTest: () -> Unit
) {
    val scrollState = rememberScrollState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BgDark)
            .verticalScroll(scrollState)
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // App Header
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 4.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Column {
                Text(
                    text = "KTAS • КИЇВ",
                    color = TextPrimary,
                    fontSize = 22.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "Zero-Knowledge Threat Shield",
                    color = TextSecondary,
                    fontSize = 12.sp
                )
            }
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = if (activeThreat != null) AccentRed.copy(alpha = 0.2f) else AccentGreen.copy(alpha = 0.15f),
                border = BorderStroke(1.dp, if (activeThreat != null) AccentRed else AccentGreen)
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 5.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .clip(CircleShape)
                            .background(if (activeThreat != null) AccentRed else AccentGreen)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = if (activeThreat != null) "ALERT ACTIVE" else "ONLINE",
                        color = if (activeThreat != null) AccentRed else AccentGreen,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Radar Visualizer with dynamic threat blips
        RadarWidget(
            modifier = Modifier.size(230.dp),
            activeThreat = activeThreat
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Threat Status Card
        val isBallistic = activeThreat?.threatType == ThreatType.BALLISTIC
        val isUav = activeThreat?.threatType == ThreatType.UAV_SHAHED

        val statusColor = when {
            isBallistic -> AccentRed
            isUav -> AccentAmber
            else -> AccentGreen
        }

        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = CardDark),
            border = if (activeThreat != null) BorderStroke(1.5.dp, statusColor) else null
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = if (activeThreat != null) Icons.Default.Warning else Icons.Default.Shield,
                        contentDescription = "Status",
                        tint = statusColor,
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = when {
                            isBallistic -> "УВАГА: БАЛІСТИЧНИЙ УДАР (КИЇВ)"
                            isUav -> "ЗАГРОЗА БПЛА: СЕКТОР ОБОЛОНЬ"
                            else -> "СТАТУС: ЧИСТО • ЗАГРОЗ НЕ ВИЯВЛЕНО"
                        },
                        color = statusColor,
                        fontWeight = FontWeight.Bold,
                        fontSize = 15.sp
                    )
                }
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = activeThreat?.description
                        ?: "Активний гео-моніторинг секторів: ${if (selectedDistricts.isNotEmpty()) selectedDistricts.joinToString(", ") else "Всі"}",
                    color = if (activeThreat != null) TextPrimary else TextSecondary,
                    fontSize = 13.sp
                )

                if (activeThreat != null) {
                    Spacer(modifier = Modifier.height(10.dp))
                    Button(
                        onClick = onStopSound,
                        shape = RoundedCornerShape(8.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = SurfaceDark),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Icon(Icons.Default.StopCircle, contentDescription = "Stop", tint = Color.White)
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("Зупинити сигнал сирени", color = Color.White, fontSize = 13.sp)
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Interactive Live Simulation Panel (Demo Controls)
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = CardDark)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "ДЕМОНСТРАЦІЙНИЙ КОНТРОЛЬ ЗАГРОЗ",
                    color = AccentCyan,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "Миттєве тестування наскрізної реакції системи (сирени, DND, радар):",
                    color = TextSecondary,
                    fontSize = 12.sp
                )
                Spacer(modifier = Modifier.height(12.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Button(
                        onClick = onTriggerBallistic,
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(10.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = AccentRed)
                    ) {
                        Text("Балістика", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }

                    Button(
                        onClick = onTriggerUav,
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(10.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = AccentAmber)
                    ) {
                        Text("БПЛА Оболонь", fontSize = 12.sp, color = Color.Black, fontWeight = FontWeight.Bold)
                    }

                    Button(
                        onClick = onTriggerClear,
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(10.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = AccentGreen)
                    ) {
                        Text("Відбій", fontSize = 12.sp, color = Color.Black, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Ballistics Quick Toggle Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = CardDark)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Оповіщення про балістику",
                        color = TextPrimary,
                        fontWeight = FontWeight.SemiBold,
                        fontSize = 15.sp
                    )
                    Text(
                        text = "Загальноміський сигнал на весь Київ (без фільтрації через швидкість цілі)",
                        color = TextSecondary,
                        fontSize = 12.sp
                    )
                }
                Switch(
                    checked = ballisticsEnabled,
                    onCheckedChange = onToggleBallistics,
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = Color.White,
                        checkedTrackColor = AccentRed,
                        uncheckedThumbColor = Color.Gray,
                        uncheckedTrackColor = SurfaceDark
                    )
                )
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Quick Audio Test Action Button
        OutlinedButton(
            onClick = onNavigateToAudioTest,
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            border = BorderStroke(1.dp, AccentAmber)
        ) {
            Icon(Icons.Default.VolumeUp, contentDescription = "Test Sound", tint = AccentAmber)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Повний звуковий тест каналів (DND Bypass)", color = TextPrimary)
        }

        Spacer(modifier = Modifier.height(24.dp))
    }
}

@Composable
fun RadarWidget(
    modifier: Modifier = Modifier,
    activeThreat: ThreatEvent? = null
) {
    val infiniteTransition = rememberInfiniteTransition(label = "RadarSweep")
    val angle by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(2800, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "Angle"
    )

    val pulseRadius by infiniteTransition.animateFloat(
        initialValue = 4f,
        targetValue = 24f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "Pulse"
    )

    val isBallistic = activeThreat?.threatType == ThreatType.BALLISTIC
    val isUav = activeThreat?.threatType == ThreatType.UAV_SHAHED

    val themeRadarColor = when {
        isBallistic -> AccentRed
        isUav -> AccentAmber
        else -> AccentCyan
    }

    Box(modifier = modifier, contentAlignment = Alignment.Center) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val center = Offset(size.width / 2, size.height / 2)
            val radius = size.minDimension / 2

            // Radar concentric rings
            drawCircle(color = themeRadarColor.copy(alpha = 0.15f), radius = radius, center = center, style = Stroke(width = 1.5f))
            drawCircle(color = themeRadarColor.copy(alpha = 0.15f), radius = radius * 0.7f, center = center, style = Stroke(width = 1.5f))
            drawCircle(color = themeRadarColor.copy(alpha = 0.15f), radius = radius * 0.4f, center = center, style = Stroke(width = 1.5f))

            // Crosshairs
            drawLine(color = themeRadarColor.copy(alpha = 0.2f), start = Offset(center.x, 0f), end = Offset(center.x, size.height), strokeWidth = 1f)
            drawLine(color = themeRadarColor.copy(alpha = 0.2f), start = Offset(0f, center.y), end = Offset(size.width, center.y), strokeWidth = 1f)

            // Dynamic Target Blips
            if (isBallistic) {
                // Pulsing central ballistic impact danger circle
                drawCircle(color = AccentRed.copy(alpha = 0.35f), radius = pulseRadius * 2, center = center)
                drawCircle(color = AccentRed, radius = 7f, center = center)
            } else if (isUav) {
                // UAV incoming from North (Obolon direction)
                val uavTarget = Offset(center.x + 10f, center.y - radius * 0.55f)
                drawCircle(color = AccentAmber.copy(alpha = 0.4f), radius = pulseRadius, center = uavTarget)
                drawCircle(color = AccentAmber, radius = 6f, center = uavTarget)
                // Vector trail towards center
                drawLine(
                    color = AccentAmber.copy(alpha = 0.8f),
                    start = uavTarget,
                    end = Offset(center.x, center.y - radius * 0.2f),
                    strokeWidth = 2.5f
                )
            }

            // Radar sweep arc
            drawArc(
                brush = Brush.sweepGradient(
                    colors = listOf(Color.Transparent, themeRadarColor.copy(alpha = 0.4f)),
                    center = center
                ),
                startAngle = angle - 50f,
                sweepAngle = 50f,
                useCenter = true
            )
        }

        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                text = when {
                    isBallistic -> "⚠️ BALLISTIC ALERT"
                    isUav -> "🚨 UAV TARGET"
                    else -> "KYIV RADAR"
                },
                color = themeRadarColor,
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = "50.45° N  30.52° E",
                color = themeRadarColor.copy(alpha = 0.6f),
                fontSize = 9.sp
            )
        }
    }
}
