package com.ktas.alert.service

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.media.AudioAttributes
import android.media.AudioManager
import android.media.RingtoneManager
import android.media.ToneGenerator
import android.os.Build
import androidx.core.app.NotificationCompat
import com.ktas.alert.ui.MainActivity

class AlertNotificationManager(private val context: Context) {

    private val notificationManager =
        context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

    companion object {
        const val CHANNEL_BALLISTIC = "BALLISTIC_ALERT_CHANNEL"
        const val CHANNEL_UAV = "UAV_SIREN_CHANNEL"
        const val CHANNEL_ALL_CLEAR = "ALL_CLEAR_CHANNEL"

        const val NOTIF_ID_BALLISTIC = 1001
        const val NOTIF_ID_UAV = 1002
        const val NOTIF_ID_CLEAR = 1003

        private var activeToneGenerator: ToneGenerator? = null
    }

    init {
        createNotificationChannels()
    }

    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val alarmAudioAttributes = AudioAttributes.Builder()
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                .setUsage(AudioAttributes.USAGE_ALARM)
                .build()

            val defaultAlarmUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
            val defaultNotifUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)

            // 1. Ballistic Alert Channel (Sharp, Urgent, DND Bypass)
            val ballisticChannel = NotificationChannel(
                CHANNEL_BALLISTIC,
                "⚠️ Балістична загроза (Київ)",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Термінове надгучне оповіщення про загрозу балістичного удару"
                setSound(defaultAlarmUri, alarmAudioAttributes)
                enableVibration(true)
                vibrationPattern = longArrayOf(0, 500, 200, 500, 200, 1000)
                setBypassDnd(true)
                lockscreenVisibility = NotificationCompat.VISIBILITY_PUBLIC
            }

            // 2. UAV Siren Channel (Undulating Siren, DND Bypass)
            val uavChannel = NotificationChannel(
                CHANNEL_UAV,
                "🚨 Сирена БПЛА / Шахеди",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Гіперлокальна сирена при наближенні безпілотників до вашого району"
                setSound(defaultAlarmUri, alarmAudioAttributes)
                enableVibration(true)
                vibrationPattern = longArrayOf(0, 1000, 500, 1000, 500, 1000)
                setBypassDnd(true)
                lockscreenVisibility = NotificationCompat.VISIBILITY_PUBLIC
            }

            // 3. All Clear Channel (Gentle Chime)
            val clearChannel = NotificationChannel(
                CHANNEL_ALL_CLEAR,
                "✅ Відбій загрози",
                NotificationManager.IMPORTANCE_DEFAULT
            ).apply {
                description = "Тихе інформаційне сповіщення про відбій небезпеки для вашого району"
                setSound(defaultNotifUri, alarmAudioAttributes)
                enableVibration(false)
            }

            notificationManager.createNotificationChannel(ballisticChannel)
            notificationManager.createNotificationChannel(uavChannel)
            notificationManager.createNotificationChannel(clearChannel)
        }
    }

    fun triggerBallisticAlert(title: String, message: String) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val builder = NotificationCompat.Builder(context, CHANNEL_BALLISTIC)
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle(title)
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .setContentIntent(pendingIntent)
            .setFullScreenIntent(pendingIntent, true)
            .setAutoCancel(true)

        notificationManager.notify(NOTIF_ID_BALLISTIC, builder.build())
        playSynthesizedTone(isBallistic = true)
    }

    fun triggerUavSiren(title: String, message: String) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val builder = NotificationCompat.Builder(context, CHANNEL_UAV)
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle(title)
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)

        notificationManager.notify(NOTIF_ID_UAV, builder.build())
        playSynthesizedTone(isBallistic = false)
    }

    fun triggerAllClear(title: String, message: String) {
        val intent = Intent(context, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val builder = NotificationCompat.Builder(context, CHANNEL_ALL_CLEAR)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle(title)
            .setContentText(message)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)

        notificationManager.notify(NOTIF_ID_CLEAR, builder.build())
        stopSound()
    }

    fun playSynthesizedTone(isBallistic: Boolean) {
        stopSound()
        try {
            activeToneGenerator = ToneGenerator(AudioManager.STREAM_ALARM, 100)
            val toneType = if (isBallistic) {
                ToneGenerator.TONE_CDMA_EMERGENCY_RINGBACK
            } else {
                ToneGenerator.TONE_CDMA_ALERT_NETWORK_LITE
            }
            activeToneGenerator?.startTone(toneType, 3000)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    fun stopSound() {
        try {
            activeToneGenerator?.stopTone()
            activeToneGenerator?.release()
            activeToneGenerator = null
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
