# Walkthrough: Kyiv Threat Alert System (KTAS)

**Проєкт:** Kyiv Threat Alert System (KTAS)  
**Ціль:** Продуктовий та архітектурний прототип системи персоналізованого геоконтекстного оповіщення про загрози для Києва з підтримкою балістики (загальноміський сигнал), БПЛА (гіперлокальні коридори та райони) та Zero-Knowledge On-Device геофільтрації.  
**Контекст:** Фінальна подача / захист для **KSE Agentic AI School 2026** (Дедлайн: 5 жовтня 2026).

---

## 1. Що було реалізовано

### 1.1. Архітектурний дизайн та специфікація
* [kyiv_threat_alert_system_spec.md](file:///d:/Agentic%20AI/docs/specs/kyiv_threat_alert_system_spec.md): повний технічний дизайн, порівняння 4 альтернативних архітектур (Android App vs Telegram Bot vs Hybrid TMA vs Client-side TDLib), аналіз компромісів та ризиків безпеки воєнного часу.
* [implementation_plan.md](file:///d:/Agentic%20AI/docs/plans/implementation_plan.md): покроковий інженерний план розробки з матрицею системних передумов (Prerequisites).

### 1.2. Хмарний бекенд обробки та аналізу (`backend/`)
* **Високошвидкісний NLP/Regex парсер (`backend/app/nlp_parser.py`):**
  * Детекція балістики (`іскандер`, `кинджал`, `швидкісна ціль`) з перевіркою відсутності слів відбою.
  * Топонімічний газетир 10 адміністративних районів Києва, 40+ мікрорайонів (Троєщина, Позняки, Осокорки, Нивки тощо) та буферних передмість (Вишгород, Бровари, Бориспіль, Васильків).
  * Векторний парсер напрямків руху дронів (`курс на`, `через`, `повз`).
  * Детекція локального та загального відбою (`чисто`, `ціль збито`).
* **Гео-просторовий рушій (`backend/app/spatial_engine.py`):**
  * Розрахунок геометрії коридорів ураження, векторів підльоту та експорт у GeoJSON.
  * Формула Haversine для точного вимірювання дистанцій.
* **Потокова обробка (`backend/app/ingestion/`):**
  * `base.py`: абстрактний інтерфейс постачальника повідомлень.
  * `mock_provider.py`: генератор синтетичних потоків із керованими таймінгами для демонстрацій.
  * `telethon_provider.py`: бойовий клієнт Telegram MTProto для прослуховування реальних каналів.
* **Транспортний рівень (`backend/app/fcm_dispatcher.py`):**
  * Розсилка `data`-пушів високого пріоритету через Google Firebase Cloud Messaging з авто-fallback у Mock-режим.
* **FastAPI сервер (`backend/app/main.py`):**
  * REST API ендпоінти: `/api/health`, `/api/threats/parse`, `/api/threats/evaluate`, `/api/districts`, `/api/simulate/run`.

### 1.3. Синтетичне тестове середовище для AI School (`simulator/`)
* **Історичний датасет (`simulator/test_dataset.json`):** 15 автентичних повідомлень моніторингових каналів (*«monitor»*, *«Николаевский Ванёк»*, *«Повітряні Сили ЗСУ»*), що охоплюють:
  * Балістику на Київ (з Брянщини, пуски Кинджалів, Іскандерів).
  * БПЛА на Оболонь та Поділ через Вишгород.
  * БПЛА на Лівий берег (Дарниця, Позняки, Осокорки) через Бровари та Бориспіль.
  * Транзитні дрони повз Фастів і Білу Церкву.
  * Локальний відбій над Оболонню («Оболонь — чисто, ціль збито»).
  * Загальний відбій по місту.
* **Автономний демонстраційний стенд (`simulator/run_simulation.py`):**
  * Емулює обробку в реальному часі.
  * Проводить бенчмарк затримки.
  * Моделює реакцію двох віртуальних користувачів:
    * **Користувач А (Оболонь):** увімкнена балістика, GPS Оболоні.
    * **Користувач Б (Позняки):** вимкнена балістика, GPS Позняків.

### 1.4. Native Android застосунок (`android/`)
* **Архітектура:** Kotlin + Jetpack Compose + Material Design 3.
* **Zero-Knowledge On-Device геофільтрація (`ThreatEvaluator.kt`, `SpatialUtils.kt`):**
  * Телефон локально виконує перевірку `isPointInPolygon` та розрахунок дистанції. Точні GPS-координати користувачів **ніколи не передаються на сервер**.
* **Аудіосистема та обхід "Не турбувати" (`AlertNotificationManager.kt`):**
  * Два незалежні аудіоканали:
    1. `BALLISTIC_ALERT_CHANNEL`: уривчастий високочастотний сигнал для балістики.
    2. `UAV_SIREN_CHANNEL`: класична сирена для БПЛА.
  * Обидва канали використовують `AudioAttributes.USAGE_ALARM`, активують `setBypassDnd(true)` та викликають `FullScreenIntent` поверх заблокованого екрана.
* **Інтерфейс користувача (Jetpack Compose Screens):**
  * `DashboardScreen.kt`: статус міста, статус району, інтерактивний радар.
  * `SettingsScreen.kt`: перемикач балістики, вибір районів, повзунок радіуса (3/5/10/15 км).
  * `AudioTestScreen.kt`: тестування гучності обох сирен.
  * `ThreatFeedScreen.kt`: хронологічний журнал подій.
* **Зібраний релізний артефакт:**
  * Файл: `android/app/build/outputs/apk/debug/app-debug.apk` (розмір: **16.4 МБ**).

### 1.5. CI/CD пайплайн (`.github/workflows/build-apk.yml`)
* Автоматизований GitHub Actions workflow, який у хмарі:
  1. Запускає Python pytest тести.
  2. Запускає E2E симулятор.
  3. Збирає Android APK через Gradle.
  4. При створенні тегу версії публікує реліз на GitHub Releases.

---

## 2. Результати верифікації та бенчмарків

### 2.1. Результати автоматизованих тестів (`pytest`)
Запуск:
```powershell
python -m pytest backend/tests/ -v
```
**Результат: 17 із 17 тестів успішно пройдено (100% PASS):**
```
backend/tests/test_api.py::test_health_endpoint PASSED                   [  5%]
backend/tests/test_api.py::test_parse_api_endpoint PASSED                [ 11%]
backend/tests/test_api.py::test_evaluate_api_endpoint PASSED             [ 17%]
backend/tests/test_api.py::test_districts_api_endpoint PASSED            [ 23%]
backend/tests/test_nlp_parser.py::test_ballistic_threat_detection PASSED [ 29%]
backend/tests/test_nlp_parser.py::test_uav_district_and_suburb_extraction PASSED [ 35%]
backend/tests/test_nlp_parser.py::test_all_clear_detection PASSED        [ 41%]
backend/tests/test_nlp_parser.py::test_transit_outside_city PASSED       [ 47%]
backend/tests/test_nlp_parser.py::test_edge_cases PASSED                 [ 52%]
backend/tests/test_nlp_parser.py::test_latency_performance_benchmark PASSED [ 58%]
backend/tests/test_spatial_engine.py::test_haversine_distance PASSED     [ 64%]
backend/tests/test_spatial_engine.py::test_calculate_bearing PASSED      [ 70%]
backend/tests/test_spatial_engine.py::test_point_in_polygon PASSED       [ 76%]
backend/tests/test_spatial_engine.py::test_corridor_polygon_generation PASSED [ 82%]
backend/tests/test_spatial_engine.py::test_user_evaluation_ballistics PASSED [ 88%]
backend/tests/test_spatial_engine.py::test_user_evaluation_uav_district_isolation PASSED [ 94%]
backend/tests/test_spatial_engine.py::test_user_evaluation_all_clear PASSED [100%]
```

### 2.2. Результати демонстраційної симуляції (`run_simulation.py`)
Запуск:
```powershell
python simulator/run_simulation.py
```
**Ключові метрики швидкодії:**
* **Середній час парсингу тексту NLP:** **`0.163 мс`** (Вимога проєкту: `< 5.0 мс` — **перевершено у 30 разів!**).
* **Максимальний сплеск часу:** `0.843 мс`.
* **Мінімальний час:** `0.019 мс`.

**Верифікація бізнес-правил:**
1. ✅ **Балістика (100% точність):** Усі 4 випадки виявлено безпомилково. Користувач А (Оболонь, балістика увімкнена) отримав `[URGENT ALARM]`; Користувач Б (Позняки, вимкнув у налаштуваннях) отримав `[MUTED (USER)]`.
2. ✅ **Ізоляція Оболоні:** При загрозі через Вишгород на Оболонь — Користувач А отримав `[DISTRICT SIREN]`, а телефон Користувача Б мовчав (`[SILENT (OUT)]`).
3. ✅ **Ізоляція Лівого берега:** При загрозі через Бровари на Дарницю/Позняки — Користувач Б отримав `[DISTRICT SIREN]`, а телефон Користувача А мовчав (`[SILENT (OUT)]`).
4. ✅ **Транзит повз Київ:** При прольоті БПЛА біля Фастова/Білої Церкви обидва користувачі залишилися у повній тиші.
5. ✅ **Гіперлокальний відбій:** Повідомлення «Оболонь — чисто» сповістило тільки Користувача А про відбій небезпеки над його будинком.

---

## 3. Інструкція із запуску для комісії / оцінювання

### Крок 1: Запуск автоматичних тестів
```powershell
python -m pytest backend/tests/ -v
```

### Крок 2: Запуск інтерактивного симулятора
```powershell
python simulator/run_simulation.py
```

### Крок 3: Запуск REST API сервера
```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```
Документація Swagger UI буде доступна за адресою: `http://127.0.0.1:8000/docs`.

### Крок 4: Встановлення Android APK на емулятор або телефон
```powershell
& "D:\Android SDK\platform-tools\adb.exe" install -r "D:\Agentic AI\android\app\build\outputs\apk\debug\app-debug.apk"
```
Або відкрийте папку `android/` у вашому **Android Studio** (`D:\Program Files\bin\studio64.exe`) для запуску на емуляторі `Medium_Phone_API_37.0`.

---

## 4. Підсумок для подання на KSE Agentic AI School
Проєкт демонструє завершений інженерний цикл розробника систем штучного інтелекту:
1. **Product Discovery & Trade-off Analysis:** Чітке технічне обґрунтування, чому Telegram-бот непридатний для нічних сирен через Rate Limits та DND, і чому обрано нативний мобільний клієнт.
2. **Zero-Knowledge Architecture:** Захист життя та персональних даних цивільного населення під час війни.
3. **Agentic & Deterministic Reliability:** Поєднання надшвидких евристик (< 0.2 мс) із повною ізоляцією хибних тривог.
4. **Виробнича готовність:** Повністю робочий Python-сервер, зібраний 16.4 МБ APK, пройдена батарея тестів та CI/CD релізний контур.
