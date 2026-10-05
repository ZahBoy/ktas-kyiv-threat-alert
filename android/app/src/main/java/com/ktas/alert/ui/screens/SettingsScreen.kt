package com.ktas.alert.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Security
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ktas.alert.data.KyivDistrictsData
import com.ktas.alert.ui.theme.*

@Composable
fun SettingsScreen(
    ballisticsEnabled: Boolean,
    selectedDistricts: Set<String>,
    radiusKm: Float,
    respectHeading: Boolean,
    onUpdateBallistics: (Boolean) -> Unit,
    onUpdateDistricts: (Set<String>) -> Unit,
    onUpdateRadius: (Float) -> Unit,
    onUpdateRespectHeading: (Boolean) -> Unit
) {
    val scrollState = rememberScrollState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BgDark)
            .verticalScroll(scrollState)
            .padding(16.dp)
    ) {
        Text(
            text = "Налаштування сповіщень",
            color = TextPrimary,
            fontSize = 22.sp,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = "Персоналізація фільтрів загрози та зон моніторингу",
            color = TextSecondary,
            fontSize = 13.sp
        )

        Spacer(modifier = Modifier.height(20.dp))

        // SECTION 1: BALLISTICS
        Text(
            text = "1. БАЛІСТИЧНІ ЗАГРОЗИ",
            color = AccentRed,
            fontSize = 13.sp,
            fontWeight = FontWeight.Bold
        )
        Spacer(modifier = Modifier.height(8.dp))

        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(14.dp),
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
                        text = "Загальноміський сигнал на весь Київ (без фільтрації районів через високу швидкість цілі)",
                        color = TextSecondary,
                        fontSize = 12.sp
                    )
                }
                Switch(
                    checked = ballisticsEnabled,
                    onCheckedChange = onUpdateBallistics,
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = Color.White,
                        checkedTrackColor = AccentRed
                    )
                )
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // SECTION 2: UAV & SHAHED HYPERLOCAL SETTINGS
        Text(
            text = "2. БПЛА ТА ШАХЕДИ (ГІПЕРЛОКАЛЬНІ СЕКТОРИ)",
            color = AccentAmber,
            fontSize = 13.sp,
            fontWeight = FontWeight.Bold
        )
        Spacer(modifier = Modifier.height(8.dp))

        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(14.dp),
            colors = CardDefaults.cardColors(containerColor = CardDark)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Оберіть ваші райони проживання:",
                    color = TextPrimary,
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 14.sp
                )
                Text(
                    text = "Сирена спрацює, тільки якщо дрони летять у ваш або сусідній обраний сектор",
                    color = TextSecondary,
                    fontSize = 12.sp
                )

                Spacer(modifier = Modifier.height(12.dp))

                KyivDistrictsData.ALL.forEach { district ->
                    val isChecked = selectedDistricts.contains(district.id)
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Checkbox(
                            checked = isChecked,
                            onCheckedChange = { checked ->
                                val newDistricts = selectedDistricts.toMutableSet()
                                if (checked) {
                                    newDistricts.add(district.id)
                                } else {
                                    newDistricts.remove(district.id)
                                }
                                onUpdateDistricts(newDistricts)
                            },
                            colors = CheckboxDefaults.colors(
                                checkedColor = AccentAmber,
                                uncheckedColor = TextSecondary
                            )
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "${district.nameUkr} район",
                            color = if (isChecked) TextPrimary else TextSecondary,
                            fontSize = 14.sp,
                            fontWeight = if (isChecked) FontWeight.SemiBold else FontWeight.Normal
                        )
                    }
                }

                HorizontalDivider(modifier = Modifier.padding(vertical = 12.dp), color = SurfaceDark)

                // Radius Slider
                Text(
                    text = "Радіус небезпеки: ${radiusKm.toInt()} км",
                    color = TextPrimary,
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 14.sp
                )
                Slider(
                    value = radiusKm,
                    onValueChange = onUpdateRadius,
                    valueRange = 3f..15f,
                    steps = 3, // 3, 5, 10, 15 km points
                    colors = SliderDefaults.colors(
                        thumbColor = AccentAmber,
                        activeTrackColor = AccentAmber
                    )
                )

                Spacer(modifier = Modifier.height(8.dp))

                // Direction Vector Switch
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "Фільтр вектора руху",
                            color = TextPrimary,
                            fontWeight = FontWeight.SemiBold,
                            fontSize = 14.sp
                        )
                        Text(
                            text = "Ігнорувати цілі, які віддаляються від вашого району",
                            color = TextSecondary,
                            fontSize = 12.sp
                        )
                    }
                    Switch(
                        checked = respectHeading,
                        onCheckedChange = onUpdateRespectHeading,
                        colors = SwitchDefaults.colors(
                            checkedThumbColor = Color.White,
                            checkedTrackColor = AccentAmber
                        )
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // SECTION 3: PRIVACY NOTICE
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(14.dp),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark)
        ) {
            Row(
                modifier = Modifier.padding(14.dp),
                verticalAlignment = Alignment.Top
            ) {
                Icon(
                    imageVector = Icons.Default.Security,
                    contentDescription = "Privacy",
                    tint = AccentGreen,
                    modifier = Modifier.size(24.dp)
                )
                Spacer(modifier = Modifier.width(12.dp))
                Column {
                    Text(
                        text = "Zero-Knowledge Конфіденційність",
                        color = AccentGreen,
                        fontWeight = FontWeight.Bold,
                        fontSize = 13.sp
                    )
                    Text(
                        text = "Сервер розсилає гео-полігони загрози всім клієнтам однаково. Фільтрація виконується виключно на процесорі вашого телефону. Ваші координати ніколи не надсилаються в мережу.",
                        color = TextSecondary,
                        fontSize = 12.sp
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(30.dp))
    }
}
