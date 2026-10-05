# Implementation Plan: Kyiv Threat Alert System (KTAS)

Розробка виробничого прототипу системи персоналізованого оповіщення про загрози для Києва з підтримкою балістики (загальноміський сигнал), БПЛА (гіперлокальні коридори та райони), Zero-Knowledge On-Device геофільтрації та синтетичного середовища симуляції для захисту проєкту в Agentic AI School.

---

## 1. Prerequisites & Необхідне середовище

Для розробки, запуску та демонстрації системи визначено такі передумови (розподілені на **Обов'язкові для дедлайну сьогодні** та **Опціональні для Production**):

### 1.1. Локальне системне середовище (Поточний стан машини)
| Інструмент | Потрібна версія | Стан на машині | Дія |
| :--- | :---: | :---: | :--- |
| **Python** | 3.10+ | ✅ **3.14.4** (FastAPI, Pydantic v2, Pytest, Shapely вже встановлено) | Готово до використання |
| **Java JDK** | 17+ | ✅ **OpenJDK 17.0.19** (`JAVA_HOME` налаштовано) | Готово для Android/Gradle |
| **Git & GitHub CLI**| 2.x | ✅ **Git 2.54.0**, **gh 2.102.0** | Готово для версіонування та CI/CD |
| **Android Studio** | Сучасна версія | ✅ **Android Studio 2026.2.1** (`D:\Program Files\bin\studio64.exe`) | Встановлено та готово |
| **Android SDK & ADB** | API 34+ | ✅ **API 37.0**, **Build-tools 36.0**, **ADB 37.0.1** (`D:\Android SDK`) | Сконфігуровано (`ANDROID_HOME`, `PATH`) |
| **Android Emulator** | AVD | ✅ **Medium_Phone_API_37.0** | Готово для запуску та тестування |

### 1.2. Облікові записи та API ключі (Credentials Matrix)
| Сервіс | Режим демонстрації (Сьогодні для AI School) | Production режим (Бойовий запуск) |
| :--- | :--- | :--- |
| **Telegram API** | **Не потрібен.** Використовується `MockStreamProvider` з датасетом із 15 реальних історичних повідомлень моніторингових каналів. | Потрібні `api_id`, `api_hash` з [my.telegram.org](https://my.telegram.org) + активний Telegram-номер для підключення `Telethon`. |
| **Firebase Cloud Messaging** | **Не потрібен для тестів.** Бекенд має вбудований `MockFCMDispatcher`, який емулює доставку та передає payload безпосередньо в емулятор або тестовий раннер. | Безкоштовний проект у [Firebase Console](https://console.firebase.google.com): завантажити `serviceAccountKey.json` (бекенд) та `google-services.json` (Android). |
| **GitHub** | Репозиторій для коду проєкту. | GitHub Actions Secrets для автоматичної збірки та релізу APK (`app-release.apk`). |

---

## 2. User Review Required

> [!IMPORTANT]
> **Звукова диференціація загроз:**
> Згідно з вашим вибором, у додатку створюються два окремих аудіоканали:
> 1. `BALLISTIC_ALERT_CHANNEL`: уривчастий, надгучний, високочастотний сигнал тривоги для балістики.
> 2. `UAV_SIREN_CHANNEL`: класична хвилеподібна сирена для БПЛА/Шахедів.
> Обидва сигнали використовують `AudioAttributes.USAGE_ALARM` та пробивають профіль "Не турбувати" (DND).

> [!WARNING]
> **План тестування для дедлайну (Agentic AI School):**
> Для успішного захисту проєкту сьогодні створюється повноцінний автономний CLI-симулятор (`simulator/run_simulation.py`). Він запускає наскрізний тест (End-to-End): зчитує 15 історичних повідомлень, проводить їх через NLP-парсер, формує гео-полігони загрози та демонструє логіку реакції для двох віртуальних користувачів (Користувач на Оболоні vs Користувач на Позняках).

---

## 3. Open Questions

Всі ключові вимоги узгоджено. Якщо під час реалізації будуть необхідні специфічні налаштування мікрорайонів, вони легко розширюються через конфігураційний файл `gazetteer.py`.

---

## 4. Proposed Changes

Структура проєкту:
```
d:\Agentic AI\
├── backend/                  # Хмарний бекенд обробки та розсилки
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py         # Налаштування середовища (PROD / MOCK_MODE)
│   │   ├── models.py         # Pydantic v2 моделі загроз та конфігурацій
│   │   ├── gazetteer.py      # Топонімічна база Києва, райони, координати
│   │   ├── nlp_parser.py     # Високошвидкісний NLP/Regex детектор (< 5 мс)
│   │   ├── spatial_engine.py # Розрахунок геометрії полігонів та коридорів
│   │   ├── ingestion/
│   │   │   ├── base.py       # Інтерфейс джерела потоку
│   │   │   ├── mock_provider.py     # Синтетичний генератор подій
│   │   │   └── telethon_provider.py # Живий клієнт Telegram MTProto
│   │   ├── fcm_dispatcher.py # Розсилка FCM пушів + Mock логер
│   │   └── main.py           # FastAPI сервер та API контролери
│   ├── requirements.txt
│   └── tests/
│       ├── __init__.py
│       ├── test_nlp_parser.py
│       └── test_spatial_engine.py
├── simulator/                # Тестовий контур для Agentic AI School
│   ├── test_dataset.json     # 15 реальних історичних повідомлень моніторингових каналів
│   └── run_simulation.py     # Інтерактивний демонстраційний E2E сценарій
├── android/                  # Повноцінний вихідний код Android застосунку
│   ├── app/
│   │   ├── src/main/
│   │   │   ├── AndroidManifest.xml
│   │   │   ├── java/com/ktas/alert/
│   │   │   │   ├── data/
│   │   │   │   │   ├── ThreatModels.kt
│   │   │   │   │   └── UserPreferencesRepository.kt
│   │   │   │   ├── engine/
│   │   │   │   │   ├── ThreatEvaluator.kt       # Zero-Knowledge оцінювач на девайсі
│   │   │   │   │   └── SpatialUtils.kt          # Локальна перевірка полігонів
│   │   │   │   ├── service/
│   │   │   │   │   ├── KTASFirebaseService.kt   # Обробка WakeLock пушів
│   │   │   │   │   └── AlertNotificationManager.kt # USAGE_ALARM, DND bypass, звуки
│   │   │   │   └── ui/
│   │   │   │       ├── MainActivity.kt
│   │   │   │       ├── theme/Theme.kt
│   │   │   │       ├── screens/
│   │   │   │       │   ├── DashboardScreen.kt   # Радар Києва та статус
│   │   │   │       │   ├── SettingsScreen.kt    # Фільтри районів, toggle балістики
│   │   │   │       │   ├── AudioTestScreen.kt   # Тест сирен (Балістика vs БПЛА)
│   │   │   │       │   └── ThreatFeedScreen.kt  # Журнал зафіксованих подій
│   │   ├── build.gradle.kts
│   │   └── proguard-rules.pro
│   ├── build.gradle.kts
│   └── settings.gradle.kts
└── .github/workflows/
    └── build-apk.yml         # CI/CD пайплайн збірки та публікації release APK
```

---

## 5. Verification Plan

### 5.1. Автоматизовані тести бекенду (Automated Tests)
Запуск через pytest:
```powershell
python -m pytest backend/tests/ -v
```
Очікувані результати:
* 100% тестів пройдено.
* Тести перевіряють точність визначення балістики, вилучення районів, розрахунок гео-полігонів та затримку менше 5 мс.

### 5.2. Запуск демонстраційної симуляції (Simulation Run)
Запуск інтерактивного симулятора:
```powershell
python simulator/run_simulation.py
```
Критерії успіху:
1. Всі 15 повідомлень оброблені з точним визначенням типу загрози.
2. Середній час парсингу: **< 2 мс**.
3. Верифікація поведінки користувачів:
   * Користувач Оболоні отримує сирену для загрози на Оболонь та балістики, але мовчить при атаці на Дарницю.
   * Користувач Позняків отримує сирену для Дарниці/Позняків, але мовчить при балістиці (бо вимкнув її в налаштуваннях) та при загрозі на Оболонь.

### 5.3. Перевірка кодової бази Android
Перевірка синтаксису, класів та відсутності помилок імпортів.
