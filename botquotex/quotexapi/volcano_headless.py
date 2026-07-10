#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Volcano Profit - Headless Trading Bot (API/CLI VERSION)
يعمل بدون واجهة رسومية - مناسب لـ Render و VPS
"""

import sys
import os
import threading

# Add parent directory to sys.path so quotexapi can be found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json
import time
import asyncio
import uuid
import hashlib
import base64
import platform
import subprocess
import requests
import smtplib
import ssl
import os
import gc
import psutil
import signal
import traceback
import random
import argparse
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Any
from collections import deque
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('volcano_headless.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Libraries for Supabase
from supabase import create_client, Client
import httpx

try:
    from quotexapi.stable_api import Quotex
    HAS_QUOTEX = True
    logger.info("Quotex API imported successfully")
except ImportError as e:
    import traceback
    HAS_QUOTEX = False
    Quotex = None
    logger.error(f"Quotex API import failed: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")

# Configuration
CONFIG_FILE = "mt4_bot_config.json"
LICENSE_FILE = "bot_license.dat"
RELOGIN_INTERVAL = 1800
PAYOUT_PERCENTAGE = 0.85
CONNECTION_CHECK_INTERVAL = 2
MAX_RECONNECT_ATTEMPTS = 100
MT4_RECONNECT_INTERVAL = 30
RECONNECT_DELAY = 1
MEMORY_CLEANUP_INTERVAL = 300
MAX_HISTORY_SIZE = 100
MAX_LOG_SIZE = 500
THREAD_CLEANUP_INTERVAL = 600
QUOTEX_HEARTBEAT_INTERVAL = 15
WEBSOCKET_KEEPALIVE_INTERVAL = 10
TRADE_RETRY_ATTEMPTS = 5
TRADE_RETRY_DELAY = 3

# File Watcher Settings
SIGNAL_FILE_NAME = "SignalsLog.txt"
SIGNAL_FILE_POLLING_INTERVAL = 0.5
FILE_WATCHER_ENABLED = True

# Telegram links
TELEGRAM_DEV = "https://t.me/Mohamed_trading01"
TELEGRAM_GROUP = "https://t.me/devRobottrading"
TELEGRAM_CHANNEL = "https://t.me/Quotex_Signals_Tradings"

# Payment information
PAYMENT_WALLET = "TGG7s5ezEiVT8LPhz52Y4ExP7jeesFKKsu"
PAYMENT_NETWORK = "TRON (TRC20)"
ADMIN_EMAIL = "iry00043@gmail.com"
ADMIN_PASSWORD = "ihhv uluc pkhd rnqi"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Subscription plans
SUBSCRIPTION_PLANS = [
    {"name": "💎 Basic", "price": 5, "days": 30, "type": "basic", "features": ["1 month subscription", "Basic support"]},
    {"name": "🔥 Standard", "price": 15, "days": 60, "type": "standard", "features": ["2 months subscription", "Priority support", "All features"]},
    {"name": "👑 Premium", "price": 20, "days": 90, "type": "premium", "features": ["3 months subscription", "VIP support", "All features", "Updates included"]}
]

# Supabase settings
SUPABASE_URL = "https://iijgojnpdckzsletcfub.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlpamdvam5wZGNremxldGNmdWIiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTc2OTIzNDAwNiwiZXhwIjoyMDg0ODEwMDA2fQ.AXdgPoFW-w9ZTkqF58-19aqPopASx7DCm655gVwwP9A"


class TradingSignal:
    """Signal format for trading"""
    def __init__(self, signal_data: Dict):
        self.asset = signal_data.get('asset', 'EUR/USD')
        self.direction = signal_data.get('direction', 'call').upper()
        self.amount = signal_data.get('amount', 1.0)
        self.duration = signal_data.get('duration', 60)
        self.timestamp = datetime.now()
        
    def __str__(self):
        return f"Signal: {self.asset} {self.direction} {self.amount}$ ({self.duration}s)"


class HeadlessQuotexBot:
    """Headless Quotex Trading Bot"""
    
    def __init__(self, email: str = None, password: str = None, 
                 auto_trade: bool = True, min_amount: float = 1.0,
                 max_amount: float = 100.0, demo: bool = True):
        self.email = email or os.getenv('QUOTEX_EMAIL')
        self.password = password or os.getenv('QUOTEX_PASSWORD')
        self.auto_trade = auto_trade
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.demo = demo
        
        self.client = None
        self.connected = False
        self.trading_enabled = False
        self.signal_queue = deque(maxlen=100)
        self.trade_history = []
        self.balance = 0.0
        self.win_count = 0
        self.loss_count = 0
        
        self.running = False
        self.threads = []
        
        logger.info("="*50)
        logger.info("Volcano Headless Bot Initialized")
        logger.info(f"Auto Trade: {auto_trade}")
        logger.info(f"Demo Mode: {demo}")
        logger.info(f"Min Amount: ${min_amount}")
        logger.info(f"Max Amount: ${max_amount}")
        logger.info("="*50)
    
    def connect(self) -> bool:
        """Connect to Quotex API"""
        if not HAS_QUOTEX:
            logger.error("Quotex API not available")
            return False
            
        try:
            logger.info(f"Connecting to Quotex...")
            logger.info(f"Email: {self.email[:3]}***@{self.email.split('@')[-1] if self.email else 'N/A'}")
            
            self.client = Quotex(
                email=self.email,
                password=self.password
            )
            
            # Check connect
            check_connect = self.client.check_connect()
            if check_connect:
                self.connected = True
                logger.info("✓ Connected to Quotex successfully!")
                
                # Get balance
                self.balance = self.client.get_balance()
                logger.info(f"Balance: ${self.balance:.2f}")
                
                return True
            else:
                logger.error("✗ Failed to connect to Quotex")
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Quotex"""
        if self.client:
            try:
                self.client.close()
                logger.info("Disconnected from Quotex")
            except:
                pass
        self.connected = False
    
    def read_signals_from_file(self, filename: str = SIGNAL_FILE_NAME) -> List[TradingSignal]:
        """Read trading signals from file"""
        signals = []
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        
                        parts = line.split(',')
                        if len(parts) >= 3:
                            signal_data = {
                                'asset': parts[0].strip(),
                                'direction': parts[1].strip(),
                                'amount': float(parts[2].strip()) if len(parts) > 2 else 1.0,
                                'duration': int(parts[3].strip()) if len(parts) > 3 else 60
                            }
                            signals.append(TradingSignal(signal_data))
        except Exception as e:
            logger.error(f"Error reading signals file: {e}")
        
        return signals
    
    def execute_trade(self, signal: TradingSignal) -> Dict:
        """Execute a single trade"""
        if not self.connected or not self.client:
            return {"status": "error", "message": "Not connected"}
        
        try:
            logger.info(f"Executing trade: {signal}")
            
            direction = "call" if signal.direction.upper() == "CALL" else "put"
            amount = max(self.min_amount, min(signal.amount, self.max_amount))
            
            # Get asset price
            asset = signal.asset
            self.client.change_asset(asset)
            
            # Execute trade
            status, trade_id = self.client.buy(
                amount=amount,
                asset=asset,
                direction=direction,
                duration=signal.duration
            )
            
            if status:
                result = {
                    "status": "success",
                    "trade_id": trade_id,
                    "asset": asset,
                    "direction": direction,
                    "amount": amount,
                    "duration": signal.duration
                }
                logger.info(f"✓ Trade executed: {trade_id}")
                return result
            else:
                return {"status": "error", "message": "Trade failed"}
                
        except Exception as e:
            logger.error(f"Trade error: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_trade_result(self, trade_id: int, timeout: int = 60) -> Dict:
        """Get trade result"""
        if not self.connected or not self.client:
            return {"status": "error", "message": "Not connected"}
        
        try:
            result = self.client.check_win(trade_id)
            
            if result is not None:
                profit = result
                win = profit > 0
                
                if win:
                    self.win_count += 1
                else:
                    self.loss_count += 1
                
                self.balance = self.client.get_balance()
                
                return {
                    "status": "closed",
                    "trade_id": trade_id,
                    "profit": profit,
                    "win": win,
                    "balance": self.balance,
                    "win_rate": self.win_count / (self.win_count + self.loss_count) if (self.win_count + self.loss_count) > 0 else 0
                }
            else:
                return {"status": "pending", "trade_id": trade_id}
                
        except Exception as e:
            logger.error(f"Error getting trade result: {e}")
            return {"status": "error", "message": str(e)}
    
    def file_watcher_loop(self):
        """Watch for signals in file"""
        logger.info(f"File watcher started (watching: {SIGNAL_FILE_NAME})")
        
        processed_lines = set()
        
        while self.running:
            try:
                if not self.trading_enabled:
                    time.sleep(1)
                    continue
                
                if os.path.exists(SIGNAL_FILE_NAME):
                    with open(SIGNAL_FILE_NAME, 'r') as f:
                        lines = f.readlines()
                        
                        for i, line in enumerate(lines):
                            if i in processed_lines:
                                continue
                            
                            line = line.strip()
                            if not line or line.startswith('#'):
                                continue
                            
                            parts = line.split(',')
                            if len(parts) >= 3:
                                signal_data = {
                                    'asset': parts[0].strip(),
                                    'direction': parts[1].strip(),
                                    'amount': float(parts[2].strip()) if len(parts) > 2 else 1.0,
                                    'duration': int(parts[3].strip()) if len(parts) > 3 else 60
                                }
                                signal = TradingSignal(signal_data)
                                logger.info(f"New signal received: {signal}")
                                
                                result = self.execute_trade(signal)
                                if result['status'] == 'success':
                                    self.trade_history.append(result)
                                
                                processed_lines.add(i)
                
                time.sleep(SIGNAL_FILE_POLLING_INTERVAL)
                
            except Exception as e:
                logger.error(f"File watcher error: {e}")
                time.sleep(1)
    
    def status_loop(self):
        """Report status periodically"""
        while self.running:
            try:
                if self.connected and self.client:
                    self.balance = self.client.get_balance()
                    
                logger.info("-"*40)
                logger.info(f"Status Report")
                logger.info(f"Connected: {self.connected}")
                logger.info(f"Trading Enabled: {self.trading_enabled}")
                logger.info(f"Balance: ${self.balance:.2f}")
                logger.info(f"Win/Loss: {self.win_count}/{self.loss_count}")
                if (self.win_count + self.loss_count) > 0:
                    win_rate = self.win_count / (self.win_count + self.loss_count) * 100
                    logger.info(f"Win Rate: {win_rate:.1f}%")
                logger.info(f"Total Trades: {len(self.trade_history)}")
                logger.info("-"*40)
                
            except Exception as e:
                logger.error(f"Status error: {e}")
            
            time.sleep(30)
    
    def memory_cleanup_loop(self):
        """Cleanup memory periodically"""
        while self.running:
            time.sleep(MEMORY_CLEANUP_INTERVAL)
            try:
                gc.collect()
                process = psutil.Process()
                mem_info = process.memory_info()
                logger.debug(f"Memory: {mem_info.rss / 1024 / 1024:.1f} MB")
            except:
                pass
    
    def start(self):
        """Start the bot"""
        if self.running:
            logger.warning("Bot is already running")
            return
        
        self.running = True
        
        # Connect
        if not self.connect():
            logger.error("Failed to connect, exiting...")
            return
        
        # Start threads
        self.trading_enabled = True
        
        threads = [
            threading.Thread(target=self.file_watcher_loop, daemon=True, name="FileWatcher"),
            threading.Thread(target=self.status_loop, daemon=True, name="StatusReporter"),
            threading.Thread(target=self.memory_cleanup_loop, daemon=True, name="MemoryCleanup")
        ]
        
        for t in threads:
            t.start()
            self.threads.append(t)
        
        logger.info("Bot started successfully!")
        logger.info("Press Ctrl+C to stop")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.stop()
    
    def stop(self):
        """Stop the bot"""
        self.running = False
        self.trading_enabled = False
        
        # Wait for threads
        for t in self.threads:
            t.join(timeout=2)
        
        self.disconnect()
        logger.info("Bot stopped")
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            "running": self.running,
            "connected": self.connected,
            "trading_enabled": self.trading_enabled,
            "balance": self.balance,
            "win_count": self.win_count,
            "loss_count": self.loss_count,
            "win_rate": self.win_count / (self.win_count + self.loss_count) if (self.win_count + self.loss_count) > 0 else 0,
            "total_trades": len(self.trade_history)
        }
    
    def enable_trading(self):
        """Enable trading"""
        self.trading_enabled = True
        logger.info("Trading enabled")
    
    def disable_trading(self):
        """Disable trading"""
        self.trading_enabled = False
        logger.info("Trading disabled")


def create_sample_signal_file():
    """Create a sample signals file"""
    sample_content = """# Volcano Bot Signals File
# Format: ASSET,DIRECTION,AMOUNT,DURATION
# DIRECTION: CALL (up) or PUT (down)
# AMOUNT: Investment amount in USD
# DURATION: Trade duration in seconds

EUR/USD,CALL,1.0,60
GBP/JPY,PUT,2.0,60
AUD/USD,CALL,1.5,120
"""
    
    with open(SIGNAL_FILE_NAME, 'w') as f:
        f.write(sample_content)
    
    print(f"Created sample signals file: {SIGNAL_FILE_NAME}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Volcano Headless Trading Bot - يعمل بدون واجهة رسومية",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
أمثلة:
  python volcano_headless.py --email "test@test.com" --password "pass123"
  python volcano_headless.py --email "test@test.com" --password "pass123" --no-auto-trade
  python volcano_headless.py --create-sample
  python volcano_headless.py --status

المتغيرات البيئية:
  QUOTEX_EMAIL - بريد Quotex
  QUOTEX_PASSWORD - كلمة مرور Quotex
        """
    )
    
    parser.add_argument('--email', '-e', help='Quotex email')
    parser.add_argument('--password', '-p', help='Quotex password')
    parser.add_argument('--demo', action='store_true', default=True, help='Use demo account')
    parser.add_argument('--min-amount', type=float, default=1.0, help='Minimum trade amount')
    parser.add_argument('--max-amount', type=float, default=100.0, help='Maximum trade amount')
    parser.add_argument('--no-auto-trade', action='store_true', help='Disable auto trading')
    parser.add_argument('--create-sample', action='store_true', help='Create sample signals file')
    parser.add_argument('--status', action='store_true', help='Check bot status')
    
    args = parser.parse_args()
    
    if args.create_sample:
        create_sample_signal_file()
        return
    
    if not args.email or not args.password:
        logger.error("Email and password are required!")
        logger.info("Use --email and --password or set QUOTEX_EMAIL and QUOTEX_PASSWORD")
        parser.print_help()
        sys.exit(1)
    
    auto_trade = not args.no_auto_trade
    
    bot = HeadlessQuotexBot(
        email=args.email,
        password=args.password,
        auto_trade=auto_trade,
        min_amount=args.min_amount,
        max_amount=args.max_amount,
        demo=args.demo
    )
    
    try:
        bot.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        bot.stop()


if __name__ == "__main__":
    main()
