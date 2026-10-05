# Proguard rules for KTAS
-keep class com.ktas.alert.data.** { *; }
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
