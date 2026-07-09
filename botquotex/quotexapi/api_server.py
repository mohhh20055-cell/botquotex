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
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global bot instance
bot_instance = None
bot_lock = threading.Lock()


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
    """Home page"""
    return jsonify({
        "name": "Volcano Bot API",
        "version": "1.0.0",
        "status": manager.status,
        "endpoints": [
            "POST /start - Start the bot",
            "POST /stop - Stop the bot",
            "GET /status - Get bot status",
            "POST /enable - Enable trading",
            "POST /disable - Disable trading",
            "POST /signal - Execute a signal",
            "GET /health - Health check"
        ]
    })


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
