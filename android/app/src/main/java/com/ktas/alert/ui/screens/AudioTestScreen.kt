package com.ktas.alert.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.NotificationsActive
import androidx.compose.material.icons.filled.StopCircle
import androidx.compose.material.icons.filled.VolumeMute
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ktas.alert.ui.theme.*

@Composable
fun AudioTestScreen(
    onTestBallistic: () -> Unit,
    onTestUav: () -> Unit,
    onTestClear: () -> Unit,
    onStopSound: () -> Unit
) {
    var playingType by remember { mutableStateOf<String?>(null) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BgDark)
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Тестування сигналів тривоги",
            color = TextPrimary,
            fontSize = 22.sp,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = "Перевірка звуку через апаратний потік USAGE_ALARM та пробивання DND",
            color = TextSecondary,
            fontSize = 13.sp
        )

        Spacer(modifier = Modifier.height(24.dp))

        // Ballistic Test Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = CardDark)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "1. Сигнал балістичної загрози",
                    color = AccentRed,
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp
                )
                Text(
                    text = "Уривчастий високочастотний звук максимальної гучності для миттєвого пробудження (90 секунд до підльоту).",
                    color = TextSecondary,
                    fontSize = 12.sp
                )
                Spacer(modifier = Modifier.height(12.dp))
                Button(
                    onClick = {
                        playingType = "Балістика"
                        onTestBallistic()
                    },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(10.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = AccentRed)
                ) {
                    Icon(Icons.Default.NotificationsActive, contentDescription = "Play", tint = Color.White)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Увімкнути сигнал балістики", color = Color.White, fontWeight = FontWeight.Bold)
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // UAV Test Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = CardDark)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "2. Сирена БПЛА / Шахедів",
                    color = AccentAmber,
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp
                )
                Text(
                    text = "Хвилеподібна сирена для гіперлокальної небезпеки при вході дронів у ваш сектор.",
                    color = TextSecondary,
                    fontSize = 12.sp
                )
                Spacer(modifier = Modifier.height(12.dp))
                Button(
                    onClick = {
                        playingType = "БПЛА"
                        onTestUav()
                    },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(10.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = AccentAmber)
                ) {
                    Icon(Icons.Default.VolumeUp, contentDescription = "Play", tint = Color.Black)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Увімкнути сирену БПЛА", color = Color.Black, fontWeight = FontWeight.Bold)
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // All Clear Test Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = CardDark)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "3. Звук відбою (Чисто)",
                    color = AccentGreen,
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp
                )
                Text(
                    text = "М'який спокійний сигнал про відбій небезпеки для вашого району.",
                    color = TextSecondary,
                    fontSize = 12.sp
                )
                Spacer(modifier = Modifier.height(12.dp))
                Button(
                    onClick = {
                        playingType = "Відбій"
                        onTestClear()
                    },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(10.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = AccentGreen)
                ) {
                    Icon(Icons.Default.VolumeMute, contentDescription = "Play", tint = Color.Black)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Увімкнути сигнал відбою", color = Color.Black, fontWeight = FontWeight.Bold)
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Stop Button
        OutlinedButton(
            onClick = {
                playingType = null
                onStopSound()
            },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            border = androidx.compose.foundation.BorderStroke(1.dp, Color.Gray)
        ) {
            Icon(Icons.Default.StopCircle, contentDescription = "Stop", tint = Color.White)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Зупинити звук", color = Color.White)
        }
    }
}
