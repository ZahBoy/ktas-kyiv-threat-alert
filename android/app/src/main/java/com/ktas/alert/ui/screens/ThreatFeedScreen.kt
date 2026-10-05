package com.ktas.alert.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ktas.alert.data.ThreatEvent
import com.ktas.alert.data.ThreatType
import com.ktas.alert.ui.theme.*
import java.text.SimpleDateFormat
import java.util.*

@Composable
fun ThreatFeedScreen(events: List<ThreatEvent>) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BgDark)
            .padding(16.dp)
    ) {
        Text(
            text = "Журнал подій",
            color = TextPrimary,
            fontSize = 22.sp,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = "Історія отриманих загроз та локальних реакцій пристрою",
            color = TextSecondary,
            fontSize = 13.sp
        )

        Spacer(modifier = Modifier.height(16.dp))

        if (events.isEmpty()) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(bottom = 60.dp),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "Очікування перших подій...",
                        color = TextSecondary,
                        fontSize = 15.sp
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = "Система підключена до потоку спостереження",
                        color = AccentCyan,
                        fontSize = 12.sp
                    )
                }
            }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                items(events) { threat ->
                    ThreatItemCard(threat)
                }
            }
        }
    }
}

@Composable
fun ThreatItemCard(threat: ThreatEvent) {
    val (typeColor, typeLabel) = when (threat.threatType) {
        ThreatType.BALLISTIC -> Pair(AccentRed, "БАЛІСТИКА")
        ThreatType.UAV_SHAHED -> Pair(AccentAmber, "БПЛА")
        ThreatType.CRUISE_MISSILE -> Pair(AccentRed, "РАКЕТА")
        ThreatType.ALL_CLEAR -> Pair(AccentGreen, "ВІДБІЙ")
        ThreatType.UNKNOWN -> Pair(TextSecondary, "ІНШЕ")
    }

    val timeFormatted = remember(threat.timestampUtc) {
        val sdf = SimpleDateFormat("HH:mm:ss", Locale.getDefault())
        sdf.format(Date(threat.timestampUtc * 1000))
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = CardDark)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Surface(
                    shape = RoundedCornerShape(6.dp),
                    color = typeColor.copy(alpha = 0.2f)
                ) {
                    Text(
                        text = typeLabel,
                        color = typeColor,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }

                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = threat.sourceChannel,
                        color = AccentCyan,
                        fontSize = 11.sp
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = timeFormatted,
                        color = TextSecondary,
                        fontSize = 11.sp
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            val descriptionText = if (threat.description.isNotEmpty()) threat.description else threat.title
            Text(
                text = descriptionText,
                color = TextPrimary,
                fontSize = 13.sp
            )

            if (threat.targetDistricts.isNotEmpty()) {
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = "Сектор: ${threat.targetDistricts.joinToString(", ")}",
                    color = TextSecondary,
                    fontSize = 11.sp
                )
            }
        }
    }
}
