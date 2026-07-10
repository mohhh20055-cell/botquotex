#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Volcano Bot API Server - لوحة تحكم كاملة للبوت
"""

import os
import sys
import json
import threading
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# Add parent directory (botquotex) to path so quotexapi can use relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    return jsonify({"status": "error", "message": str(e)}), 500

# Global variables
logs = {"time": datetime.now().strftime("%H:%M:%S"), "message": "Volcano Bot Ready!"}


# HTML Template للواجهة الكاملة
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Volcano Bot - لوحة التحكم</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { text-align: center; color: #ff6b6b; font-size: 2.5em; margin-bottom: 10px; text-shadow: 0 0 30px rgba(255,107,107,0.5); }
        .subtitle { text-align: center; color: #aaa; margin-bottom: 30px; }
        
        .status-bar {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 30px;
            padding: 20px;
            background: rgba(0,0,0,0.4);
            border-radius: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .status-item { text-align: center; }
        .status-dot {
            width: 15px; height: 15px;
            border-radius: 50%;
            display: inline-block;
            animation: blink 1.5s infinite;
        }
        .status-dot.green { background: #00ff88; box-shadow: 0 0 15px #00ff88; }
        .status-dot.red { background: #ff4444; box-shadow: 0 0 15px #ff4444; }
        .status-dot.yellow { background: #ffdd00; box-shadow: 0 0 15px #ffdd00; }
        .status-dot.orange { background: #ff9500; box-shadow: 0 0 15px #ff9500; }
        @keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }
        .card {
            background: linear-gradient(145deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            border-radius: 20px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        .card h2 {
            color: #ff6b6b;
            margin-bottom: 20px;
            font-size: 1.2em;
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 2px solid rgba(255,107,107,0.3);
            padding-bottom: 10px;
        }
        
        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 10px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: bold;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(255,107,107,0.4); }
        
        .btn-connect { background: linear-gradient(135deg, #00ff88, #00b894); color: #000; width: 100%; }
        .btn-disconnect { background: linear-gradient(135deg, #ff4444, #ff6b6b); color: #fff; width: 100%; }
        .btn-start { background: linear-gradient(135deg, #00b4d8, #0077b6); color: #fff; }
        .btn-stop { background: linear-gradient(135deg, #ff9500, #ff6b6b); color: #fff; }
        .btn-enable { background: linear-gradient(135deg, #00ff88, #00b894); color: #000; }
        .btn-disable { background: linear-gradient(135deg, #ff4444, #ff6b6b); color: #fff; }
        
        .btn-group { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-top: 15px; }
        
        .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .form-group { display: flex; flex-direction: column; gap: 5px; }
        .form-group.full { grid-column: span 2; }
        .form-group label { color: #aaa; font-size: 0.9em; }
        .form-group input, .form-group select {
            padding: 12px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 10px;
            background: rgba(0,0,0,0.3);
            color: #fff;
            font-size: 1em;
        }
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #ff6b6b;
            box-shadow: 0 0 10px rgba(255,107,107,0.3);
        }
        
        .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .stat-box {
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
        }
        .stat-box .label { color: #888; font-size: 0.85em; }
        .stat-box .value { font-size: 1.5em; font-weight: bold; color: #fff; margin-top: 5px; }
        .stat-box .value.green { color: #00ff88; }
        .stat-box .value.red { color: #ff4444; }
        .stat-box .value.blue { color: #00b4d8; }
        .stat-box .value.orange { color: #ff9500; }
        
        .progress-bar {
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 5px;
            overflow: hidden;
            margin-top: 10px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #00b894);
            border-radius: 5px;
            transition: width 0.5s ease;
        }
        
        .log-box {
            background: rgba(0,0,0,0.4);
            border-radius: 10px;
            padding: 15px;
            max-height: 300px;
            overflow-y: auto;
            font-family: 'Consolas', monospace;
            font-size: 0.85em;
            direction: ltr;
            text-align: left;
        }
        .log-entry { padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .log-time { color: #666; }
        .log-win { color: #00ff88; }
        .log-loss { color: #ff4444; }
        .log-signal { color: #00b4d8; }
        .log-error { color: #ff9500; }
        .log-info { color: #888; }
        
        .alert-box {
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
            font-size: 0.9em;
        }
        .alert-warning { background: rgba(255,149,0,0.2); border: 1px solid rgba(255,149,0,0.5); color: #ff9500; }
        .alert-success { background: rgba(0,255,136,0.2); border: 1px solid rgba(0,255,136,0.5); color: #00ff88; }
        
        .signal-info {
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
            direction: ltr;
            text-align: left;
        }
        .signal-info code {
            color: #00ff88;
            background: rgba(0,255,136,0.1);
            padding: 2px 8px;
            border-radius: 5px;
            display: block;
            margin-top: 5px;
        }
        
        .footer { text-align: center; margin-top: 30px; color: #666; padding: 20px; }
        
        .toggle-container { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; }
        .toggle { position: relative; width: 50px; height: 26px; }
        .toggle input { opacity: 0; width: 0; height: 0; }
        .toggle-slider {
            position: absolute;
            cursor: pointer;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(255,255,255,0.1);
            border-radius: 26px;
            transition: 0.3s;
        }
        .toggle-slider:before {
            position: absolute;
            content: "";
            height: 20px; width: 20px;
            left: 3px; bottom: 3px;
            background: white;
            border-radius: 50%;
            transition: 0.3s;
        }
        .toggle input:checked + .toggle-slider { background: #00ff88; }
        .toggle input:checked + .toggle-slider:before { transform: translateX(24px); }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 Volcano Profit Trading Bot</h1>
        <p class="subtitle">Volcano Bot - لوحة تحكم التداول الآلي</p>
        
        <!-- Status Bar -->
        <div class="status-bar">
            <div class="status-item">
                <div id="status-connected" class="status-dot {{ 'green' if status.get('connected') else 'red' }}"></div>
                <div id="status-connected-text">{{ 'متصل' if status.get('connected') else 'غير متصل' }}</div>
            </div>
            <div class="status-item">
                <div id="status-running" class="status-dot {{ 'green' if status.get('running') else 'red' }}"></div>
                <div id="status-running-text">{{ ' працює' if status.get('running') else 'متوقف' }}</div>
            </div>
            <div class="status-item">
                <div id="status-trading" class="status-dot {{ 'yellow' if status.get('trading_enabled') else 'orange' }}"></div>
                <div id="status-trading-text">{{ 'التداول مفعل' if status.get('trading_enabled') else 'التداول معطل' }}</div>
            </div>
            <div class="status-item">
                <span id="balance-value" style="font-size: 1.5em; font-weight: bold;">${{ "%.2f"|format(status.get('balance', 0)) }}</span>
                <div>الرصيد</div>
            </div>
        </div>
        
        <div class="grid">
            <!-- حساب Quotex -->
            <div class="card">
                <h2>👤 حساب Quotex</h2>
                <form id="loginForm" onsubmit="saveLogin(event)">
                    <div class="form-group">
                        <label>📧 البريد الإلكتروني</label>
                        <input type="email" id="email" value="{{ config.get('email', '') }}" placeholder="example@email.com">
                    </div>
                    <div class="form-group">
                        <label>🔐 كلمة المرور</label>
                        <input type="password" id="password" value="{{ config.get('password', '') }}" placeholder="••••••••">
                    </div>
                    <div class="btn-group">
                        <button type="submit" class="btn btn-connect">💾 حفظ البيانات</button>
                    </div>
                </form>
                <div class="alert-box alert-warning">
                    ⚠️ <b>الوضع التجريبي:</b> يعمل بحساب Demo افتراضي
                </div>
            </div>
            
            <!-- إعدادات التداول -->
            <div class="card">
                <h2>⚙️ إعدادات التداول</h2>
                <form id="tradeForm" onsubmit="saveSettings(event)">
                    <div class="form-grid">
                        <div class="form-group">
                            <label>💰 أقل مبلغ</label>
                            <input type="number" id="min_amount" value="{{ config.get('min_amount', 1) }}" min="1" max="100" step="0.1">
                        </div>
                        <div class="form-group">
                            <label>💰 أعلى مبلغ</label>
                            <input type="number" id="max_amount" value="{{ config.get('max_amount', 100) }}" min="1" max="1000" step="1">
                        </div>
                    </div>
                    
                    <div class="toggle-container">
                        <span>🔄 تداول تلقائي</span>
                        <label class="toggle">
                            <input type="checkbox" id="auto_trade" {{ 'checked' if config.get('auto_trade') else '' }}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                    
                    <div class="btn-group">
                        <button type="submit" class="btn btn-connect">💾 حفظ الإعدادات</button>
                    </div>
                </form>
            </div>
            
            <!-- التحكم بالبوت -->
            <div class="card">
                <h2>🎮 التحكم بالبوت</h2>
                <div class="btn-group">
                    <button class="btn btn-start" onclick="startBot()">▶️ تشغيل البوت</button>
                    <button class="btn btn-stop" onclick="stopBot()">⏹️ إيقاف</button>
                </div>
                <div class="btn-group">
                    <button class="btn btn-enable" onclick="enableTrading()">✅ تفعيل التداول</button>
                    <button class="btn btn-disable" onclick="disableTrading()">🚫 إيقاف التداول</button>
                </div>
                
                <div class="signal-info">
                    <strong>📁 ملف الإشارات:</strong>
                    <code>SignalsLog.txt</code>
                    <small style="color: #888; display: block; margin-top: 10px;">
                        MT4 يكتب الإشارات في هذا الملف والبوت يقرأها تلقائياً
                    </small>
                </div>
            </div>
            
            <!-- إشارة يدوية -->
            <div class="card">
                <h2>📨 إشارة يدوية</h2>
                <form onsubmit="sendSignal(event)">
                    <div class="form-group">
                        <label>📊 الأداة المالية</label>
                        <select id="asset">
                            <option value="EUR/USD">EUR/USD</option>
                            <option value="GBP/USD">GBP/USD</option>
                            <option value="USD/JPY">USD/JPY</option>
                            <option value="AUD/USD">AUD/USD</option>
                            <option value="USD/CAD">USD/CAD</option>
                            <option value="GBP/JPY">GBP/JPY</option>
                            <option value="EUR/GBP">EUR/GBP</option>
                            <option value="EUR/JPY">EUR/JPY</option>
                            <option value="BTC/USD">BTC/USD</option>
                            <option value="ETH/USD">ETH/USD</option>
                            <option value="XAU/USD">XAU/USD (Gold)</option>
                        </select>
                    </div>
                    <div class="form-grid">
                        <div class="form-group">
                            <label>📈 الاتجاه</label>
                            <select id="direction">
                                <option value="CALL">📈 CALL (أعلى)</option>
                                <option value="PUT">📉 PUT (أسفل)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>⏱️ المدة</label>
                            <select id="duration">
                                <option value="30">30 ثانية</option>
                                <option value="60" selected>60 ثانية</option>
                                <option value="120">2 دقيقة</option>
                                <option value="180">3 دقيقة</option>
                                <option value="300">5 دقيقة</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>💵 المبلغ ($)</label>
                        <input type="number" id="amount" value="1" min="1" max="100" step="0.1">
                    </div>
                    <button type="submit" class="btn btn-enable" style="width: 100%; margin-top: 10px;">🚀 تنفيذ الصفقة</button>
                </form>
            </div>
            
            <!-- الإحصائيات -->
            <div class="card">
                <h2>📊 إحصائيات التداول</h2>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="label">العمليات الرابحة</div>
                        <div class="value green">{{ status.get('win_count', 0) }}</div>
                    </div>
                    <div class="stat-box">
                        <div class="label">العمليات الخاسرة</div>
                        <div class="value red">{{ status.get('loss_count', 0) }}</div>
                    </div>
                    <div class="stat-box">
                        <div class="label">نسبة الربح</div>
                        <div class="value blue">{{ "%.1f"|format((status.get('win_rate', 0) or 0) * 100) }}%</div>
                    </div>
                    <div class="stat-box">
                        <div class="label">إجمالي العمليات</div>
                        <div class="value orange">{{ status.get('total_trades', 0) }}</div>
                    </div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ (status.get('win_rate', 0) or 0) * 100 }}%"></div>
                </div>
            </div>
            
            <!-- سجل العمليات -->
            <div class="card">
                <h2>📋 سجل العمليات</h2>
                <div class="log-box" id="logContainer">
                    <div class="log-entry">
                        <span class="log-time">[{{ logs.time }}]</span>
                        <span class="log-info">{{ logs.message }}</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Volcano Bot v1.0 | Trading Automation</p>
            <p style="font-size: 0.8em; margin-top: 10px;">يتابع ملف SignalsLog.txt تلقائياً من MT4</p>
        </div>
    </div>
    
    <script>
        function addLog(message, type = 'info') {
            const container = document.getElementById('logContainer');
            const now = new Date();
            const time = now.toLocaleTimeString();
            
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.innerHTML = '<span class="log-time">[' + time + ']</span> <span class="log-' + type + '">' + message + '</span>';
            container.insertBefore(entry, container.firstChild);
            
            while (container.children.length > 50) {
                container.removeChild(container.lastChild);
            }
        }
        
        async function saveLogin(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            try {
                await fetch('/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                addLog('✅ تم حفظ بيانات الحساب', 'success');
            } catch (e) {
                addLog('❌ خطأ: ' + e.message, 'error');
            }
        }
        
        async function saveSettings(e) {
            e.preventDefault();
            const min_amount = parseFloat(document.getElementById('min_amount').value);
            const max_amount = parseFloat(document.getElementById('max_amount').value);
            const auto_trade = document.getElementById('auto_trade').checked;
            
            try {
                await fetch('/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ min_amount, max_amount, auto_trade })
                });
                addLog('✅ تم حفظ إعدادات التداول', 'success');
            } catch (e) {
                addLog('❌ خطأ: ' + e.message, 'error');
            }
        }
        
        async function startBot() {
            try {
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                const response = await fetch('/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const data = await response.json();
                addLog(data.status === 'success' ? '✅ تم تشغيل البوت' : '❌ ' + data.message, data.status === 'success' ? 'success' : 'error');
                setTimeout(() => location.reload(), 1000);
            } catch (e) {
                addLog('❌ خطأ: ' + e.message, 'error');
            }
        }
        
        async function stopBot() {
            try {
                const response = await fetch('/stop', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
                const data = await response.json();
                addLog(data.status === 'success' ? '⏹️ تم إيقاف البوت' : '❌ ' + data.message, data.status === 'success' ? 'success' : 'error');
                setTimeout(() => location.reload(), 1000);
            } catch (e) {
                addLog('❌ خطأ: ' + e.message, 'error');
            }
        }
        
        async function enableTrading() {
            try {
                const response = await fetch('/enable', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
                const data = await response.json();
                addLog(data.status === 'success' ? '✅ تم تفعيل التداول' : '❌ ' + data.message, data.status === 'success' ? 'success' : 'error');
                setTimeout(() => location.reload(), 500);
            } catch (e) {
                addLog('❌ خطأ: ' + e.message, 'error');
            }
        }
        
        async function disableTrading() {
            try {
                const response = await fetch('/disable', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
                const data = await response.json();
                addLog(data.status === 'success' ? '🚫 تم إيقاف التداول' : '❌ ' + data.message, data.status === 'success' ? 'success' : 'error');
                setTimeout(() => location.reload(), 500);
            } catch (e) {
                addLog('❌ خطأ: ' + e.message, 'error');
            }
        }
        
        async function sendSignal(e) {
            e.preventDefault();
            const data = {
                asset: document.getElementById('asset').value,
                direction: document.getElementById('direction').value,
                amount: parseFloat(document.getElementById('amount').value),
                duration: parseInt(document.getElementById('duration').value)
            };
            
            try {
                const response = await fetch('/signal', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                if (result.status === 'success') {
                    addLog('📨 إشارة مُنفذة: ' + data.asset + ' ' + data.direction + ' $' + data.amount, 'signal');
                } else {
                    addLog('❌ خطأ: ' + result.message, 'error');
                }
            } catch (e) {
                addLog('❌ خطأ: ' + e.message, 'error');
            }
        }
        
        // Auto refresh status only (no page reload)
        setInterval(() => {
            fetch('/status').then(r => r.json()).then(d => {
                if(d.status !== 'error' && d.status !== undefined) {
                    document.getElementById('status-connected').className = 'status-dot ' + (d.connected ? 'green' : 'red');
                    document.getElementById('status-connected-text').textContent = d.connected ? 'متصل' : 'غير متصل';
                    document.getElementById('status-running').className = 'status-dot ' + (d.running ? 'green' : 'red');
                    document.getElementById('status-running-text').textContent = d.running ? ' працює' : 'متوقف';
                    document.getElementById('status-trading').className = 'status-dot ' + (d.trading_enabled ? 'yellow' : 'orange');
                    document.getElementById('status-trading-text').textContent = d.trading_enabled ? 'التداول مفعل' : 'التداول معطل';
                    if(d.balance) document.getElementById('balance-value').textContent = '$' + d.balance.toFixed(2);
                }
            });
        }, 3000);
        
        addLog('🔥 لوحة التحكم جاهزة', 'info');
    </script>
</body>
</html>
'''


class BotManager:
    """Manages the trading bot"""
    
    def __init__(self):
        self.bot = None
        self.status = "stopped"
        self.config = {
            "email": os.getenv("QUOTEX_EMAIL", ""),
            "password": os.getenv("QUOTEX_PASSWORD", ""),
            "demo": True,
            "min_amount": 1.0,
            "max_amount": 100.0,
            "auto_trade": True
        }
    
    def start_bot(self, config: dict = None):
        """Start the bot"""
        if config:
            self.config.update(config)
        
        try:
            from volcano_headless import HeadlessQuotexBot
            
            self.bot = HeadlessQuotexBot(
                email=self.config.get("email") or None,
                password=self.config.get("password") or None,
                auto_trade=self.config.get("auto_trade", True),
                min_amount=self.config.get("min_amount", 1.0),
                max_amount=self.config.get("max_amount", 100.0),
                demo=self.config.get("demo", True)
            )
            
            thread = threading.Thread(target=self._run_bot, daemon=True)
            thread.start()
            
            self.status = "running"
            return {"status": "success", "message": "Bot started"}
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            return {"status": "error", "message": str(e)}
    
    def _run_bot(self):
        """Run the bot (blocking)"""
        try:
            self.bot.start()
        except Exception as e:
            logger.error(f"Bot error: {e}")
            self.status = "error"
    
    def stop_bot(self):
        """Stop the bot"""
        if self.bot:
            self.bot.stop()
            self.bot = None
        self.status = "stopped"
        return {"status": "success", "message": "Bot stopped"}
    
    def get_status(self):
        """Get bot status"""
        if not self.bot:
            return {
                "status": "stopped",
                "running": False,
                "connected": False,
                "trading_enabled": False,
                "balance": 0,
                "win_count": 0,
                "loss_count": 0,
                "win_rate": 0,
                "total_trades": 0
            }
        
        try:
            bot_status = self.bot.get_status()
            return {
                "status": self.status,
                "running": bot_status.get("running", False),
                "connected": bot_status.get("connected", False),
                "trading_enabled": bot_status.get("trading_enabled", False),
                "balance": bot_status.get("balance", 0),
                "win_count": bot_status.get("win_count", 0),
                "loss_count": bot_status.get("loss_count", 0),
                "win_rate": bot_status.get("win_rate", 0),
                "total_trades": bot_status.get("total_trades", 0)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def enable_trading(self):
        """Enable trading"""
        if self.bot:
            self.bot.enable_trading()
            return {"status": "success"}
        return {"status": "error", "message": "Bot not running"}
    
    def disable_trading(self):
        """Disable trading"""
        if self.bot:
            self.bot.disable_trading()
            return {"status": "success"}
        return {"status": "error", "message": "Bot not running"}
    
    def execute_signal(self, signal_data: dict):
        """Execute a trading signal"""
        if not self.bot or not self.bot.connected:
            return {"status": "error", "message": "Bot not connected"}
        
        try:
            from volcano_headless import TradingSignal
            signal = TradingSignal(signal_data)
            result = self.bot.execute_trade(signal)
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Initialize bot manager
manager = BotManager()


# API Routes

@app.route('/')
def index():
    """Home page with web interface"""
    status = manager.get_status()
    config = manager.config
    return render_template_string(HTML_TEMPLATE, status=status, config=config, logs=logs)


@app.route('/health')
def health():
    """Health check"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


@app.route('/start', methods=['POST'])
def start_bot():
    """Start the bot"""
    data = request.get_json() or {}
    result = manager.start_bot(data)
    return jsonify(result)


@app.route('/stop', methods=['POST'])
def stop_bot():
    """Stop the bot"""
    result = manager.stop_bot()
    return jsonify(result)


@app.route('/status')
def get_status():
    """Get bot status"""
    status = manager.get_status()
    return jsonify(status)


@app.route('/enable', methods=['POST'])
def enable_trading():
    """Enable trading"""
    result = manager.enable_trading()
    return jsonify(result)


@app.route('/disable', methods=['POST'])
def disable_trading():
    """Disable trading"""
    result = manager.disable_trading()
    return jsonify(result)


@app.route('/signal', methods=['POST'])
def execute_signal():
    """Execute a trading signal"""
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "No signal data provided"}), 400
    
    required = ['asset', 'direction', 'amount']
    missing = [f for f in required if f not in data]
    
    if missing:
        return jsonify({
            "status": "error", 
            "message": f"Missing required fields: {missing}"
        }), 400
    
    result = manager.execute_signal(data)
    return jsonify(result)


@app.route('/config', methods=['GET', 'POST'])
def config():
    """Get or update config"""
    if request.method == 'GET':
        return jsonify(manager.config)
    
    data = request.get_json()
    if data:
        manager.config.update(data)
    return jsonify(manager.config)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Volcano Bot API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
