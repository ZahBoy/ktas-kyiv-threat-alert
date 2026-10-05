package com.ktas.alert.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val BgDark = Color(0xFF0F1117)
val SurfaceDark = Color(0xFF1A1E29)
val CardDark = Color(0xFF222837)
val AccentRed = Color(0xFFFF3B30)
val AccentAmber = Color(0xFFFF9500)
val AccentGreen = Color(0xFF34C759)
val AccentCyan = Color(0xFF32ADE6)
val TextPrimary = Color(0xFFF2F4F8)
val TextSecondary = Color(0xFF8E95A5)

private val DarkColorScheme = darkColorScheme(
    primary = AccentRed,
    secondary = AccentAmber,
    tertiary = AccentGreen,
    background = BgDark,
    surface = SurfaceDark,
    onPrimary = Color.White,
    onSecondary = Color.Black,
    onTertiary = Color.Black,
    onBackground = TextPrimary,
    onSurface = TextPrimary
)

@Composable
fun KTASTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = DarkColorScheme,
        content = content
    )
}
