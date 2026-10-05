package com.ktas.alert.ui.screens

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.NotificationsActive
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material.icons.filled.VolumeUp
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
import com.ktas.alert.ui.theme.*

@Composable
fun DashboardScreen(
    ballisticsEnabled: Boolean,
    selectedDistricts: Set<String>,
    onToggleBallistics: (Boolean) -> Unit,
    onNavigateToAudioTest: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BgDark)
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // App Header
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp),
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
                color = AccentGreen.copy(alpha = 0.15f),
                border = androidx.compose.foundation.BorderStroke(1.dp, AccentGreen)
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .clip(CircleShape)
                            .background(AccentGreen)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "ONLINE",
                        color = AccentGreen,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Radar Visualizer
        RadarWidget(modifier = Modifier.size(220.dp))

        Spacer(modifier = Modifier.height(20.dp))

        // Status Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = CardDark)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Shield,
                        contentDescription = "Shield",
                        tint = AccentGreen,
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "СТАТУС: ЧИСТО",
                        color = AccentGreen,
                        fontWeight = FontWeight.Bold,
                        fontSize = 16.sp
                    )
                }
                Spacer(modifier = Modifier.height(8.dp))
                val districtsText = if (selectedDistricts.isNotEmpty()) {
                    selectedDistricts.joinToString(", ")
                } else "Не обрано (сповіщення вимкнено)"
                Text(
                    text = "Моніторинг секторів: $districtsText",
                    color = TextSecondary,
                    fontSize = 13.sp
                )
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

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
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = "Балістика (Загальноміське)",
                            color = TextPrimary,
                            fontWeight = FontWeight.SemiBold,
                            fontSize = 15.sp
                        )
                    }
                    Text(
                        text = "Миттєве сповіщення про загрозу ракет на весь Київ без геофільтрації",
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

        Spacer(modifier = Modifier.height(16.dp))

        // Quick Audio Test Action Button
        Button(
            onClick = onNavigateToAudioTest,
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            colors = ButtonDefaults.buttonColors(containerColor = SurfaceDark)
        ) {
            Icon(Icons.Default.VolumeUp, contentDescription = "Test Sound", tint = AccentAmber)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Перевірити пробивання звуку DND", color = TextPrimary)
        }
    }
}

@Composable
fun RadarWidget(modifier: Modifier = Modifier) {
    val infiniteTransition = rememberInfiniteTransition(label = "RadarSweep")
    val angle by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(3000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "Angle"
    )

    Box(modifier = modifier, contentAlignment = Alignment.Center) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val center = Offset(size.width / 2, size.height / 2)
            val radius = size.minDimension / 2

            // Radar concentric rings
            drawCircle(color = AccentCyan.copy(alpha = 0.15f), radius = radius, center = center, style = Stroke(width = 1.5f))
            drawCircle(color = AccentCyan.copy(alpha = 0.15f), radius = radius * 0.7f, center = center, style = Stroke(width = 1.5f))
            drawCircle(color = AccentCyan.copy(alpha = 0.15f), radius = radius * 0.4f, center = center, style = Stroke(width = 1.5f))

            // Crosshairs
            drawLine(color = AccentCyan.copy(alpha = 0.2f), start = Offset(center.x, 0f), end = Offset(center.x, size.height), strokeWidth = 1f)
            drawLine(color = AccentCyan.copy(alpha = 0.2f), start = Offset(0f, center.y), end = Offset(size.width, center.y), strokeWidth = 1f)

            // Radar sweep arc
            drawArc(
                brush = Brush.sweepGradient(
                    colors = listOf(Color.Transparent, AccentCyan.copy(alpha = 0.35f)),
                    center = center
                ),
                startAngle = angle - 45f,
                sweepAngle = 45f,
                useCenter = true
            )
        }
        Text(
            text = "KYIV RADAR",
            color = AccentCyan.copy(alpha = 0.7f),
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold
        )
    }
}
