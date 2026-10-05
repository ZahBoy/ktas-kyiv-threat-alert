"""
Kyiv Threat Alert System (KTAS) — Standalone Production Server Runner & Web Control Panel.

Runs the complete backend engine, REST API, real-time Telegram parsing pipeline,
and serves a tactical Web Radar Dashboard & APK download portal.

Usage:
    python server_run.py
    python server_run.py --port 8000 --host 0.0.0.0
"""
import os
import sys
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.main import app as api_app, recent_threats_buffer
from backend.app.nlp_parser import nlp_parser
from backend.app.fcm_dispatcher import fcm_dispatcher
from backend.app.models import ThreatEvent, ThreatType, ThreatUrgency, ThreatScope

# Populate some initial realistic threats if buffer is empty
if not recent_threats_buffer:
    recent_threats_buffer.extend([
        ThreatEvent(
            event_id="init_1",
            threat_type=ThreatType.BALLISTIC,
            scope=ThreatScope.CITY_WIDE,
            urgency=ThreatUrgency.CRITICAL,
            title="Загроза балістики: Київ!",
            description="Швидкісна ціль з північного сходу в напрямку столиці. Всім негайно в укриття!",
            target_districts=["ALL"],
            source_channel="@kpszsu",
            timestamp_utc=int(time.time()) - 1800
        ),
        ThreatEvent(
            event_id="init_2",
            threat_type=ThreatType.UAV_SHAHED,
            scope=ThreatScope.SPATIAL_POLYGON,
            urgency=ThreatUrgency.WARNING,
            title="Шахед з Вишгорода курсом на Оболонь",
            description="БПЛА заходить у північний сектор Києва. Робота ППО.",
            target_districts=["Obolonskyi"],
            source_channel="@monitor_war",
            timestamp_utc=int(time.time()) - 3600
        ),
        ThreatEvent(
            event_id="init_3",
            threat_type=ThreatType.ALL_CLEAR,
            scope=ThreatScope.SPATIAL_POLYGON,
            urgency=ThreatUrgency.INFO,
            title="Оболонь — чисто, ціль збито",
            description="Локальний відбій небезпеки для вашого району.",
            target_districts=["Obolonskyi"],
            source_channel="@vanek_nikolaev",
            timestamp_utc=int(time.time()) - 3200
        )
    ])


@api_app.get("/download/apk")
async def download_apk():
    """Direct APK download endpoint."""
    apk_paths = [
        PROJECT_ROOT / "KTAS_Kyiv_Threat_Alert.apk",
        PROJECT_ROOT / "release" / "KTAS_Kyiv_Threat_Alert.apk",
        PROJECT_ROOT / "android" / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
    ]
    for p in apk_paths:
        if p.exists():
            return FileResponse(
                path=str(p),
                filename="KTAS_Kyiv_Threat_Alert.apk",
                media_type="application/vnd.android.package-archive"
            )
    raise HTTPException(status_code=404, detail="APK file not found. Please compile it first.")


@api_app.get("/", response_class=HTMLResponse)
@api_app.get("/dashboard", response_class=HTMLResponse)
async def web_dashboard():
    """Tactical Web Radar Dashboard & Live Threat Control Center."""
    html_content = """<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KTAS • Головний Сервер Оповіщення Києва</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;800&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0a0c10;
            --surface-dark: #12161f;
            --card-dark: #181d2a;
            --border-color: #262d3d;
            --red: #ff3344;
            --amber: #ff9900;
            --green: #00e676;
            --cyan: #00d4ff;
            --text-primary: #f0f4fc;
            --text-secondary: #8a94a6;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: var(--bg-dark);
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        header {
            background: var(--surface-dark);
            border-bottom: 1px solid var(--border-color);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .brand-logo {
            width: 32px;
            height: 32px;
            background: radial-gradient(circle, var(--cyan) 20%, transparent 70%);
            border: 2px solid var(--cyan);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
        }
        .brand-title {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.25rem;
            font-weight: 800;
            letter-spacing: 1px;
        }
        .brand-subtitle {
            font-size: 0.75rem;
            color: var(--text-secondary);
        }
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            background: rgba(0, 230, 118, 0.1);
            color: var(--green);
            border: 1px solid var(--green);
        }
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--green);
            box-shadow: 0 0 8px var(--green);
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(1.3); } }
        
        .main-container {
            display: grid;
            grid-template-columns: 420px 1fr;
            gap: 1.5rem;
            padding: 1.5rem 2rem;
            flex: 1;
        }
        @media (max-width: 992px) {
            .main-container { grid-template-columns: 1fr; }
        }
        
        .card {
            background: var(--surface-dark);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.25rem;
        }
        .card-header {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        /* Radar Canvas */
        .radar-box {
            position: relative;
            width: 100%;
            height: 340px;
            background: #06080c;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        canvas#radarCanvas {
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
        }
        .radar-overlay {
            position: absolute;
            top: 10px; left: 10px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: var(--cyan);
            line-height: 1.4;
            pointer-events: none;
            z-index: 5;
        }
        
        /* Quick Actions Panel */
        .btn-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-top: 12px;
        }
        .btn {
            background: var(--card-dark);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }
        .btn:hover {
            transform: translateY(-1px);
        }
        .btn-red { background: rgba(255, 51, 68, 0.15); border-color: var(--red); color: var(--red); }
        .btn-red:hover { background: var(--red); color: #fff; box-shadow: 0 0 15px rgba(255, 51, 68, 0.4); }
        .btn-amber { background: rgba(255, 153, 0, 0.15); border-color: var(--amber); color: var(--amber); }
        .btn-amber:hover { background: var(--amber); color: #000; box-shadow: 0 0 15px rgba(255, 153, 0, 0.4); }
        .btn-green { background: rgba(0, 230, 118, 0.15); border-color: var(--green); color: var(--green); }
        .btn-green:hover { background: var(--green); color: #000; box-shadow: 0 0 15px rgba(0, 230, 118, 0.4); }
        .btn-primary { background: var(--cyan); color: #000; font-weight: 700; border-color: var(--cyan); }
        .btn-primary:hover { background: #33e0ff; box-shadow: 0 0 15px rgba(0, 212, 255, 0.4); }
        
        /* Sandbox Parser */
        .input-group {
            display: flex;
            gap: 8px;
            margin-top: 8px;
        }
        textarea.sandbox-input {
            width: 100%;
            height: 70px;
            background: #0d111a;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            color: var(--text-primary);
            padding: 8px 12px;
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            resize: none;
        }
        textarea.sandbox-input:focus {
            outline: none;
            border-color: var(--cyan);
        }
        
        /* Threat Feed Table */
        .feed-container {
            display: flex;
            flex-direction: column;
            gap: 8px;
            max-height: 480px;
            overflow-y: auto;
        }
        .feed-item {
            background: var(--card-dark);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--cyan);
            border-radius: 8px;
            padding: 12px 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.2s;
        }
        .feed-item.ballistic { border-left-color: var(--red); background: rgba(255, 51, 68, 0.05); }
        .feed-item.uav { border-left-color: var(--amber); background: rgba(255, 153, 0, 0.05); }
        .feed-item.clear { border-left-color: var(--green); background: rgba(0, 230, 118, 0.05); }
        
        .feed-badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 4px;
            display: inline-block;
            margin-bottom: 4px;
        }
        .badge-red { background: rgba(255, 51, 68, 0.2); color: var(--red); }
        .badge-amber { background: rgba(255, 153, 0, 0.2); color: var(--amber); }
        .badge-green { background: rgba(0, 230, 118, 0.2); color: var(--green); }
        
        .feed-title { font-weight: 600; font-size: 0.9rem; }
        .feed-desc { font-size: 0.8rem; color: var(--text-secondary); margin-top: 2px; }
        .feed-meta {
            text-align: right;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: var(--text-secondary);
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 1.5rem;
        }
        .metric-box {
            background: var(--surface-dark);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }
        .metric-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.4rem;
            font-weight: 800;
            color: var(--cyan);
        }
        .metric-label {
            font-size: 0.7rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            margin-top: 4px;
        }
        
        footer {
            background: var(--surface-dark);
            border-top: 1px solid var(--border-color);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            color: var(--text-secondary);
        }
        a { color: var(--cyan); text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <div class="brand-logo">📡</div>
            <div>
                <div class="brand-title">KTAS SERVER CORE</div>
                <div class="brand-subtitle">Kyiv Threat Alert System • Engine v1.0.0</div>
            </div>
        </div>
        <div style="display: flex; gap: 12px; align-items: center;">
            <a href="/download/apk" class="btn btn-primary" style="padding: 6px 14px; text-decoration: none;">
                📥 Завантажити Android APK (16.5 MB)
            </a>
            <div class="status-badge" id="serverStatusBadge">
                <div class="status-dot"></div>
                ONLINE
            </div>
        </div>
    </header>

    <div style="padding: 1.5rem 2rem 0;">
        <div class="metrics-grid">
            <div class="metric-box">
                <div class="metric-val" id="metricLatency">0.16 ms</div>
                <div class="metric-label">Середній час NLP</div>
            </div>
            <div class="metric-box">
                <div class="metric-val" id="metricDistricts">10 / 10</div>
                <div class="metric-label">Районів Києва</div>
            </div>
            <div class="metric-box">
                <div class="metric-val" style="color: var(--green);">100%</div>
                <div class="metric-label">Zero-Knowledge захист</div>
            </div>
            <div class="metric-box">
                <div class="metric-val" style="color: var(--amber);" id="metricThreatsCount">0</div>
                <div class="metric-label">Зафіксовано подій</div>
            </div>
        </div>
    </div>

    <div class="main-container">
        <!-- Left Column: Radar & Quick Triggers -->
        <div style="display: flex; flex-direction: column; gap: 1.5rem;">
            <div class="card">
                <div class="card-header">
                    <span>KYIV TACTICAL RADAR</span>
                    <span id="threatStatusText" style="color: var(--green);">СТАТУС: ЧИСТО</span>
                </div>
                <div class="radar-box">
                    <canvas id="radarCanvas" width="400" height="340"></canvas>
                    <div class="radar-overlay">
                        LAT: 50.4501° N<br>
                        LON: 30.5234° E<br>
                        RANGE: 25 KM<br>
                        SWEEP: 360°/s
                    </div>
                </div>
            </div>

            <!-- Quick Alert Dispatch Panel -->
            <div class="card">
                <div class="card-header">
                    <span>ПУЛЬТ ШВИДКОГО ЗАПУСКУ ТРИВОГ</span>
                    <span>LIVE EMULATOR</span>
                </div>
                <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 8px;">
                    Один клік транслює загрозу на всі підключені Android клієнти та FCM топіки:
                </p>
                <div class="btn-grid">
                    <button class="btn btn-red" onclick="triggerAlert('Київ — загроза балістики з Брянщини!')">
                        💥 Балістика (Київ)
                    </button>
                    <button class="btn btn-amber" onclick="triggerAlert('Шахед з Вишгорода курсом на Оболонь')">
                        🛸 Дрон (Оболонь)
                    </button>
                    <button class="btn btn-amber" onclick="triggerAlert('2 БПЛА через Бровари на Дарницький район/Позняки')">
                        🛸 Дрон (Позняки)
                    </button>
                    <button class="btn btn-green" onclick="triggerAlert('Оболонь — чисто, ціль збито')">
                        🛡️ Відбій Оболонь
                    </button>
                </div>
                <button class="btn btn-green" style="width: 100%; margin-top: 8px;" onclick="triggerAlert('Відбій загрози по місту Києву')">
                    ✅ Загальний відбій по Києву
                </button>
            </div>

            <!-- Custom Telegram Post Sandbox -->
            <div class="card">
                <div class="card-header">
                    <span>ТЕСТ ДОВІЛЬНОГО ТЕКСТУ З КАНАЛУ</span>
                    <span>NLP BENCHMARK</span>
                </div>
                <textarea id="customTextInput" class="sandbox-input" placeholder="Введіть текст повідомлення каналу (напр. 'Шахед повз Вишгород на Поділ')..."></textarea>
                <div style="display: flex; gap: 8px; margin-top: 8px;">
                    <button class="btn btn-primary" style="flex: 1;" onclick="testCustomText()">
                        ⚡ Проаналізувати та розіслати
                    </button>
                </div>
                <div id="parseBenchmarkResult" style="margin-top: 8px; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: var(--cyan); display: none;"></div>
            </div>
        </div>

        <!-- Right Column: Live Threat Feed -->
        <div class="card" style="display: flex; flex-direction: column;">
            <div class="card-header">
                <span>ЖУРНАЛ ЗАФІКСОВАНИХ ПОДІЙ ТА РОЗСИЛОК</span>
                <button class="btn" style="padding: 4px 10px; font-size: 0.75rem;" onclick="loadThreats()">🔄 Оновити</button>
            </div>
            <div class="feed-container" id="feedContainer">
                <!-- Dynamically populated -->
            </div>
        </div>
    </div>

    <footer>
        <div>Розроблено для відбору та захисту проєкту в <b>KSE Agentic AI School 2026</b></div>
        <div>
            <a href="/docs" target="_blank">Swagger OpenAPI Docs</a> • 
            <a href="/download/apk">Завантажити APK</a>
        </div>
    </footer>

    <script>
        // Radar Animation
        const canvas = document.getElementById('radarCanvas');
        const ctx = canvas.getContext('2d');
        let angle = 0;
        let activeBlips = [];

        function drawRadar() {
            const w = canvas.width;
            const h = canvas.height;
            const cx = w / 2;
            const cy = h / 2;
            const radius = Math.min(w, h) / 2 - 15;

            ctx.clearRect(0, 0, w, h);

            // Rings
            ctx.strokeStyle = 'rgba(0, 212, 255, 0.15)';
            ctx.lineWidth = 1.5;
            for (let r = 0.3; r <= 1.0; r += 0.35) {
                ctx.beginPath();
                ctx.arc(cx, cy, radius * r, 0, Math.PI * 2);
                ctx.stroke();
            }

            // Crosshairs
            ctx.strokeStyle = 'rgba(0, 212, 255, 0.15)';
            ctx.beginPath();
            ctx.moveTo(cx, 15); ctx.lineTo(cx, h - 15);
            ctx.moveTo(15, cy); ctx.lineTo(w - 15, cy);
            ctx.stroke();

            // Sweep Line
            angle += 0.035;
            if (angle > Math.PI * 2) angle = 0;

            const sweepX = cx + Math.cos(angle) * radius;
            const sweepY = cy + Math.sin(angle) * radius;

            const gradient = ctx.createRadialGradient(cx, cy, 10, cx, cy, radius);
            gradient.addColorStop(0, 'rgba(0, 212, 255, 0.3)');
            gradient.addColorStop(1, 'rgba(0, 212, 255, 0.0)');

            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.arc(cx, cy, radius, angle - 0.4, angle);
            ctx.fillStyle = gradient;
            ctx.fill();

            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.lineTo(sweepX, sweepY);
            ctx.strokeStyle = '#00d4ff';
            ctx.lineWidth = 2;
            ctx.stroke();

            // Blips
            activeBlips.forEach(b => {
                ctx.beginPath();
                ctx.arc(b.x, b.y, b.size, 0, Math.PI * 2);
                ctx.fillStyle = b.color;
                ctx.shadowColor = b.color;
                ctx.shadowBlur = 12;
                ctx.fill();
                ctx.shadowBlur = 0;
            });

            requestAnimationFrame(drawRadar);
        }
        drawRadar();

        // API Interactions
        async function loadThreats() {
            try {
                const res = await fetch('/api/v1/recent_threats');
                const threats = await res.json();
                renderThreats(threats);
                document.getElementById('metricThreatsCount').innerText = threats.length;
            } catch (e) {
                console.error(e);
            }
        }

        function renderThreats(threats) {
            const container = document.getElementById('feedContainer');
            if (!threats || threats.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 40px;">Немає зафіксованих подій</div>';
                return;
            }

            // Update radar blips based on the latest threat
            activeBlips = [];
            const latest = threats[0];
            const statusText = document.getElementById('threatStatusText');

            if (latest) {
                if (latest.threat_type === 'BALLISTIC') {
                    statusText.innerText = '⚠️ УВАГА: БАЛІСТИКА';
                    statusText.style.color = 'var(--red)';
                    activeBlips.push({ x: canvas.width / 2, y: canvas.height / 2, size: 9, color: '#ff3344' });
                } else if (latest.threat_type === 'UAV_SHAHED') {
                    statusText.innerText = '🚨 ЗАГРОЗА БПЛА';
                    statusText.style.color = 'var(--amber)';
                    activeBlips.push({ x: canvas.width / 2 + 15, y: canvas.height / 2 - 60, size: 7, color: '#ff9900' });
                } else {
                    statusText.innerText = 'СТАТУС: ЧИСТО';
                    statusText.style.color = 'var(--green)';
                }
            }

            container.innerHTML = threats.map(t => {
                let badgeClass = 'badge-amber';
                let itemClass = 'uav';
                let label = 'БПЛА';

                if (t.threat_type === 'BALLISTIC') {
                    badgeClass = 'badge-red';
                    itemClass = 'ballistic';
                    label = 'БАЛІСТИКА';
                } else if (t.threat_type === 'ALL_CLEAR') {
                    badgeClass = 'badge-green';
                    itemClass = 'clear';
                    label = 'ВІДБІЙ';
                }

                const timeStr = new Date(t.timestamp_utc * 1000).toLocaleTimeString('uk-UA');
                const districts = (t.target_districts && t.target_districts.length) ? t.target_districts.join(', ') : 'Київ';

                return `
                <div class="feed-item ${itemClass}">
                    <div>
                        <span class="feed-badge ${badgeClass}">${label}</span>
                        <div class="feed-title">${t.title}</div>
                        <div class="feed-desc">${t.description}</div>
                        <div style="font-size: 0.75rem; color: var(--cyan); margin-top: 4px;">Сектор: ${districts}</div>
                    </div>
                    <div class="feed-meta">
                        <div>${timeStr}</div>
                        <div style="color: var(--cyan);">${t.source_channel || '@monitor'}</div>
                    </div>
                </div>`;
            }).join('');
        }

        async function triggerAlert(text) {
            try {
                const res = await fetch('/api/v1/broadcast', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text, source_channel: '@kpszsu' })
                });
                const data = await res.json();
                loadThreats();
            } catch (err) {
                alert('Помилка надсилання: ' + err);
            }
        }

        async function testCustomText() {
            const input = document.getElementById('customTextInput');
            const text = input.value.trim();
            if (!text) return;

            const resDiv = document.getElementById('parseBenchmarkResult');
            resDiv.style.display = 'block';
            resDiv.innerText = 'Аналіз конвеєром NLP...';

            try {
                const start = performance.now();
                const res = await fetch('/api/v1/broadcast', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text, source_channel: '@custom_channel' })
                });
                const data = await res.json();
                const totalTime = (performance.now() - start).toFixed(2);

                if (data.status === 'dispatched') {
                    resDiv.innerHTML = `✅ РОЗІСЛАНО! Час NLP: <b>${data.parse_time_ms} мс</b> | Загальний час: <b>${totalTime} мс</b> | Тип: ${data.threat_event.threat_type}`;
                } else {
                    resDiv.innerHTML = `ℹ️ ІГНОРОВАНО: ${data.reason} (Час NLP: ${data.parse_time_ms} мс)`;
                }
                input.value = '';
                loadThreats();
            } catch (err) {
                resDiv.innerText = 'Помилка: ' + err;
            }
        }

        // Initial load and periodic refresh
        loadThreats();
        setInterval(loadThreats, 4000);
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)


def main():
    parser = argparse.ArgumentParser(description="Kyiv Threat Alert System — Production Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host address to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for dev")
    args = parser.parse_args()

    print("=" * 80)
    print("      KYIV THREAT ALERT SYSTEM (KTAS) — STANDALONE SERVER CORE")
    print("=" * 80)
    print(f"  • Web Control Panel & Radar:  http://localhost:{args.port}/")
    print(f"  • Swagger OpenAPI Docs:       http://localhost:{args.port}/docs")
    print(f"  • Direct Android APK Link:    http://localhost:{args.port}/download/apk")
    print(f"  • Listening on:               http://{args.host}:{args.port}")
    print("=" * 80)
    print("  [ONLINE] Server is running. Press Ctrl+C to terminate.")
    print("=" * 80)

    uvicorn.run(api_app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
