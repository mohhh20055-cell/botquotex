#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Volcano Bot API Server
API Server للتواصل مع Headless Bot على Render
"""

import os
import sys
import json
import threading
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# HTML Template للواجهة
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Volcano Bot - لوحة التحكم</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        h1 {
            text-align: center;
            color: #e94560;
            font-size: 2.5em;
            margin-bottom: 30px;
            text-shadow: 0 0 20px rgba(233, 69, 96, 0.5);
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .card h2 {
            color: #e94560;
            margin-bottom: 20px;
            font-size: 1.3em;
            border-bottom: 2px solid #e94560;
            padding-bottom: 10px;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .status-dot {
            width: 15px;
            height: 15px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .status-dot.connected { background: #00ff88; box-shadow: 0 0 10px #00ff88; }
        .status-dot.disconnected { background: #ff4444; box-shadow: 0 0 10px #ff4444; }
        .status-dot.trading { background: #ffff00; box-shadow: 0 0 10px #ffff00; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .stat {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .stat-label { color: #aaa; }
        .stat-value { font-weight: bold; color: #e94560; }
        
        .btn {
            display: inline-block;
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
            margin: 5px;
        }
        
        .btn-success {
            background: linear-gradient(135deg, #00b894, #00cec9);
            color: white;
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #e94560, #ff6b6b);
            color: white;
        }
        
        .btn-warning {
            background: linear-gradient(135deg, #fdcb6e, #f39c12);
            color: #333;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(233, 69, 96, 0.4);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .button-group {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            margin-top: 20px;
        }
        
        .signal-form {
            display: grid;
            gap: 15px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .form-group label {
            color: #aaa;
            font-size: 0.9em;
        }
        
        .form-group input, .form-group select {
            padding: 12px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.05);
            color: white;
            font-size: 1em;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #e94560;
        }
        
        .log-container {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 15px;
            max-height: 300px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.85em;
        }
        
        .log-entry {
            padding: 5px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .log-time { color: #666; margin-left: 10px; }
        .log-success { color: #00ff88; }
        .log-error { color: #ff4444; }
        .log-info { color: #00b4d8; }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: #666;
        }
        
        .refresh-info {
            text-align: center;
            color: #666;
            margin-top: 10px;
        }
        
        .win-rate-bar {
            height: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            overflow: hidden;
            margin-top: 10px;
        }
        
        .win-rate-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #00b894);
            border-radius: 10px;
            transition: width 0.5s ease;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 Volcano Bot - لوحة التحكم</h1>
        
        <div class="dashboard">
            <!-- حالة البوت -->
            <div class="card">
                <h2>📊 حالة البوت</h2>
                <div class="status-indicator">
                    <div class="status-dot {{ 'connected' if status.connected else 'disconnected' }}"></div>
                    <span>{{ 'متصل' if status.connected else 'غير متصل' }}</span>
                </div>
                
                <div class="stat">
                    <span class="stat-label">الحالة:</span>
                    <span class="stat-value">{{ status.status }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">الرصيد:</span>
                    <span class="stat-value">${{ "%.2f"|format(status.get('balance', 0)) }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">العمليات الرابحة:</span>
                    <span class="stat-value">{{ status.get('win_count', 0) }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">العمليات الخاسرة:</span>
                    <span class="stat-value">{{ status.get('loss_count', 0) }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">نسبة الربح:</span>
                    <span class="stat-value">{{ "%.1f"|format((status.win_rate or 0) * 100) }}%</span>
                </div>
                
                <div class="win-rate-bar">
                    <div class="win-rate-fill" style="width: {{ (status.win_rate or 0) * 100 }}%"></div>
                </div>
            </div>
            
            <!-- التحكم -->
            <div class="card">
                <h2>🎮 التحكم</h2>
                <div class="button-group">
                    <button class="btn btn-success" onclick="startBot()">▶️ تشغيل البوت</button>
                    <button class="btn btn-danger" onclick="stopBot()">⏹️ إيقاف البوت</button>
                </div>
                <div class="button-group">
                    <button class="btn btn-warning" onclick="enableTrading()">✅ تفعيل التداول</button>
                    <button class="btn btn-warning" onclick="disableTrading()">🚫 إيقاف التداول</button>
                </div>
                <div class="refresh-info">
                    <button class="btn btn-warning" onclick="refreshStatus()">🔄 تحديث الحالة</button>
                </div>
            </div>
            
            <!-- إرسال إشارة -->
            <div class="card">
                <h2>📨 إرسال إشارة</h2>
                <form class="signal-form" onsubmit="sendSignal(event)">
                    <div class="form-group">
                        <label>الأداة (Asset)</label>
                        <select name="asset" id="asset">
                            <option value="EUR/USD">EUR/USD</option>
                            <option value="GBP/USD">GBP/USD</option>
                            <option value="USD/JPY">USD/JPY</option>
                            <option value="AUD/USD">AUD/USD</option>
                            <option value="USD/CAD">USD/CAD</option>
                            <option value="GBP/JPY">GBP/JPY</option>
                            <option value="EUR/GBP">EUR/GBP</option>
                            <option value="BTC/USD">BTC/USD</option>
                            <option value="ETH/USD">ETH/USD</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>الاتجاه (Direction)</label>
                        <select name="direction" id="direction">
                            <option value="CALL">📈 CALL (أعلى)</option>
                            <option value="PUT">📉 PUT (أسفل)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>المبلغ ($)</label>
                        <input type="number" name="amount" id="amount" value="1" min="1" max="100" step="0.1">
                    </div>
                    <div class="form-group">
                        <label>المدة (ثانية)</label>
                        <input type="number" name="duration" id="duration" value="60" min="30" max="300">
                    </div>
                    <button type="submit" class="btn btn-success" style="width: 100%">🚀 إرسال الإشارة</button>
                </form>
            </div>
            
            <!-- السجل -->
            <div class="card">
                <h2>📋 السجل</h2>
                <div class="log-container" id="logContainer">
                    <div class="log-entry">
                        <span class="log-time">{{ logs.time }}</span>
                        <span class="log-info">{{ logs.message }}</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Volcano Bot API v1.0.0 | لوحة التحكم</p>
        </div>
    </div>
    
    <script>
        async function startBot() {
            try {
                const response = await fetch('/start', { method: 'POST' });
                const data = await response.json();
                addLog(data.status === 'success' ? 'تم تشغيل البوت بنجاح!' : 'خطأ: ' + data.message, data.status === 'success' ? 'success' : 'error');
                refreshStatus();
            } catch (e) {
                addLog('خطأ في الاتصال: ' + e.message, 'error');
            }
        }
        
        async function stopBot() {
            try {
                const response = await fetch('/stop', { method: 'POST' });
                const data = await response.json();
                addLog(data.status === 'success' ? 'تم إيقاف البوت!' : 'خطأ: ' + data.message, data.status === 'success' ? 'success' : 'error');
                refreshStatus();
            } catch (e) {
                addLog('خطأ في الاتصال: ' + e.message, 'error');
            }
        }
        
        async function enableTrading() {
            try {
                const response = await fetch('/enable', { method: 'POST' });
                const data = await response.json();
                addLog(data.status === 'success' ? 'تم تفعيل التداول!' : 'خطأ: ' + data.message, data.status === 'success' ? 'success' : 'error');
                refreshStatus();
            } catch (e) {
                addLog('خطأ في الاتصال: ' + e.message, 'error');
            }
        }
        
        async function disableTrading() {
            try {
                const response = await fetch('/disable', { method: 'POST' });
                const data = await response.json();
                addLog(data.status === 'success' ? 'تم إيقاف التداول!' : 'خطأ: ' + data.message, data.status === 'success' ? 'success' : 'error');
                refreshStatus();
            } catch (e) {
                addLog('خطأ في الاتصال: ' + e.message, 'error');
            }
        }
        
        async function sendSignal(e) {
            e.preventDefault();
            const form = e.target;
            const data = {
                asset: form.asset.value,
                direction: form.direction.value,
                amount: parseFloat(form.amount.value),
                duration: parseInt(form.duration.value)
            };
            
            try {
                const response = await fetch('/signal', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                if (result.status === 'success') {
                    addLog('تم إرسال الإشارة: ' + data.asset + ' ' + data.direction + ' $' + data.amount, 'success');
                } else {
                    addLog('خطأ: ' + result.message, 'error');
                }
                refreshStatus();
            } catch (e) {
                addLog('خطأ في الاتصال: ' + e.message, 'error');
            }
        }
        
        async function refreshStatus() {
            try {
                const response = await fetch('/status');
                const data = await response.json();
                if (data.status !== 'error') {
                    location.reload();
                }
            } catch (e) {
                console.log('Auto-refresh skipped');
            }
        }
        
        function addLog(message, type = 'info') {
            const container = document.getElementById('logContainer');
            const now = new Date();
            const time = now.toLocaleTimeString('ar');
            
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.innerHTML = '<span class="log-time">' + time + '</span><span class="log-' + type + '">' + message + '</span>';
            container.insertBefore(entry, container.firstChild);
            
            // Keep only last 20 logs
            while (container.children.length > 20) {
                container.removeChild(container.lastChild);
            }
        }
        
        // Auto refresh every 10 seconds
        setInterval(refreshStatus, 10000);
    </script>
</body>
</html>
'''

# Global bot instance
bot_instance = None
bot_lock = threading.Lock()
logs = {"time": datetime.now().strftime("%H:%M:%S"), "message": "مرحباً بك في Volcano Bot!"}


class BotManager:
    """Manages the trading bot"""
    
    def __init__(self):
        self.bot = None
        self.status = "stopped"
        self.config = {
            "email": os.getenv("QUOTEX_EMAIL"),
            "password": os.getenv("QUOTEX_PASSWORD"),
            "demo": True,
            "min_amount": 1.0,
            "max_amount": 100.0,
            "auto_trade": True
        }
    
    def start_bot(self, config: dict = None):
        """Start the bot"""
        global bot_instance
        
        if self.bot and self.status == "running":
            return {"status": "error", "message": "Bot is already running"}
        
        if config:
            self.config.update(config)
        
        try:
            from volcano_headless import HeadlessQuotexBot
            
            self.bot = HeadlessQuotexBot(
                email=self.config.get("email"),
                password=self.config.get("password"),
                auto_trade=self.config.get("auto_trade", True),
                min_amount=self.config.get("min_amount", 1.0),
                max_amount=self.config.get("max_amount", 100.0),
                demo=self.config.get("demo", True)
            )
            
            # Start in a separate thread
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
                "balance": 0,
                "trades": []
            }
        
        try:
            bot_status = self.bot.get_status()
            return {
                "status": self.status,
                "running": bot_status.get("running", False),
                "connected": bot_status.get("connected", False),
                "balance": bot_status.get("balance", 0),
                "win_count": bot_status.get("win_count", 0),
                "loss_count": bot_status.get("loss_count", 0),
                "win_rate": bot_status.get("win_rate", 0),
                "total_trades": bot_status.get("total_trades", 0),
                "trades": self.bot.trade_history[-10:] if self.bot.trade_history else []
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
    return render_template_string(HTML_TEMPLATE, status=status, logs=logs)


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
