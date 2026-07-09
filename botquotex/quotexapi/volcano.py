#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Volcano Profit - Advanced Trading Bot (FILE BASED VERSION)
الإصدار: 9.0 - يعمل عن طريق قراءة الإشارات من ملف بدلاً من Socket
"""

import sys
import threading
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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Any
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QObject, QPropertyAnimation, QEasingCurve, QDate, QUrl, QMutex, QMutexLocker, QCoreApplication, QEventLoop
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QBrush, QPainter, QDesktopServices, QPixmap
from PyQt5.QtMultimedia import QSound, QSoundEffect
from PyQt5.QtCore import QUrl as QtUrl

# Libraries for Supabase
from supabase import create_client, Client
import httpx

try:
    from quotexapi.stable_api import Quotex
    HAS_QUOTEX = True
except ImportError:
    HAS_QUOTEX = False
    Quotex = None

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

# Language strings
LANGUAGES = {
    'en': {
        'app_title': '🌋 Volcano Profit - Advanced Trading Bot (FILE MODE)',
        'connected': '✅ Connected',
        'disconnected': '❌ Disconnected',
        'connecting': '🔄 Connecting...',
        'connect': '🔌 Connect',
        'balance': '💰 Balance:',
        'email': '📧 Email:',
        'password': '🔑 Password:',
        'account': '📊 Account:',
        'practice': 'PRACTICE',
        'real': 'REAL',
        'assets': '📈 Assets',
        'refresh': '🔄 Refresh',
        'auto_trade': '🤖 Auto trade from File',
        'call': '📈 CALL',
        'put': '📉 PUT',
        'martingale': '🎲 Martingale',
        'martingale_status': 'Status:',
        'martingale_type': 'Type:',
        'martingale_pending': 'Pending:',
        'enabled': 'Enabled',
        'disabled': 'Disabled',
        'log': '📋 LIVE LOG',
        'active_trades': '⚡ ACTIVE TRADES',
        'not_executed': '⚠️ NOT EXECUTED',
        'history': '📜 HISTORY',
        'stats': '📊 STATISTICS',
        'payment': '💳 PAYMENT',
        'settings': '⚙️ SETTINGS',
        'no_active_trades': 'No active trades',
        'no_connection': '⚠️ Not connected to Quotex',
        'auto_trade_disabled': 'ℹ️ Auto trade disabled - Signal ignored',
        'license_required': '⚠️ LICENSE REQUIRED - REAL account needs license',
        'license_expired': '⚠️ LICENSE EXPIRED - Please renew license',
        'license_activated': '✅ License activated successfully',
        'license_not_activated': '⚠️ License not activated - Some features are locked',
        'sound_on': '🔊 Sound On',
        'sound_off': '🔇 Sound Off',
        'buy_subscription': '💳 Buy Subscription',
        'activate_license': '🔐 Activate License',
        'total_trades': 'Total Trades:',
        'wins': 'Wins:',
        'losses': 'Losses:',
        'break_even': 'Break Even:',
        'win_rate': 'Win Rate:',
        'total_pl': 'Total P/L:',
        'net_profit': 'Net Profit:',
        'avg_win': 'Avg Win:',
        'avg_loss': 'Avg Loss:',
        'not_executed_count': 'Not Executed:',
        'martingale_trades': 'Martingale Trades:',
        'martingale_wins': 'M-Wins:',
        'risk_status': 'Risk Status:',
        'risk_active': '✅ Active',
        'risk_sl_triggered': '⛔ STOP LOSS TRIGGERED',
        'risk_tp_triggered': '🎯 TAKE PROFIT TRIGGERED',
        'reset_risk': '🔄 Reset Risk & Resume Trading',
        'refresh_stats': 'Refresh Statistics',
        'clear_history': 'Clear History',
        'clear_not_executed': 'Clear List',
        'save_settings': 'Save Settings',
        'language': '🌐 Language:',
        'memory_cleanup': '🧹 Memory Cleanup',
        'thread_cleanup': '🔄 Thread Cleanup',
        'bot_frozen': '⚠️ Bot frozen - Auto-restarting...',
        'switch_account': '🔄 Switch Account',
        'asset_closed': '⚠️ {asset} is CLOSED - Trade rejected',
        'mt4_reconnect': '🔄 Reconnecting to MT4 server...',
        'mt4_reconnected': '✅ MT4 Server reconnected successfully',
        'connection_lost': '⚠️ Connection to Quotex lost! Auto-reconnecting...',
        'connection_restored': '✅ Connection to Quotex restored!',
        'reconnecting': '🔄 Reconnecting to Quotex... (Attempt {attempt}/{max})',
        'reconnect_success': '✅ Successfully reconnected to Quotex!',
        'reconnect_failed': '❌ Failed to reconnect after {attempts} attempts',
        'switching_account': '🔄 Switching account to {email}...',
        'disconnecting': '🔄 Disconnecting from current account...',
        'retrying_trade': '🔄 Retrying trade for {symbol}... (Attempt {attempt}/{max})',
        'trade_retry_success': '✅ Trade retry successful for {symbol}!',
        'trade_retry_failed': '❌ All retry attempts failed for {symbol}',
        'file_watcher_started': '📁 File watcher started - Monitoring {path} for signals',
        'signal_received': '📨 Signal received from file: {symbol} {direction} ${amount}',
        'no_signal_file': '⚠️ Signal file not found: {path}'
    },
    'ar': {
        'app_title': '🌋 فولكانو بروفيت - بوت تداول متقدم (نسخة الملفات)',
        'connected': '✅ متصل',
        'disconnected': '❌ غير متصل',
        'connecting': '🔄 جاري الاتصال...',
        'connect': '🔌 اتصال',
        'balance': '💰 الرصيد:',
        'email': '📧 البريد الإلكتروني:',
        'password': '🔑 كلمة المرور:',
        'account': '📊 الحساب:',
        'practice': 'تجريبي',
        'real': 'حقيقي',
        'assets': '📈 الأصول',
        'refresh': '🔄 تحديث',
        'auto_trade': '🤖 تداول تلقائي من الملف',
        'call': '📈 شراء',
        'put': '📉 بيع',
        'martingale': '🎲 مارتينجال',
        'martingale_status': 'الحالة:',
        'martingale_type': 'النوع:',
        'martingale_pending': 'معلق:',
        'enabled': 'مفعل',
        'disabled': 'معطل',
        'log': '📋 سجل الأحداث',
        'active_trades': '⚡ الصفقات النشطة',
        'not_executed': '⚠️ الصفقات غير المنفذة',
        'history': '📜 السجل',
        'stats': '📊 الإحصائيات',
        'payment': '💳 الدفع',
        'settings': '⚙️ الإعدادات',
        'no_active_trades': 'لا توجد صفقات نشطة',
        'no_connection': '⚠️ غير متصل بـ Quotex',
        'auto_trade_disabled': 'ℹ️ التداول التلقائي معطل - تم تجاهل الإشارة',
        'license_required': '⚠️ الترخيص مطلوب - الحساب الحقيقي يحتاج ترخيص',
        'license_expired': '⚠️ انتهى الترخيص - يرجى تجديد الترخيص',
        'license_activated': '✅ تم تفعيل الترخيص بنجاح',
        'license_not_activated': '⚠️ الترخيص غير مفعل - بعض الميزات مقفلة',
        'sound_on': '🔊 الصوت مفعل',
        'sound_off': '🔇 الصوت معطل',
        'buy_subscription': '💳 شراء اشتراك',
        'activate_license': '🔐 تفعيل الترخيص',
        'total_trades': 'إجمالي الصفقات:',
        'wins': 'الربح:',
        'losses': 'الخسارة:',
        'break_even': 'تعادل:',
        'win_rate': 'نسبة الربح:',
        'total_pl': 'إجمالي الربح/الخسارة:',
        'net_profit': 'صافي الربح:',
        'avg_win': 'متوسط الربح:',
        'avg_loss': 'متوسط الخسارة:',
        'not_executed_count': 'غير منفذ:',
        'martingale_trades': 'صفقات المارتينجال:',
        'martingale_wins': 'ربح المارتينجال:',
        'risk_status': 'حالة المخاطرة:',
        'risk_active': '✅ نشط',
        'risk_sl_triggered': '⛔ تم تفعيل وقف الخسارة',
        'risk_tp_triggered': '🎯 تم تفعيل جني الأرباح',
        'reset_risk': '🔄 إعادة ضبط المخاطرة واستئناف التداول',
        'refresh_stats': 'تحديث الإحصائيات',
        'clear_history': 'مسح السجل',
        'clear_not_executed': 'مسح القائمة',
        'save_settings': 'حفظ الإعدادات',
        'language': '🌐 اللغة:',
        'memory_cleanup': '🧹 تنظيف الذاكرة',
        'thread_cleanup': '🔄 تنظيف الخيوط',
        'bot_frozen': '⚠️ البوت متجمد - جاري إعادة التشغيل التلقائي...',
        'switch_account': '🔄 تبديل الحساب',
        'asset_closed': '⚠️ {asset} مغلق - تم رفض الصفقة',
        'mt4_reconnect': '🔄 جاري إعادة الاتصال بسيرفر MT4...',
        'mt4_reconnected': '✅ تم إعادة الاتصال بسيرفر MT4 بنجاح',
        'connection_lost': '⚠️ فقد الاتصال بـ Quotex! جاري إعادة الاتصال...',
        'connection_restored': '✅ تم استعادة الاتصال بـ Quotex!',
        'reconnecting': '🔄 جاري إعادة الاتصال بـ Quotex... (محاولة {attempt}/{max})',
        'reconnect_success': '✅ تم إعادة الاتصال بـ Quotex بنجاح!',
        'reconnect_failed': '❌ فشلت إعادة الاتصال بعد {attempts} محاولات',
        'switching_account': '🔄 جاري تبديل الحساب إلى {email}...',
        'disconnecting': '🔄 جاري قطع الاتصال بالحساب الحالي...',
        'retrying_trade': '🔄 جاري إعادة محاولة الصفقة لـ {symbol}... (محاولة {attempt}/{max})',
        'trade_retry_success': '✅ نجحت إعادة محاولة الصفقة لـ {symbol}!',
        'trade_retry_failed': '❌ فشلت جميع محاولات إعادة الصفقة لـ {symbol}',
        'file_watcher_started': '📁 تم تشغيل مراقب الملفات - جاري مراقبة {path} للإشارات',
        'signal_received': '📨 تم استلام إشارة من الملف: {symbol} {direction} ${amount}',
        'no_signal_file': '⚠️ ملف الإشارات غير موجود: {path}'
    }
}

# Martingale types
class MartingaleType(Enum):
    DISABLED = "disabled"
    NEXT_OPPORTUNITY_SAME = "next_opportunity_same"
    NEXT_OPPORTUNITY_ANY = "next_opportunity_any"

class TradeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_CANDLE_CLOSE = "waiting_candle"
    CHECKING_RESULT = "checking_result"
    COMPLETED = "completed"
    ERROR = "error"
    NOT_EXECUTED = "not_executed"
    RETRYING = "retrying"

class TradeResult(Enum):
    WIN = "win"
    LOSS = "loss"
    BREAK_EVEN = "break_even"

@dataclass
class MartingaleInfo:
    enabled: bool = False
    martingale_type: MartingaleType = MartingaleType.DISABLED
    max_steps: int = 5
    current_step: int = 0
    base_amount: float = 0
    original_symbol: str = ""
    loss_occurred_at: datetime = None
    pending_double: bool = False
    
    def calculate_next_amount(self) -> float:
        return self.base_amount * (2 ** self.current_step)

@dataclass
class TradeInfo:
    trade_id: str
    internal_id: str
    symbol: str
    direction: str
    amount: float
    duration_minutes: int
    entry_time: datetime
    requested_duration_seconds: int
    candle_remaining_seconds: float
    actual_wait_seconds: float
    candle_close_time: datetime
    wait_type: str
    status: TradeStatus = TradeStatus.PENDING
    balance_before: float = 0.0
    balance_after: float = 0.0
    profit: float = 0.0
    win: bool = False
    result_type: str = "loss"
    api_trade_id: any = None
    api_trade_id_int: any = None
    completion_time: datetime = None
    error_message: str = ""
    result_check_attempts: int = 0
    martingale_info: MartingaleInfo = None
    parent_trade_id: str = ""
    child_trade_id: str = ""
    signal_source: str = "FILE"
    retry_count: int = 0
    
    def to_dict(self) -> dict:
        return {
            'internal_id': self.internal_id,
            'trade_id': self.trade_id,
            'symbol': self.symbol,
            'direction': self.direction,
            'amount': self.amount,
            'duration_minutes': self.duration_minutes,
            'entry_time': self.entry_time.strftime("%H:%M:%S"),
            'candle_remaining_seconds': self.candle_remaining_seconds,
            'actual_wait_seconds': self.actual_wait_seconds,
            'wait_type': self.wait_type,
            'candle_close_time': self.candle_close_time.strftime("%H:%M:%S") if self.candle_close_time else "",
            'completion_time': self.completion_time.strftime("%H:%M:%S") if self.completion_time else "",
            'status': self.status.value,
            'win': self.win,
            'result_type': self.result_type,
            'profit': self.profit,
            'balance_before': self.balance_before,
            'balance_after': self.balance_after,
            'error_message': self.error_message,
            'result_check_attempts': self.result_check_attempts,
            'martingale_step': self.martingale_info.current_step if self.martingale_info else 0,
            'parent_trade': self.parent_trade_id[:8] if self.parent_trade_id else "",
            'signal_source': self.signal_source,
            'retry_count': self.retry_count
        }

class MemoryManager:
    def __init__(self):
        self.last_cleanup = time.time()
        self.cleanup_interval = MEMORY_CLEANUP_INTERVAL
        self.max_log_size = MAX_LOG_SIZE
        self.max_history_size = MAX_HISTORY_SIZE
        
    def cleanup(self):
        try:
            gc.collect()
            if hasattr(gc, 'garbage'):
                gc.garbage.clear()
            try:
                process = psutil.Process()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                if memory_mb > 500:
                    print(f"⚠️ High memory usage: {memory_mb:.1f} MB")
            except:
                pass
            self.last_cleanup = time.time()
            return True
        except Exception as e:
            print(f"Memory cleanup error: {e}")
            return False
    
    def should_cleanup(self):
        return (time.time() - self.last_cleanup) >= self.cleanup_interval

class ThreadManager:
    def __init__(self):
        self.active_threads = []
        self.thread_lock = threading.Lock()
        self.last_cleanup = time.time()
        
    def add_thread(self, thread):
        with self.thread_lock:
            self.active_threads.append(thread)
            self._cleanup_finished_threads()
    
    def _cleanup_finished_threads(self):
        with self.thread_lock:
            self.active_threads = [t for t in self.active_threads if t.is_alive()]
    
    def cleanup(self):
        with self.thread_lock:
            self._cleanup_finished_threads()
            for thread in self.active_threads:
                if hasattr(thread, 'start_time') and thread.is_alive():
                    runtime = time.time() - thread.start_time
                    if runtime > 3600:
                        print(f"⚠️ Thread {thread.name} running for {runtime:.0f}s - potential leak")
        self.last_cleanup = time.time()
    
    def should_cleanup(self):
        return (time.time() - self.last_cleanup) >= THREAD_CLEANUP_INTERVAL

class EmailSender:
    def __init__(self, smtp_server=SMTP_SERVER, smtp_port=SMTP_PORT, 
                 sender_email=ADMIN_EMAIL, sender_password=ADMIN_PASSWORD):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
    
    def send_payment_notification(self, to_email: str, plan_name: str, amount: float, 
                                  txid: str, image_path: str = None, 
                                  user_email: str = None, days: int = 30) -> bool:
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = f"💰 New Payment Request - {plan_name}"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #FF9800; text-align: center;">💰 New Payment Request</h2>
                    <div style="background-color: #FFF3E0; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p><strong>📋 Plan:</strong> {plan_name}</p>
                        <p><strong>💰 Amount:</strong> ${amount}</p>
                        <p><strong>📧 User Email:</strong> {user_email}</p>
                        <p><strong>🔗 TXID:</strong> {txid}</p>
                        <p><strong>📅 Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p><strong>💳 Wallet:</strong> {PAYMENT_WALLET}</p>
                    </div>
                    <p style="color: #666666;">Please verify the payment and send the license key to the user's email.</p>
                    <hr style="border: 1px solid #FFE0B2;">
                    <p style="font-size: 12px; color: #999999; text-align: center;">
                        Volcano Profit - Automated Payment System
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    filename = os.path.basename(image_path)
                    part.add_header('Content-Disposition', f'attachment; filename= {filename}')
                    msg.attach(part)
            
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Email sending error: {e}")
            return False
    
    def send_license_key_email(self, to_email: str, license_key: str, 
                              plan_name: str, expiry_date: str) -> bool:
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = f"🔑 Your License Key - {plan_name}"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #FF9800; text-align: center;">🔑 Your License Key</h2>
                    <div style="background-color: #FFF3E0; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p><strong>📋 Plan:</strong> {plan_name}</p>
                        <p><strong>📅 Expiry:</strong> {expiry_date}</p>
                        <p><strong>🔐 License Key:</strong></p>
                        <div style="background-color: #333; color: #FF9800; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 18px; text-align: center;">
                            {license_key}
                        </div>
                    </div>
                    <p style="color: #666666;">To activate your license:</p>
                    <ol style="color: #666666;">
                        <li>Open the Volcano Profit</li>
                        <li>Click on "Activate License"</li>
                        <li>Enter your license key</li>
                        <li>Start trading!</li>
                    </ol>
                    <p style="color: #FF9800;"><strong>⚠️ Important:</strong> This key is one-time use.</p>
                    <hr style="border: 1px solid #FFE0B2;">
                    <p style="font-size: 12px; color: #999999; text-align: center;">
                        Volcano Profit - License Delivery System
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"License email error: {e}")
            return False

class SupabaseLicenseManager:
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.activated_key = None
        self.expiration_date = None
        self.is_valid = False
        self.hwid = self.get_hardware_id()
        self.server_time_diff = 0
        self.connected = False
        self.remaining_seconds = 0
        self.plan_type = "basic"
        self.user_email = ""
        self.email_sender = EmailSender()
        self.offline_mode = False
        self.last_check_time = None
        self.check_interval = 60
        
        self._disable_ssl_verification()
        self.connect_to_supabase()
        self.sync_server_time()
        self.load_saved_license()
        self.check_current_license()
    
    def _disable_ssl_verification(self):
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
            self.http_client = httpx.Client(verify=False)
        except:
            pass
    
    def connect_to_supabase(self):
        try:
            self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            test = self.supabase.table("licenses").select("*").limit(1).execute()
            self.connected = True
            print("✅ Connected to Supabase")
        except Exception as e:
            print(f"⚠️ Supabase connection failed: {e}")
            self.connected = False
            self.offline_mode = True
    
    def sync_server_time(self):
        try:
            response = requests.get("https://worldtimeapi.org/api/timezone/Etc/UTC", timeout=5, verify=False)
            if response.status_code == 200:
                server_time_str = response.json()['datetime']
                server_time = datetime.fromisoformat(server_time_str.replace('Z', '+00:00')).replace(tzinfo=None)
                local_time = datetime.now()
                self.server_time_diff = (server_time - local_time).total_seconds()
        except:
            self.server_time_diff = 0
    
    def get_server_time(self) -> datetime:
        return datetime.now() + timedelta(seconds=self.server_time_diff)
    
    def get_hardware_id(self) -> str:
        identifiers = []
        
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output('wmic cpu get processorid', shell=True).decode()
                processor_id = output.strip().split('\n')[1].strip()
                identifiers.append(processor_id)
        except:
            pass
        
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output('wmic diskdrive get serialnumber', shell=True).decode()
                lines = output.strip().split('\n')
                if len(lines) > 1:
                    disk_serial = lines[1].strip()
                    identifiers.append(disk_serial)
        except:
            pass
        
        try:
            identifiers.append(str(uuid.getnode()))
        except:
            pass
        
        try:
            identifiers.append(platform.node())
        except:
            pass
        
        try:
            if platform.system() == "Windows":
                import winreg
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Cryptography")
                    machine_guid = winreg.QueryValueEx(key, "MachineGuid")[0]
                    identifiers.append(machine_guid)
                except:
                    pass
        except:
            pass
        
        combined = ''.join(identifiers)
        if not combined:
            combined = str(uuid.uuid4())
        
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def get_ip_address(self) -> str:
        try:
            response = requests.get("https://api.ipify.org", timeout=3, verify=False)
            return response.text
        except:
            return "Unknown"
    
    def generate_license_key(self) -> str:
        import random
        import string
        
        def generate_segment(length=4):
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        
        return f"BEAST-{generate_segment()}-{generate_segment()}-{generate_segment()}"
    
    def create_license(self, email: str, days: int = 30, plan_type: str = "basic", notes: str = "") -> str:
        if not self.connected or not self.supabase:
            print("Supabase not connected")
            return ""
        
        license_key = self.generate_license_key()
        expiry_date = (self.get_server_time() + timedelta(days=days)).isoformat()
        created_at = self.get_server_time().isoformat()
        
        try:
            data = {
                "email": email,
                "license_key": license_key,
                "created_at": created_at,
                "expiry_date": expiry_date,
                "is_active": True,
                "plan_type": plan_type,
                "notes": notes,
                "payment_status": "pending",
                "payment_txid": notes
            }
            
            result = self.supabase.table("licenses").insert(data).execute()
            
            if result.data and len(result.data) > 0:
                print(f"✅ License created: {license_key}")
                plan_name = next((p["name"] for p in SUBSCRIPTION_PLANS if p["type"] == plan_type), plan_type)
                self.email_sender.send_license_key_email(email, license_key, plan_name, expiry_date)
                return license_key
            else:
                print("❌ Failed to create license - no data returned")
                return ""
        except Exception as e:
            print(f"Error creating license: {e}")
            return ""
    
    def process_payment_request(self, email: str, plan_name: str, amount: float, 
                               txid: str, image_path: str = None) -> bool:
        try:
            success = self.email_sender.send_payment_notification(
                to_email=ADMIN_EMAIL,
                plan_name=plan_name,
                amount=amount,
                txid=txid,
                image_path=image_path,
                user_email=email
            )
            
            if success:
                print(f"✅ Payment request sent to admin for {email}")
                if self.connected and self.supabase:
                    payment_data = {
                        "email": email,
                        "plan_name": plan_name,
                        "amount": amount,
                        "txid": txid,
                        "status": "pending",
                        "created_at": self.get_server_time().isoformat()
                    }
                    self.supabase.table("payment_requests").insert(payment_data).execute()
                return True
            else:
                print("❌ Failed to send payment email")
                return False
        except Exception as e:
            print(f"Error processing payment: {e}")
            return False
    
    def save_license_to_file(self, key: str, expiration: datetime, plan_type: str = "basic", email: str = ""):
        try:
            data = {
                "key": key,
                "expiration": expiration.isoformat(),
                "hwid": self.hwid,
                "activated": datetime.now().isoformat(),
                "plan_type": plan_type,
                "email": email
            }
            json_str = json.dumps(data)
            encoded = base64.b64encode(json_str.encode()).decode()
            with open(LICENSE_FILE, 'w') as f:
                f.write(encoded)
            print(f"✅ License saved to {LICENSE_FILE}")
        except Exception as e:
            print(f"Error saving license: {e}")
    
    def load_saved_license(self):
        try:
            if os.path.exists(LICENSE_FILE):
                with open(LICENSE_FILE, 'r') as f:
                    encoded = f.read().strip()
                missing_padding = len(encoded) % 4
                if missing_padding:
                    encoded += '=' * (4 - missing_padding)
                json_str = base64.b64decode(encoded).decode()
                data = json.loads(json_str)
                self.activated_key = data.get("key")
                try:
                    self.expiration_date = datetime.fromisoformat(data.get("expiration"))
                    self.plan_type = data.get("plan_type", "basic")
                    self.user_email = data.get("email", "")
                    now = datetime.now()
                    if self.expiration_date > now:
                        self.is_valid = True
                        self.remaining_seconds = int((self.expiration_date - now).total_seconds())
                        print(f"✅ Loaded valid license from file, expires in {self.remaining_seconds // 86400} days")
                    else:
                        print("❌ Saved license has expired")
                        self.is_valid = False
                        self.remaining_seconds = 0
                except Exception as e:
                    print(f"Error parsing saved license: {e}")
        except Exception as e:
            print(f"Error loading license file: {e}")
    
    def activate_key(self, key: str) -> bool:
        if not self.connected or not self.supabase:
            return self.offline_activate(key)
        
        try:
            result = self.supabase.table("licenses")\
                .select("*")\
                .eq("license_key", key)\
                .execute()
            
            if not result.data or len(result.data) == 0:
                print("❌ License key not found")
                return False
            
            license_data = result.data[0]
            
            if not license_data.get('is_active', False):
                print(f"❌ License is deactivated")
                return False
            
            expiry_date_str = license_data['expiry_date']
            if 'Z' in expiry_date_str:
                expiry_date_str = expiry_date_str.replace('Z', '+00:00')
            expiry_date = datetime.fromisoformat(expiry_date_str).replace(tzinfo=None)
            server_time = self.get_server_time()
            
            if expiry_date < server_time:
                print("❌ License has expired")
                self.supabase.table("licenses")\
                    .update({"is_active": False})\
                    .eq("license_key", key)\
                    .execute()
                return False
            
            update_data = {
                "last_used": self.get_server_time().isoformat(),
                "payment_status": "completed"
            }
            
            self.supabase.table("licenses")\
                .update(update_data)\
                .eq("license_key", key)\
                .execute()
            
            self._log_activity(key, "license_validation", {
                "machine_id": self.hwid,
                "ip": self.get_ip_address(),
                "action": "activate"
            })
            
            self.save_license_to_file(key, expiry_date, license_data.get('plan_type', 'basic'), license_data.get('email', ''))
            
            self.activated_key = key
            self.expiration_date = expiry_date
            self.is_valid = True
            self.remaining_seconds = int((expiry_date - server_time).total_seconds())
            self.plan_type = license_data.get('plan_type', 'basic')
            self.user_email = license_data.get('email', '')
            
            print(f"✅ License activated successfully and saved to file")
            return True
        except Exception as e:
            print(f"Activation error: {e}")
            return self.offline_activate(key)
    
    def offline_activate(self, key: str) -> bool:
        print("🔄 Using offline activation mode")
        import re
        if not re.match(r'^[A-Z0-9]{5}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$', key):
            print("❌ Invalid license key format")
            return False
        
        expiry_date = datetime.now() + timedelta(days=30)
        self.save_license_to_file(key, expiry_date, "basic", "offline@user.com")
        self.activated_key = key
        self.expiration_date = expiry_date
        self.is_valid = True
        self.remaining_seconds = int((expiry_date - datetime.now()).total_seconds())
        self.plan_type = "basic"
        self.user_email = "offline@user.com"
        print("✅ Offline activation successful (30 days)")
        return True
    
    def _log_activity(self, key: str, activity_type: str, details: dict):
        try:
            result = self.supabase.table("licenses")\
                .select("id")\
                .eq("license_key", key)\
                .execute()
            
            if result.data and len(result.data) > 0:
                license_id = result.data[0]['id']
                activity_data = {
                    "license_id": license_id,
                    "activity_type": activity_type,
                    "details": details,
                    "ip_address": details.get('ip', self.get_ip_address()),
                    "user_agent": f"HWID: {self.hwid}"
                }
                self.supabase.table("license_activity").insert(activity_data).execute()
        except Exception as e:
            print(f"Error logging activity: {e}")
    
    def check_current_license(self):
        now = datetime.now()
        if self.last_check_time and (now - self.last_check_time).total_seconds() < self.check_interval:
            return
        
        self.last_check_time = now
        
        if not self.activated_key:
            return
        
        if self.expiration_date:
            now = datetime.now()
            if self.expiration_date > now:
                self.remaining_seconds = int((self.expiration_date - now).total_seconds())
                self.is_valid = True
            else:
                self.is_valid = False
                self.remaining_seconds = 0
        
        if self.connected and self.supabase and self.activated_key:
            try:
                result = self.supabase.table("licenses")\
                    .select("*")\
                    .eq("license_key", self.activated_key)\
                    .execute()
                
                if result.data and len(result.data) > 0:
                    license_data = result.data[0]
                    
                    if not license_data.get('is_active', False):
                        print("❌ License is deactivated in server")
                        self.is_valid = False
                        self.remaining_seconds = 0
                        return
                    
                    expiry_date_str = license_data['expiry_date']
                    if 'Z' in expiry_date_str:
                        expiry_date_str = expiry_date_str.replace('Z', '+00:00')
                    expiry_date = datetime.fromisoformat(expiry_date_str).replace(tzinfo=None)
                    server_time = self.get_server_time()
                    
                    if expiry_date < server_time:
                        print("❌ License expired in server")
                        self.is_valid = False
                        self.remaining_seconds = 0
                        if os.path.exists(LICENSE_FILE):
                            os.remove(LICENSE_FILE)
                        return
                    
                    if not self.expiration_date or expiry_date > self.expiration_date:
                        self.expiration_date = expiry_date
                        self.plan_type = license_data.get('plan_type', self.plan_type)
                        self.user_email = license_data.get('email', self.user_email)
                        self.remaining_seconds = int((expiry_date - server_time).total_seconds())
                        self.is_valid = True
                        self.save_license_to_file(self.activated_key, expiry_date, self.plan_type, self.user_email)
            except Exception as e:
                print(f"License sync error: {e}")
    
    def deactivate_key(self, key: str) -> bool:
        if not self.connected or not self.supabase:
            return False
        
        try:
            self.supabase.table("licenses")\
                .update({"is_active": False})\
                .eq("license_key", key)\
                .execute()
            if os.path.exists(LICENSE_FILE):
                os.remove(LICENSE_FILE)
            self.activated_key = None
            self.is_valid = False
            self.remaining_seconds = 0
            return True
        except:
            return False
    
    def get_all_keys(self) -> List[dict]:
        if not self.connected or not self.supabase:
            return []
        
        try:
            result = self.supabase.table("licenses")\
                .select("*")\
                .order("created_at", desc=True)\
                .execute()
            
            if result.data:
                for item in result.data:
                    if 'expiry_date' in item and item['expiry_date']:
                        item['expiry_date'] = item['expiry_date'].replace('Z', '+00:00')
                    if 'created_at' in item and item['created_at']:
                        item['created_at'] = item['created_at'].replace('Z', '+00:00')
                    if 'last_used' in item and item['last_used']:
                        item['last_used'] = item['last_used'].replace('Z', '+00:00')
                return result.data
            return []
        except Exception as e:
            print(f"Error getting keys: {e}")
            return []
    
    def get_remaining_days(self) -> int:
        if self.expiration_date and self.is_valid:
            server_time = self.get_server_time()
            if hasattr(self.expiration_date, 'tzinfo') and self.expiration_date.tzinfo is not None:
                self.expiration_date = self.expiration_date.replace(tzinfo=None)
            remaining = (self.expiration_date - server_time).days
            return max(0, remaining)
        return 0
    
    def delete_key(self, key: str) -> bool:
        if not self.connected or not self.supabase:
            return False
        
        try:
            self.supabase.table("licenses")\
                .delete()\
                .eq("license_key", key)\
                .execute()
            return True
        except:
            return False
    
    def reactivate_key(self, key: str) -> bool:
        if not self.connected or not self.supabase:
            return False
        
        try:
            self.supabase.table("licenses")\
                .update({"is_active": True})\
                .eq("license_key", key)\
                .execute()
            return True
        except:
            return False

class AsyncHelper:
    _loops = {}
    
    @classmethod
    def run_async(cls, coro, timeout=10):
        if coro is None:
            return None
        thread_id = threading.get_ident()
        try:
            try:
                loop = asyncio.get_running_loop()
                future = asyncio.run_coroutine_threadsafe(coro, loop)
                return future.result(timeout=timeout)
            except RuntimeError:
                if thread_id not in cls._loops or cls._loops[thread_id].is_closed():
                    cls._loops[thread_id] = asyncio.new_event_loop()
                    asyncio.set_event_loop(cls._loops[thread_id])
                return cls._loops[thread_id].run_until_complete(coro)
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            return None

class FileWatcherThread(QThread):
    """مراقب الملفات - يقرأ الإشارات من ملف SignalsLog.txt"""
    signal_received = pyqtSignal(str, str, float, int)
    log_signal = pyqtSignal(str)
    
    def __init__(self, file_path: str = None):
        super().__init__()
        self.running = True
        self.file_path = file_path
        self.last_position = 0
        self.last_modify_time = 0
        
    def find_signal_file(self) -> str:
        """يبحث عن ملف الإشارات في مجلد MT4"""
        if self.file_path and os.path.exists(self.file_path):
            return self.file_path
        
        # البحث في المجلدات الافتراضية لـ MT4
        possible_paths = []
        
        # 1. مجلد MT4 الافتراضي
        app_data = os.path.expanduser("~/AppData/Roaming/MetaQuotes/Terminal")
        if os.path.exists(app_data):
            for terminal_id in os.listdir(app_data):
                terminal_path = os.path.join(app_data, terminal_id, "MQL4", "Files")
                if os.path.exists(terminal_path):
                    possible_paths.append(terminal_path)
        
        # 2. مجلد التثبيت الافتراضي
        program_files = os.path.expanduser("~/AppData/Local/Programs/MetaTrader 4")
        if os.path.exists(program_files):
            mql4_path = os.path.join(program_files, "MQL4", "Files")
            if os.path.exists(mql4_path):
                possible_paths.append(mql4_path)
        
        # 3. مجلد سطح المكتب (إذا قام المستخدم بوضع الملف هناك)
        desktop = os.path.expanduser("~/Desktop")
        if os.path.exists(desktop):
            possible_paths.append(desktop)
        
        # 4. المجلد الحالي
        possible_paths.append(os.getcwd())
        
        # البحث عن الملف في كل مسار
        for folder in possible_paths:
            test_path = os.path.join(folder, SIGNAL_FILE_NAME)
            if os.path.exists(test_path):
                self.log_signal.emit(f"📁 Found signal file at: {test_path}")
                return test_path
        
        return None
    
    def run(self):
        # البحث عن الملف
        self.file_path = self.find_signal_file()
        
        if not self.file_path:
            self.log_signal.emit(f"⚠️ {SIGNAL_FILE_NAME} not found! Please run the MT4 indicator first.")
            self.log_signal.emit(f"📁 Expected file location: MQL4/Files/{SIGNAL_FILE_NAME}")
            return
        
        self.log_signal.emit(self.tr('file_watcher_started').format(path=self.file_path))
        
        # تهيئة مؤشرات الملف
        try:
            if os.path.exists(self.file_path):
                self.last_position = os.path.getsize(self.file_path)
                self.last_modify_time = os.path.getmtime(self.file_path)
        except:
            pass
        
        while self.running:
            try:
                # التحقق من وجود الملف
                if not os.path.exists(self.file_path):
                    # محاولة إعادة البحث عن الملف
                    self.file_path = self.find_signal_file()
                    if not self.file_path:
                        time.sleep(2)
                        continue
                    self.last_position = 0
                
                # التحقق من التغييرات في الملف
                current_modify_time = os.path.getmtime(self.file_path)
                
                if current_modify_time != self.last_modify_time:
                    # تم تعديل الملف - قراءة السطور الجديدة
                    with open(self.file_path, 'r', encoding='utf-8') as f:
                        f.seek(self.last_position)
                        new_lines = f.readlines()
                        self.last_position = f.tell()
                    
                    self.last_modify_time = current_modify_time
                    
                    # معالجة كل سطر جديد
                    for line in new_lines:
                        line = line.strip()
                        if line:
                            self.process_signal_line(line)
                
                time.sleep(SIGNAL_FILE_POLLING_INTERVAL)
                
            except Exception as e:
                self.log_signal.emit(f"⚠️ File watcher error: {str(e)[:50]}")
                time.sleep(1)
    
    def process_signal_line(self, line: str):
        """معالجة سطر الإشارة من الملف"""
        try:
            # تنسيق الإشارة: [HH:MM:SS] SYMBOL,SIDE,AMOUNT,DURATION
            # مثال: [17:30:45] BTCUSD_otc,call,1.00,1
            
            # إزالة الطابع الزمني إذا كان موجوداً
            if '] ' in line:
                line = line.split('] ')[1]
            
            parts = line.split(',')
            if len(parts) >= 4:
                symbol = parts[0].strip()
                side = parts[1].strip().lower()
                amount = float(parts[2].strip())
                duration = int(parts[3].strip())
                
                # تحقق من صحة البيانات
                if side in ['call', 'put'] and amount > 0 and duration > 0:
                    self.log_signal.emit(self.tr('signal_received').format(
                        symbol=symbol, 
                        direction='CALL' if side == 'call' else 'PUT', 
                        amount=amount
                    ))
                    self.signal_received.emit(symbol, side, amount, duration)
                else:
                    self.log_signal.emit(f"⚠️ Invalid signal data: {line}")
            else:
                self.log_signal.emit(f"⚠️ Malformed signal line: {line}")
                
        except Exception as e:
            self.log_signal.emit(f"⚠️ Error processing signal: {str(e)[:50]} - Line: {line}")
    
    def tr(self, key):
        return LANGUAGES.get('en', {}).get(key, key)
    
    def stop(self):
        self.running = False
        self.quit()
        self.wait(3000)

class RobustConnectionManager(QThread):
    connection_lost = pyqtSignal()
    connection_restored = pyqtSignal()
    reconnecting = pyqtSignal(int, int)
    log_signal = pyqtSignal(str)
    connection_status_changed = pyqtSignal(bool)
    
    def __init__(self, email, password, account_mode):
        super().__init__()
        self.email = email
        self.password = password
        self.account_mode = account_mode
        self.running = True
        self.client = None
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_attempts = MAX_RECONNECT_ATTEMPTS
        self.last_heartbeat = time.time()
        self.last_successful_balance = 0
        self.lock = threading.Lock()
        self.reconnect_lock = threading.Lock()
        self.is_reconnecting = False
        
    def set_client(self, client):
        with self.lock:
            self.client = client
            self.is_connected = True
            self.reconnect_attempts = 0
            self.last_heartbeat = time.time()
        
    def _check_connection(self) -> bool:
        with self.lock:
            if not self.client:
                return False
        
        try:
            balance = AsyncHelper.run_async(self.client.get_balance(), timeout=8)
            if balance is not None and float(balance) > 0:
                self.last_successful_balance = float(balance)
                return True
        except Exception as e:
            pass
        
        try:
            if hasattr(self.client, 'websocket') and self.client.websocket:
                if hasattr(self.client.websocket, 'sock') and self.client.websocket.sock:
                    return True
        except:
            pass
        
        if time.time() - self.last_heartbeat > 45:
            return False
        
        return self.is_connected
    
    def _force_reconnect(self) -> bool:
        with self.reconnect_lock:
            if self.is_reconnecting:
                return False
            self.is_reconnecting = True
        
        try:
            self.log_signal.emit("🔄 Attempting forced reconnection...")
            
            try:
                if self.client:
                    AsyncHelper.run_async(self.client.close(), timeout=5)
            except:
                pass
            
            for attempt in range(3):
                try:
                    new_client = Quotex(email=self.email, password=self.password, lang="en")
                    time.sleep(random.uniform(1, 2))
                    check, reason = AsyncHelper.run_async(new_client.connect(), timeout=15)
                    
                    if check and new_client:
                        if hasattr(new_client, 'change_account'):
                            AsyncHelper.run_async(new_client.change_account(self.account_mode), timeout=5)
                        
                        balance = AsyncHelper.run_async(new_client.get_balance(), timeout=8)
                        if balance is not None and float(balance) > 0:
                            with self.lock:
                                self.client = new_client
                                self.is_connected = True
                                self.last_heartbeat = time.time()
                                self.reconnect_attempts = 0
                            self.is_reconnecting = False
                            return True
                    time.sleep(2)
                except Exception as e:
                    continue
            
            self.is_reconnecting = False
            return False
        except Exception as e:
            self.log_signal.emit(f"⚠️ Force reconnect error: {str(e)[:50]}")
            self.is_reconnecting = False
            return False
    
    def _send_heartbeat(self):
        try:
            if self.client and self.is_connected:
                AsyncHelper.run_async(self.client.get_balance(), timeout=5)
                self.last_heartbeat = time.time()
        except:
            pass
    
    def run(self):
        last_heartbeat_send = time.time()
        
        while self.running:
            try:
                time.sleep(CONNECTION_CHECK_INTERVAL)
                if not self.running:
                    break
                
                if time.time() - last_heartbeat_send > WEBSOCKET_KEEPALIVE_INTERVAL:
                    last_heartbeat_send = time.time()
                    self._send_heartbeat()
                
                connected = self._check_connection()
                
                if not connected and self.is_connected:
                    self.log_signal.emit(self.tr('connection_lost'))
                    self.connection_lost.emit()
                    self.is_connected = False
                    self.connection_status_changed.emit(False)
                    self._attempt_reconnect()
                    
                elif connected and not self.is_connected:
                    self.log_signal.emit(self.tr('connection_restored'))
                    self.is_connected = True
                    self.reconnect_attempts = 0
                    self.last_heartbeat = time.time()
                    self.connection_restored.emit()
                    self.connection_status_changed.emit(True)
                    
                elif connected:
                    self.last_heartbeat = time.time()
                    
            except Exception as e:
                self.log_signal.emit(f"⚠️ Connection monitor error: {str(e)[:50]}")
                time.sleep(3)
    
    def _attempt_reconnect(self):
        attempt = 0
        
        while self.running and not self.is_connected and attempt < self.max_attempts:
            attempt += 1
            self.reconnecting.emit(attempt, self.max_attempts)
            self.log_signal.emit(self.tr('reconnecting').format(attempt=attempt, max=self.max_attempts))
            success = self._force_reconnect()
            
            if success:
                self.log_signal.emit(self.tr('reconnect_success'))
                return
            else:
                wait_time = min(RECONNECT_DELAY * attempt, 5)
                for _ in range(wait_time):
                    if not self.running:
                        return
                    time.sleep(1)
        
        if not self.is_connected:
            self.log_signal.emit(self.tr('reconnect_failed').format(attempts=self.max_attempts))
    
    def tr(self, key):
        return LANGUAGES.get('en', {}).get(key, key)
    
    def stop(self):
        self.running = False
        self.quit()
        self.wait(5000)

class AssetsLoader(QThread):
    finished = pyqtSignal(list)
    progress = pyqtSignal(str)
    
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.start_time = time.time()
        
    def run(self):
        try:
            self.progress.emit("Loading assets from Quotex platform...")
            assets = []
            
            try:
                instruments = AsyncHelper.run_async(self.client.get_instruments(), timeout=15)
                
                if instruments and isinstance(instruments, (list, tuple)) and len(instruments) > 0:
                    for instrument in instruments:
                        if isinstance(instrument, (list, tuple)) and len(instrument) >= 2:
                            asset_name = instrument[1]
                            if asset_name and isinstance(asset_name, str):
                                if asset_name not in assets:
                                    assets.append(asset_name)
                    
                    if assets:
                        self.progress.emit(f"✅ Loaded {len(assets)} assets from Quotex")
                        self.finished.emit(sorted(assets))
                        return
            except Exception as e:
                self.progress.emit(f"⚠️ Error loading instruments: {str(e)[:50]}")
            
            try:
                if hasattr(self.client, 'api') and hasattr(self.client.api, 'all_instruments'):
                    all_instruments = self.client.api.all_instruments
                    if all_instruments and isinstance(all_instruments, dict):
                        for key, value in all_instruments.items():
                            if isinstance(value, (list, tuple)) and len(value) >= 2:
                                asset_name = value[1] if len(value) > 1 else key
                                if asset_name and asset_name not in assets:
                                    assets.append(asset_name)
            except:
                pass
            
            if assets:
                self.finished.emit(sorted(assets))
            else:
                default_assets = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", 
                                 "XAUUSD", "BTCUSD", "ETHUSD", "US30", "US500", "USTEC"]
                self.progress.emit("⚠️ Could not load assets from API, using fallback list")
                self.finished.emit(default_assets)
                
        except Exception as e:
            self.progress.emit(f"❌ Assets loading error: {str(e)[:50]}")
            self.finished.emit(["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"])
        finally:
            self.client = None

class AutoReloginThread(QThread):
    login_successful = pyqtSignal(bool, object)
    login_failed = pyqtSignal(str)
    log_signal = pyqtSignal(str)
    
    def __init__(self, email, password, account_mode):
        super().__init__()
        self.email = email
        self.password = password
        self.account_mode = account_mode
        self.running = True
        self.consecutive_failures = 0
        self.max_retries = 3
        self.retry_delay = 5
        
    def run(self):
        while self.running:
            try:
                for _ in range(RELOGIN_INTERVAL):
                    if not self.running:
                        return
                    time.sleep(1)
                
                if not self.running:
                    break
                
                success = False
                attempt = 0
                while not success and attempt < self.max_retries and self.running:
                    attempt += 1
                    if attempt > 1:
                        time.sleep(self.retry_delay)
                    
                    success, client = self._attempt_relogin()
                    
                    if success:
                        self.consecutive_failures = 0
                        self.login_successful.emit(True, client)
                        break
                    else:
                        self.consecutive_failures += 1
                        if attempt >= self.max_retries:
                            if self.consecutive_failures >= 3:
                                time.sleep(60)
            except Exception as e:
                time.sleep(30)
    
    def _attempt_relogin(self):
        try:
            new_client = Quotex(email=self.email, password=self.password, lang="en")
            import random
            time.sleep(random.uniform(1, 2))
            check, reason = AsyncHelper.run_async(new_client.connect(), timeout=15)
            
            if check and new_client:
                if hasattr(new_client, 'change_account'):
                    AsyncHelper.run_async(new_client.change_account(self.account_mode), timeout=5)
                balance = AsyncHelper.run_async(new_client.get_balance(), timeout=8)
                if balance is not None:
                    return True, new_client
            return False, None
        except Exception as e:
            return False, None
    
    def stop(self):
        self.running = False
        self.quit()
        self.wait(5000)

class SessionManager:
    def __init__(self):
        self.last_activity = time.time()
        self.lock = threading.Lock()
        
    def update_activity(self):
        with self.lock:
            self.last_activity = time.time()
            
    def is_session_expired(self, timeout=900):
        with self.lock:
            return (time.time() - self.last_activity) > timeout

class MT4ReconnectThread(QThread):
    log_signal = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.interval = MT4_RECONNECT_INTERVAL
        
    def run(self):
        while self.running:
            try:
                for _ in range(self.interval):
                    if not self.running:
                        return
                    time.sleep(1)
                if not self.running:
                    break
                self.log_signal.emit(self.tr('mt4_reconnect'))
                success = self._check_mt4_file()
                if success:
                    self.log_signal.emit(self.tr('mt4_reconnected'))
                else:
                    self.log_signal.emit("⚠️ MT4 signal file not found - indicator may not be running")
            except Exception as e:
                self.log_signal.emit(f"⚠️ MT4 reconnect error: {e}")
    
    def _check_mt4_file(self) -> bool:
        try:
            app_data = os.path.expanduser("~/AppData/Roaming/MetaQuotes/Terminal")
            if os.path.exists(app_data):
                for terminal_id in os.listdir(app_data):
                    file_path = os.path.join(app_data, terminal_id, "MQL4", "Files", SIGNAL_FILE_NAME)
                    if os.path.exists(file_path):
                        return True
            return False
        except:
            return False
    
    def tr(self, key):
        return LANGUAGES.get('en', {}).get(key, key)
    
    def stop(self):
        self.running = False
        self.quit()
        self.wait(3000)

class TradeManager(QObject):
    trade_started = pyqtSignal(str, dict)
    trade_progress = pyqtSignal(str, int, int)
    trade_completed = pyqtSignal(str, dict)
    trade_not_executed = pyqtSignal(dict)
    log_signal = pyqtSignal(str)
    martingale_triggered = pyqtSignal(str, dict)
    balance_updated = pyqtSignal(float)
    sound_signal = pyqtSignal(str)
    active_trades_updated = pyqtSignal()
    
    def __init__(self, client, martingale_settings=None, global_stop_loss=0.0, global_take_profit=0.0, connection_manager=None):
        super().__init__()
        self.client = client
        self.connection_manager = connection_manager
        self.session_manager = SessionManager()
        self.active_trades: Dict[str, TradeInfo] = {}
        self.trade_history: deque = deque(maxlen=MAX_HISTORY_SIZE)
        self.not_executed_trades: deque = deque(maxlen=MAX_HISTORY_SIZE)
        self._lock = QMutex()
        self.client_lock = threading.Lock()
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_trades, daemon=True)
        self._monitor_thread.start()
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._emit_active_trades_update)
        self._update_timer.start(200)
        
        self.current_balance = 0.0
        self.initial_balance = 0.0
        self.net_profit = 0.0
        
        self.global_stop_loss = global_stop_loss
        self.global_take_profit = global_take_profit
        self.stop_loss_triggered = False
        self.take_profit_triggered = False
        
        self.martingale_settings = martingale_settings or {
            'enabled': False,
            'martingale_type': MartingaleType.DISABLED,
            'max_steps': 5
        }
        
        self.pending_martingale: Dict[str, MartingaleInfo] = {}
        self.last_cleanup = time.time()
        self.retry_timer = QTimer()
        self.retry_timer.timeout.connect(self._retry_failed_trades)
        self.retry_timer.start(10000)
        self.failed_trades_queue: deque = deque(maxlen=100)
    
    def _retry_failed_trades(self):
        if not self.failed_trades_queue:
            return
        
        if not self._is_connected():
            return
        
        failed_trades = list(self.failed_trades_queue)
        self.failed_trades_queue.clear()
        
        for trade_data in failed_trades:
            retry_count = trade_data.get('retry_count', 0) + 1
            if retry_count <= TRADE_RETRY_ATTEMPTS:
                self.log_signal.emit(f"🔄 Retrying trade for {trade_data['symbol']}... (Attempt {retry_count}/{TRADE_RETRY_ATTEMPTS})")
                trade_data['retry_count'] = retry_count
                
                time.sleep(TRADE_RETRY_DELAY)
                
                internal_id = self.open_trade(
                    trade_data['symbol'],
                    trade_data['direction'],
                    trade_data['amount'],
                    trade_data['duration'],
                    parent_trade_id=trade_data.get('parent_trade_id', ''),
                    signal_source="FILE_RETRY",
                    retry_count=retry_count
                )
                
                if internal_id:
                    self.log_signal.emit(f"✅ Trade retry successful for {trade_data['symbol']}!")
                else:
                    self.log_signal.emit(f"⚠️ Trade retry pending for {trade_data['symbol']} (will retry again)")
                    if retry_count < TRADE_RETRY_ATTEMPTS:
                        self.failed_trades_queue.append(trade_data)
            else:
                self.log_signal.emit(f"❌ All retry attempts failed for {trade_data['symbol']}")
                trade_info = TradeInfo(
                    trade_id="", internal_id=str(uuid.uuid4())[:8], 
                    symbol=trade_data['symbol'], direction=trade_data['direction'], 
                    amount=trade_data['amount'], duration_minutes=trade_data['duration'],
                    entry_time=datetime.now(), requested_duration_seconds=trade_data['duration'] * 60,
                    candle_remaining_seconds=0, actual_wait_seconds=0,
                    candle_close_time=datetime.now(), wait_type="retry_failed",
                    parent_trade_id=trade_data.get('parent_trade_id', ''),
                    signal_source="FILE_RETRY_FAILED", 
                    error_message=f"Failed after {TRADE_RETRY_ATTEMPTS} retry attempts",
                    retry_count=retry_count
                )
                trade_info.status = TradeStatus.NOT_EXECUTED
                self._handle_not_executed_trade(trade_info)
    
    def _is_connected(self) -> bool:
        if not self.client:
            return False
        
        if self.connection_manager:
            if self.connection_manager.is_connected:
                return True
            try:
                balance = AsyncHelper.run_async(self.client.get_balance(), timeout=5)
                if balance is not None:
                    return True
            except:
                pass
            return False
        
        try:
            balance = AsyncHelper.run_async(self.client.get_balance(), timeout=5)
            return balance is not None
        except:
            return False
    
    def _ensure_connection_before_trade(self, max_wait=10) -> bool:
        start_time = time.time()
        while time.time() - start_time < max_wait:
            if self._is_connected():
                return True
            time.sleep(0.5)
        return False
    
    async def check_asset_open(self, asset_name: str):
        try:
            instruments = await self.client.get_instruments()
            if not instruments:
                return [None, [None, None, None]]
            for instrument in instruments:
                if len(instrument) >= 2 and asset_name == instrument[1]:
                    self.client.api.current_asset = asset_name
                    return instrument, (instrument[0], instrument[2].replace("\n", "") if len(instrument) > 2 else "", instrument[14] if len(instrument) > 14 else "")
            return [None, [None, None, None]]
        except Exception as e:
            self.log_signal.emit(f"⚠️ Error checking asset {asset_name}: {str(e)[:50]}")
            return [None, [None, None, None]]
    
    def set_risk_parameters(self, stop_loss_pct: float, take_profit_pct: float):
        with QMutexLocker(self._lock):
            self.global_stop_loss = stop_loss_pct
            self.global_take_profit = take_profit_pct
            self.stop_loss_triggered = False
            self.take_profit_triggered = False
        self.log_signal.emit(f"📊 Global Risk: Stop Loss {stop_loss_pct}% | Take Profit {take_profit_pct}%")
    
    def _check_global_risk(self, new_profit: float) -> bool:
        if self.initial_balance == 0:
            return False
        self.net_profit += new_profit
        profit_percentage = (self.net_profit / self.initial_balance) * 100
        if self.global_stop_loss > 0 and self.net_profit < 0:
            loss_pct = abs(profit_percentage)
            if loss_pct >= self.global_stop_loss and not self.stop_loss_triggered:
                self.stop_loss_triggered = True
                self.log_signal.emit(f"🛑 GLOBAL STOP LOSS TRIGGERED! Loss: {loss_pct:.1f}% (Limit: {self.global_stop_loss}%)")
                self.sound_signal.emit("stop_loss")
                return True
        if self.global_take_profit > 0 and self.net_profit > 0:
            if profit_percentage >= self.global_take_profit and not self.take_profit_triggered:
                self.take_profit_triggered = True
                self.log_signal.emit(f"🎯 GLOBAL TAKE PROFIT TRIGGERED! Profit: {profit_percentage:.1f}% (Target: {self.global_take_profit}%)")
                self.sound_signal.emit("take_profit")
                return True
        return False
    
    def reset_risk_triggers(self):
        with QMutexLocker(self._lock):
            self.stop_loss_triggered = False
            self.take_profit_triggered = False
            self.initial_balance = self.current_balance
            self.net_profit = 0.0
        self.log_signal.emit("🔄 Risk triggers reset for new session")
    
    def _emit_active_trades_update(self):
        self.active_trades_updated.emit()
    
    def _refresh_session(self):
        if not self.client:
            return
        try:
            with self.client_lock:
                balance = AsyncHelper.run_async(self.client.get_balance(), timeout=8)
            if balance is not None:
                self.session_manager.update_activity()
                self.current_balance = float(balance)
                self.balance_updated.emit(self.current_balance)
        except Exception as e:
            pass
    
    def update_client(self, new_client):
        with self.client_lock:
            with QMutexLocker(self._lock):
                self.client = new_client
            self.session_manager.update_activity()
            try:
                balance = AsyncHelper.run_async(self.client.get_balance(), timeout=8)
                if balance is not None:
                    self.current_balance = float(balance)
                    self.initial_balance = self.current_balance
                    self.net_profit = 0.0
                    self.balance_updated.emit(self.current_balance)
                    self.log_signal.emit(f"💰 New account balance: ${self.current_balance:.2f}")
            except:
                pass
    
    def update_martingale_settings(self, settings):
        with QMutexLocker(self._lock):
            self.martingale_settings = settings
    
    def calculate_candle_close_time(self, entry_time: datetime, duration_minutes: int) -> Tuple[datetime, float, float, str]:
        entry_timestamp = entry_time.timestamp()
        duration_seconds = duration_minutes * 60
        current_minute_start = int(entry_timestamp / 60) * 60
        seconds_into_current_minute = entry_timestamp - current_minute_start
        candle_remaining_seconds = 60 - seconds_into_current_minute
        if candle_remaining_seconds < 30:
            total_wait_seconds = candle_remaining_seconds + duration_seconds
            wait_type = "wait_full_duration"
        else:
            total_wait_seconds = candle_remaining_seconds
            wait_type = "wait_candle_only"
        return datetime.fromtimestamp(entry_timestamp + total_wait_seconds), candle_remaining_seconds, total_wait_seconds, wait_type
    
    def open_trade(self, symbol: str, direction: str, amount: float, duration_minutes: int, 
                   parent_trade_id: str = "", martingale_info: MartingaleInfo = None, 
                   signal_source: str = "FILE", retry_count: int = 0) -> Optional[str]:
        try:
            with QMutexLocker(self._lock):
                if self.stop_loss_triggered or self.take_profit_triggered:
                    self.log_signal.emit("⚠️ Global risk limit reached. Trading paused.")
                    self.sound_signal.emit("blocked")
                    return None
            
            if not self._ensure_connection_before_trade(max_wait=10):
                self.log_signal.emit("⚠️ No connection to Quotex. Trade queued for retry.")
                self.failed_trades_queue.append({
                    'symbol': symbol,
                    'direction': direction,
                    'amount': amount,
                    'duration': duration_minutes,
                    'parent_trade_id': parent_trade_id,
                    'signal_source': signal_source,
                    'retry_count': retry_count
                })
                return None
            
            internal_id = str(uuid.uuid4())[:8]
            entry_time = datetime.now()
            asset_check = AsyncHelper.run_async(self.check_asset_open(symbol), timeout=10)
            
            if not asset_check or not asset_check[0]:
                error_msg = f"⚠️ {symbol} is CLOSED - Trade rejected"
                self.log_signal.emit(error_msg)
                self.sound_signal.emit("blocked")
                trade_info = TradeInfo(
                    trade_id="", internal_id=internal_id, symbol=symbol, direction=direction, amount=amount,
                    duration_minutes=duration_minutes, entry_time=entry_time,
                    requested_duration_seconds=duration_minutes * 60,
                    candle_remaining_seconds=0, actual_wait_seconds=0,
                    candle_close_time=datetime.now(), wait_type="rejected",
                    parent_trade_id=parent_trade_id, martingale_info=martingale_info,
                    signal_source=signal_source, error_message=f"Asset closed: {symbol}",
                    retry_count=retry_count
                )
                trade_info.status = TradeStatus.NOT_EXECUTED
                self._handle_not_executed_trade(trade_info)
                return None
            
            actual_symbol = asset_check[0][1]
            candle_close_time, candle_remaining, total_wait, wait_type = self.calculate_candle_close_time(entry_time, duration_minutes)
            
            trade_info = TradeInfo(
                trade_id="", internal_id=internal_id, symbol=actual_symbol, direction=direction, amount=amount,
                duration_minutes=duration_minutes, entry_time=entry_time,
                requested_duration_seconds=duration_minutes * 60,
                candle_remaining_seconds=candle_remaining,
                actual_wait_seconds=total_wait,
                candle_close_time=candle_close_time,
                wait_type=wait_type,
                parent_trade_id=parent_trade_id,
                martingale_info=martingale_info,
                signal_source=signal_source,
                retry_count=retry_count
            )
            
            with QMutexLocker(self._lock):
                self.active_trades[internal_id] = trade_info
            self.active_trades_updated.emit()
            
            threading.Thread(target=self._execute_trade_thread, args=(internal_id, actual_symbol, asset_check), daemon=True).start()
            
            martingale_text = f" [M{martingale_info.current_step}]" if martingale_info else ""
            retry_text = f" [Retry {retry_count}]" if retry_count > 0 else ""
            self.log_signal.emit(f"⚡ {internal_id}{martingale_text}{retry_text}: {actual_symbol} {direction.upper()} ${amount:.2f}")
            self.sound_signal.emit("trade")
            return internal_id
        except Exception as e:
            self.log_signal.emit(f"❌ Error opening trade: {str(e)[:50]}")
            return None
    
    def _execute_trade_thread(self, internal_id: str, symbol: str, asset_data):
        try:
            with QMutexLocker(self._lock):
                if internal_id not in self.active_trades:
                    return
                trade = self.active_trades[internal_id]
            
            trade.status = TradeStatus.RUNNING
            self.active_trades_updated.emit()
            self.session_manager.update_activity()
            
            if asset_data and len(asset_data) >= 2:
                name = asset_data[0][1]
                data = asset_data[1] if len(asset_data) > 1 else None
            else:
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        with self.client_lock:
                            asset_data = AsyncHelper.run_async(self.client.get_available_asset(symbol, True), timeout=10)
                        if asset_data and len(asset_data) >= 2:
                            name, data = asset_data
                            break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            time.sleep(1)
                        else:
                            trade.status = TradeStatus.NOT_EXECUTED
                            trade.error_message = f"Asset not available after {max_retries} attempts"
                            self._handle_not_executed_trade(trade)
                            return
            
            if not data or len(data) < 3 or not data[2]:
                trade.status = TradeStatus.NOT_EXECUTED
                trade.error_message = "Asset not tradable"
                self._handle_not_executed_trade(trade)
                return
            
            balance = self._get_balance_with_retry()
            if balance is None:
                trade.status = TradeStatus.NOT_EXECUTED
                trade.error_message = "Failed to get balance - connection issue"
                self._handle_not_executed_trade(trade)
                return
            
            trade.balance_before = balance
            
            with QMutexLocker(self._lock):
                if self.initial_balance == 0:
                    self.initial_balance = trade.balance_before
                    self.log_signal.emit(f"💰 Initial balance set to: ${self.initial_balance:.2f}")
            
            duration_seconds = trade.duration_minutes * 60
            
            result = None
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    with self.client_lock:
                        result = AsyncHelper.run_async(
                            self.client.buy(trade.amount, name, trade.direction, duration_seconds),
                            timeout=15
                        )
                    if result:
                        break
                except Exception as e:
                    if attempt < max_retries - 1:
                        self.log_signal.emit(f"⚠️ Buy attempt {attempt+1} failed, retrying...")
                        time.sleep(2)
                    else:
                        trade.status = TradeStatus.NOT_EXECUTED
                        trade.error_message = f"Buy failed after {max_retries} attempts: {str(e)[:50]}"
                        self._handle_not_executed_trade(trade)
                        return
            
            if not result:
                trade.status = TradeStatus.NOT_EXECUTED
                trade.error_message = "Buy returned None - Insufficient balance or connection issue"
                self._handle_not_executed_trade(trade)
                return
            
            if isinstance(result, tuple) and len(result) == 2:
                status, buy_info = result
                if not status:
                    trade.status = TradeStatus.NOT_EXECUTED
                    trade.error_message = str(buy_info)[:100]
                    self._handle_not_executed_trade(trade)
                    return
                if isinstance(buy_info, dict):
                    trade.api_trade_id = buy_info.get('id')
                    trade.api_trade_id_int = buy_info.get('id_number')
                    trade.trade_id = str(trade.api_trade_id) if trade.api_trade_id else internal_id
                else:
                    trade.api_trade_id = buy_info
                    trade.trade_id = str(buy_info)
            else:
                trade.api_trade_id = result
                trade.trade_id = str(result)
            
            self.trade_started.emit(internal_id, trade.to_dict())
            self._wait_and_check(internal_id)
        except Exception as e:
            with QMutexLocker(self._lock):
                if internal_id in self.active_trades:
                    trade = self.active_trades[internal_id]
                    trade.status = TradeStatus.NOT_EXECUTED
                    trade.error_message = str(e)[:100]
                    self._handle_not_executed_trade(trade)
    
    def _get_balance_with_retry(self, max_retries=5) -> Optional[float]:
        for attempt in range(max_retries):
            try:
                with self.client_lock:
                    balance = AsyncHelper.run_async(self.client.get_balance(), timeout=8)
                if balance is not None:
                    self.session_manager.update_activity()
                    self.current_balance = float(balance)
                    self.balance_updated.emit(self.current_balance)
                    return float(balance)
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
        return None
    
    def _wait_and_check(self, internal_id: str):
        try:
            with QMutexLocker(self._lock):
                if internal_id not in self.active_trades:
                    return
                trade = self.active_trades[internal_id]
            
            trade.status = TradeStatus.WAITING_CANDLE_CLOSE
            self.active_trades_updated.emit()
            start_wait = time.time()
            total_wait = trade.actual_wait_seconds
            
            while time.time() - start_wait < total_wait:
                elapsed = time.time() - start_wait
                self.trade_progress.emit(internal_id, int(elapsed), int(total_wait))
                if not self._is_connected():
                    trade.status = TradeStatus.RETRYING
                    trade.error_message = "Connection lost during trade - will retry"
                    self.log_signal.emit(f"⚠️ Connection lost during trade {internal_id}, will retry...")
                    self._handle_not_executed_trade(trade)
                    return
                time.sleep(0.2)
            self._check_result_internal(internal_id)
        except Exception as e:
            pass
    
    def _check_result_internal(self, internal_id: str):
        try:
            with QMutexLocker(self._lock):
                if internal_id not in self.active_trades:
                    return
                trade = self.active_trades[internal_id]
            
            trade.status = TradeStatus.CHECKING_RESULT
            self.active_trades_updated.emit()
            
            win_result = None
            profit_amount = 0
            is_break_even = False
            
            for attempt in range(5):
                time.sleep(1.0)
                win_result, profit_amount, is_break_even = self._get_result_with_retry(trade)
                if win_result is not None:
                    break
                self.log_signal.emit(f"⚠️ Checking result attempt {attempt+1}/5 for trade {internal_id}")
            
            if win_result is None:
                balance_after = self._get_balance_with_retry()
                if balance_after is not None:
                    trade.balance_after = balance_after
                    balance_change = trade.balance_after - trade.balance_before
                    if balance_change > 0:
                        win_result = True
                        profit_amount = balance_change
                        is_break_even = False
                    elif balance_change < 0:
                        win_result = False
                        profit_amount = -balance_change
                        is_break_even = False
                    else:
                        win_result = True
                        profit_amount = 0
                        is_break_even = True
            
            self._finalize_trade_result(trade, win_result, profit_amount, is_break_even)
        except Exception as e:
            with QMutexLocker(self._lock):
                if internal_id in self.active_trades:
                    self.active_trades[internal_id].status = TradeStatus.ERROR
    
    def _get_result_with_retry(self, trade: TradeInfo, max_retries=3) -> Tuple[Optional[bool], float, bool]:
        win_result = None
        profit_amount = 0.0
        is_break_even = False
        
        for attempt in range(max_retries):
            if trade.api_trade_id_int:
                try:
                    with self.client_lock:
                        win_result = AsyncHelper.run_async(
                            self.client.check_win(int(trade.api_trade_id_int)), timeout=8
                        )
                    if win_result is not None:
                        balance_before = trade.balance_before
                        balance_after = self._get_balance_with_retry()
                        if balance_after is not None:
                            balance_change = balance_after - balance_before
                            if abs(balance_change) < 0.01:
                                is_break_even = True
                                win_result = True
                                profit_amount = 0.0
                                return win_result, profit_amount, is_break_even
                        
                        if win_result:
                            profit_amount = trade.amount * PAYOUT_PERCENTAGE
                        else:
                            profit_amount = 0.0
                        return win_result, profit_amount, False
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(1)
                    continue
            
            if trade.trade_id:
                try:
                    with self.client_lock:
                        status, result_data = AsyncHelper.run_async(
                            self.client.get_result(str(trade.trade_id)), timeout=8
                        )
                    if status == "win":
                        win_result = True
                        is_break_even = False
                    elif status == "loss":
                        win_result = False
                        is_break_even = False
                    elif status == "equal":
                        win_result = True
                        is_break_even = True
                        profit_amount = 0
                        return win_result, profit_amount, is_break_even
                    
                    if result_data and isinstance(result_data, dict):
                        profit_amount = float(result_data.get("profitAmount", 0))
                        if profit_amount == 0 and win_result:
                            profit_amount = trade.amount * PAYOUT_PERCENTAGE
                    
                    if win_result is not None:
                        return win_result, profit_amount, is_break_even
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(1)
                    continue
        
        return win_result, profit_amount, is_break_even
    
    def _handle_not_executed_trade(self, trade: TradeInfo):
        trade.completion_time = datetime.now()
        trade.status = TradeStatus.NOT_EXECUTED
        
        with QMutexLocker(self._lock):
            self.not_executed_trades.appendleft(trade.to_dict())
            if trade.internal_id in self.active_trades:
                del self.active_trades[trade.internal_id]
        self.active_trades_updated.emit()
        self.log_signal.emit(f"⚠️ {trade.internal_id}: NOT EXECUTED - {trade.error_message}")
        self.trade_not_executed.emit(trade.to_dict())
    
    def _finalize_trade_result(self, trade: TradeInfo, win_result: Optional[bool], profit_amount: float, is_break_even: bool):
        if trade.balance_after == 0:
            balance = self._get_balance_with_retry()
            if balance is not None:
                trade.balance_after = balance
            else:
                trade.balance_after = trade.balance_before
        
        balance_change = trade.balance_after - trade.balance_before
        
        if is_break_even:
            trade.profit = 0.0
            trade.win = True
            trade.result_type = "break_even"
            self.log_signal.emit(f"⚖️ {trade.internal_id}: $0.00 (Break Even)")
        elif win_result is not None and win_result:
            if profit_amount > 0:
                trade.profit = profit_amount
                trade.win = True
                trade.result_type = "win"
            else:
                trade.profit = 0
                trade.win = True
                trade.result_type = "break_even"
        elif win_result is not None and not win_result:
            if balance_change == 0 and profit_amount == 0:
                trade.profit = 0
                trade.win = True
                trade.result_type = "break_even"
            else:
                trade.profit = -trade.amount
                trade.win = False
                trade.result_type = "loss"
        else:
            if balance_change > 0:
                trade.profit = balance_change
                trade.win = True
                trade.result_type = "win"
            elif balance_change < 0:
                trade.profit = balance_change
                trade.win = False
                trade.result_type = "loss"
            else:
                trade.profit = 0
                trade.win = True
                trade.result_type = "break_even"
        
        trade.completion_time = datetime.now()
        trade.status = TradeStatus.COMPLETED
        self.current_balance = trade.balance_after
        
        if trade.result_type != "break_even":
            risk_triggered = self._check_global_risk(trade.profit)
        else:
            risk_triggered = False
        
        with QMutexLocker(self._lock):
            self.trade_history.appendleft(trade.to_dict())
            if trade.internal_id in self.active_trades:
                del self.active_trades[trade.internal_id]
        self.active_trades_updated.emit()
        
        profit_pct = (self.net_profit / self.initial_balance * 100) if self.initial_balance > 0 else 0
        
        if trade.result_type == "win":
            total_returned = trade.amount + trade.profit
            self.log_signal.emit(f"✅ {trade.internal_id}: +${trade.profit:.2f} (Total: ${total_returned:.2f})")
            self.balance_updated.emit(self.current_balance)
            self.sound_signal.emit("win")
        elif trade.result_type == "loss":
            self.log_signal.emit(f"❌ {trade.internal_id}: -${abs(trade.profit):.2f}")
            self.balance_updated.emit(self.current_balance)
            self.sound_signal.emit("loss")
        else:
            self.log_signal.emit(f"⚖️ {trade.internal_id}: $0.00 (Break Even)")
            self.balance_updated.emit(self.current_balance)
        
        if risk_triggered:
            self.log_signal.emit("🛑 Trading paused until risk is reset")
        
        self.trade_completed.emit(trade.internal_id, trade.to_dict())
        
        if trade.result_type == "loss" and self.martingale_settings['enabled'] and not risk_triggered:
            self._handle_martingale(trade)
    
    def _handle_martingale(self, loss_trade: TradeInfo):
        if loss_trade.martingale_info:
            if loss_trade.martingale_info.current_step >= loss_trade.martingale_info.max_steps:
                self.log_signal.emit(f"⚠️ Martingale max steps ({loss_trade.martingale_info.max_steps}) reached for {loss_trade.symbol}")
                return
        
        martingale_type = self.martingale_settings['martingale_type']
        if martingale_type == MartingaleType.DISABLED:
            return
        
        if loss_trade.martingale_info:
            base_amount = loss_trade.martingale_info.base_amount
            current_step = loss_trade.martingale_info.current_step + 1
            max_steps = loss_trade.martingale_info.max_steps
            original_symbol = loss_trade.martingale_info.original_symbol
        else:
            base_amount = loss_trade.amount
            current_step = 1
            max_steps = self.martingale_settings['max_steps']
            original_symbol = loss_trade.symbol
        
        if current_step > max_steps:
            self.log_signal.emit(f"⚠️ Martingale max steps ({max_steps}) would be exceeded for {original_symbol}")
            return
        
        next_amount = base_amount * (2 ** current_step)
        current_balance = self.current_balance
        if next_amount > current_balance * 0.9:
            self.log_signal.emit(f"⚠️ Martingale M{current_step} cancelled: Insufficient balance (Need ${next_amount:.2f}, Have ${current_balance:.2f})")
            return
        
        martingale_info = MartingaleInfo(
            enabled=True,
            martingale_type=martingale_type,
            max_steps=max_steps,
            current_step=current_step,
            base_amount=base_amount,
            original_symbol=original_symbol,
            loss_occurred_at=datetime.now(),
            pending_double=True
        )
        
        if martingale_type == MartingaleType.NEXT_OPPORTUNITY_SAME:
            with QMutexLocker(self._lock):
                self.pending_martingale[loss_trade.symbol] = martingale_info
            self.log_signal.emit(f"⏳ M{current_step} pending for {loss_trade.symbol} (${next_amount:.2f})")
        elif martingale_type == MartingaleType.NEXT_OPPORTUNITY_ANY:
            with QMutexLocker(self._lock):
                self.pending_martingale["ANY"] = martingale_info
            self.log_signal.emit(f"⏳ M{current_step} pending for ANY pair (${next_amount:.2f})")
        
        self.martingale_triggered.emit(loss_trade.internal_id, {
            'symbol': loss_trade.symbol,
            'step': current_step,
            'amount': next_amount,
            'type': martingale_type.value
        })
    
    def check_pending_martingale(self, symbol: str) -> Optional[MartingaleInfo]:
        with QMutexLocker(self._lock):
            if symbol in self.pending_martingale:
                info = self.pending_martingale.pop(symbol)
                self.log_signal.emit(f"🎯 Executing Martingale M{info.current_step} on {symbol} (${info.calculate_next_amount():.2f})")
                return info
            if "ANY" in self.pending_martingale:
                info = self.pending_martingale.pop("ANY")
                info.original_symbol = symbol
                self.log_signal.emit(f"🎯 Executing Martingale M{info.current_step} on ANY -> {symbol} (${info.calculate_next_amount():.2f})")
                return info
        return None
    
    def _get_balance(self) -> float:
        return self._get_balance_with_retry() or self.current_balance
    
    def _monitor_trades(self):
        while self._running:
            try:
                time.sleep(5)
                if time.time() - self.last_cleanup > 300:
                    with QMutexLocker(self._lock):
                        now = datetime.now()
                        to_remove = [tid for tid, t in self.active_trades.items()
                                    if t.status in [TradeStatus.COMPLETED, TradeStatus.ERROR, TradeStatus.NOT_EXECUTED]
                                    and t.completion_time and (now - t.completion_time).seconds > 300]
                        for tid in to_remove:
                            del self.active_trades[tid]
                        if len(self.trade_history) > MAX_HISTORY_SIZE * 1.5:
                            while len(self.trade_history) > MAX_HISTORY_SIZE:
                                self.trade_history.pop()
                        if len(self.not_executed_trades) > MAX_HISTORY_SIZE:
                            while len(self.not_executed_trades) > MAX_HISTORY_SIZE:
                                self.not_executed_trades.pop()
                    self.last_cleanup = time.time()
            except Exception as e:
                pass
    
    def get_active_trades(self) -> List[dict]:
        with QMutexLocker(self._lock):
            return [trade.to_dict() for trade in self.active_trades.values()]
    
    def get_trade_history(self) -> List[dict]:
        return list(self.trade_history)
    
    def get_not_executed_trades(self) -> List[dict]:
        return list(self.not_executed_trades)
    
    def get_net_profit(self) -> Tuple[float, float]:
        if self.initial_balance > 0:
            profit_pct = (self.net_profit / self.initial_balance) * 100
        else:
            profit_pct = 0
        return self.net_profit, profit_pct
    
    def get_stats(self) -> dict:
        history = list(self.trade_history)
        not_executed = list(self.not_executed_trades)
        total = len(history)
        wins = sum(1 for t in history if t.get('result_type') == 'win')
        losses = sum(1 for t in history if t.get('result_type') == 'loss')
        break_even = sum(1 for t in history if t.get('result_type') == 'break_even')
        total_profit = sum(t.get('profit', 0) for t in history)
        winning_trades = [t for t in history if t.get('result_type') == 'win']
        avg_win = sum(t.get('profit', 0) for t in winning_trades) / len(winning_trades) if winning_trades else 0
        losing_trades = [t for t in history if t.get('result_type') == 'loss']
        avg_loss = sum(abs(t.get('profit', 0)) for t in losing_trades) / len(losing_trades) if losing_trades else 0
        martingale_trades = [t for t in history if t.get('martingale_step', 0) > 0]
        martingale_wins = sum(1 for t in martingale_trades if t.get('result_type') == 'win')
        net_profit, profit_pct = self.get_net_profit()
        
        return {
            'total_trades': total,
            'wins': wins,
            'losses': losses,
            'break_even': break_even,
            'win_rate': (wins / total * 100) if total > 0 else 0,
            'total_profit': total_profit,
            'net_profit': net_profit,
            'profit_percentage': profit_pct,
            'active_trades': len(self.active_trades),
            'not_executed_trades': len(not_executed),
            'candle_only_trades': len([t for t in history if t.get('wait_type') == 'wait_candle_only']),
            'full_duration_trades': len([t for t in history if t.get('wait_type') == 'wait_full_duration']),
            'martingale_trades': len(martingale_trades),
            'martingale_wins': martingale_wins,
            'martingale_win_rate': (martingale_wins / len(martingale_trades) * 100) if martingale_trades else 0,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'current_balance': self.current_balance,
            'initial_balance': self.initial_balance,
            'stop_loss_triggered': self.stop_loss_triggered,
            'take_profit_triggered': self.take_profit_triggered
        }
    
    def reset_risk(self):
        with QMutexLocker(self._lock):
            self.stop_loss_triggered = False
            self.take_profit_triggered = False
            self.initial_balance = self.current_balance
            self.net_profit = 0.0
        self.log_signal.emit("✅ Risk reset. Trading resumed.")
        self.sound_signal.emit("reset")
    
    def stop(self):
        self._running = False
        if hasattr(self, '_update_timer'):
            self._update_timer.stop()
        if hasattr(self, 'retry_timer'):
            self.retry_timer.stop()
        with QMutexLocker(self._lock):
            self.active_trades.clear()
            self.trade_history.clear()
            self.not_executed_trades.clear()
            self.pending_martingale.clear()
            self.failed_trades_queue.clear()

class ConnectThread(QThread):
    finished = pyqtSignal(bool, str, object)
    progress = pyqtSignal(str)
    
    def __init__(self, email, password, account_mode):
        super().__init__()
        self.email = email
        self.password = password
        self.account_mode = account_mode
        self.client = None
        
    def run(self):
        try:
            self.progress.emit("Connecting...")
            self.client = Quotex(email=self.email, password=self.password, lang="en")
            import random
            time.sleep(random.uniform(1, 2))
            check, reason = AsyncHelper.run_async(self.client.connect(), timeout=20)
            
            if check:
                if hasattr(self.client, 'change_account'):
                    self.progress.emit(f"Setting account...")
                    AsyncHelper.run_async(self.client.change_account(self.account_mode), timeout=10)
                balance = AsyncHelper.run_async(self.client.get_balance(), timeout=10)
                if balance is None:
                    self.finished.emit(False, "Failed to get balance", None)
                    return
                time.sleep(0.5)
                self.finished.emit(True, "Connected", self.client)
            else:
                self.finished.emit(False, reason or "Connection failed", None)
        except Exception as e:
            self.finished.emit(False, str(e), None)
        finally:
            self.quit()

class BalanceThread(QThread):
    finished = pyqtSignal(float, bool)
    
    def __init__(self, client):
        super().__init__()
        self.client = client
        
    def run(self):
        if not self.client:
            self.finished.emit(0.0, False)
            return
        try:
            balance = AsyncHelper.run_async(self.client.get_balance(), timeout=8)
            if balance:
                self.finished.emit(float(balance), True)
                return
        except Exception as e:
            pass
        self.finished.emit(0.0, False)
        self.quit()

class ActivationDialog(QDialog):
    def __init__(self, license_manager, parent=None):
        super().__init__(parent)
        self.license_manager = license_manager
        self.setWindowTitle("License Activation")
        self.setFixedSize(500, 300)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        title = QLabel("🔐 License Activation")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FF9800;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        info = QLabel("Please enter your license key")
        info.setStyleSheet("color: #666666; font-size: 12px;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        key_label = QLabel("License Key:")
        key_label.setStyleSheet("font-weight: bold; color: #E65100;")
        layout.addWidget(key_label)
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("BEAST-XXXX-XXXX-XXXX")
        self.key_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #FFB74D;
                border-radius: 5px;
                font-size: 14px;
                font-family: monospace;
            }
            QLineEdit:focus {
                border: 2px solid #FF9800;
            }
        """)
        layout.addWidget(self.key_input)
        button_layout = QHBoxLayout()
        self.activate_btn = QPushButton("✅ Activate")
        self.activate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.activate_btn.clicked.connect(self.activate)
        button_layout.addWidget(self.activate_btn)
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #f44336; font-size: 12px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        info_text = QLabel("⚠️ License key is one-time use for REAL accounts only.")
        info_text.setStyleSheet("color: #666666; font-size: 10px; font-style: italic;")
        info_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_text)
        layout.addStretch()
        self.setLayout(layout)
    
    def activate(self):
        key = self.key_input.text().strip().upper()
        if not key:
            self.status_label.setText("❌ Please enter license key")
            return
        self.activate_btn.setEnabled(False)
        self.activate_btn.setText("Activating...")
        if self.license_manager.activate_key(key):
            self.status_label.setText("✅ Activation successful!")
            self.status_label.setStyleSheet("color: #4CAF50; font-size: 14px; font-weight: bold;")
            QTimer.singleShot(1500, self.accept)
        else:
            self.status_label.setText("❌ Invalid or expired license key")
            self.activate_btn.setEnabled(True)
            self.activate_btn.setText("✅ Activate")

class PaymentDialog(QDialog):
    def __init__(self, license_manager, parent=None):
        super().__init__(parent)
        self.license_manager = license_manager
        self.setWindowTitle("💳 Buy Subscription - Trading Bot")
        self.setMinimumSize(600, 400)
        self.resize(700, 500)
        self.setMaximumSize(1000, 700)
        self.setSizeGripEnabled(True)
        self.selected_plan = None
        self.payment_txid = ""
        self.image_path = None
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        title = QLabel("💎 Trading Bot Subscription")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FF9800; margin: 5px;")
        title.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title)
        
        plans_group = QGroupBox("📊 Subscription Plans")
        plans_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #FF9800;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 8px;
                font-size: 13px;
            }
        """)
        plans_layout = QGridLayout()
        plans_layout.setSpacing(10)
        plans_layout.setContentsMargins(10, 10, 10, 10)
        
        self.plan_buttons = []
        for i, plan in enumerate(SUBSCRIPTION_PLANS):
            plan_widget = QFrame()
            plan_widget.setFrameStyle(QFrame.Box)
            plan_widget.setLineWidth(2)
            plan_widget.setMinimumHeight(180)
            plan_widget.setStyleSheet("""
                QFrame {
                    background-color: #FFF3E0;
                    border: 2px solid #FF9800;
                    border-radius: 10px;
                    padding: 10px;
                }
                QFrame:hover {
                    background-color: #FFE0B2;
                    border: 2px solid #F57C00;
                }
            """)
            plan_layout = QVBoxLayout(plan_widget)
            plan_layout.setSpacing(5)
            name_label = QLabel(plan["name"])
            name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #E65100;")
            name_label.setAlignment(Qt.AlignCenter)
            plan_layout.addWidget(name_label)
            price_label = QLabel(f"${plan['price']}")
            price_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FF9800;")
            price_label.setAlignment(Qt.AlignCenter)
            plan_layout.addWidget(price_label)
            duration_text = f"{plan['days']} days" if plan['days'] < 365 else "Lifetime"
            duration_label = QLabel(duration_text)
            duration_label.setStyleSheet("font-size: 12px; color: #666666;")
            duration_label.setAlignment(Qt.AlignCenter)
            plan_layout.addWidget(duration_label)
            features_text = ""
            for feature in plan["features"]:
                features_text += f"✅ {feature}\n"
            features_label = QLabel(features_text)
            features_label.setStyleSheet("font-size: 10px; color: #333333; padding: 5px; background-color: white; border-radius: 3px;")
            features_label.setAlignment(Qt.AlignLeft)
            features_label.setWordWrap(True)
            plan_layout.addWidget(features_label)
            select_btn = QPushButton("Select Plan")
            select_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    padding: 8px;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                }
            """)
            select_btn.clicked.connect(lambda checked, idx=i: self.select_plan(idx))
            plan_layout.addWidget(select_btn)
            self.plan_buttons.append(select_btn)
            row = i // 2
            col = i % 2
            plans_layout.addWidget(plan_widget, row, col)
        plans_group.setLayout(plans_layout)
        content_layout.addWidget(plans_group)
        
        payment_group = QGroupBox("💳 Payment Details")
        payment_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #FF9800;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 8px;
                font-size: 13px;
            }
        """)
        payment_layout = QGridLayout()
        payment_layout.setVerticalSpacing(8)
        payment_layout.setHorizontalSpacing(10)
        payment_layout.setContentsMargins(15, 15, 15, 15)
        
        wallet_label = QLabel("Wallet Address (TRON):")
        wallet_label.setStyleSheet("font-weight: bold; color: #E65100; font-size: 12px;")
        payment_layout.addWidget(wallet_label, 0, 0)
        wallet_address = QLineEdit(PAYMENT_WALLET)
        wallet_address.setReadOnly(True)
        wallet_address.setStyleSheet("background-color: #FFF3E0; font-family: monospace; font-size: 11px; padding: 8px; border-radius: 4px;")
        payment_layout.addWidget(wallet_address, 0, 1)
        copy_wallet_btn = QPushButton("📋 Copy")
        copy_wallet_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        copy_wallet_btn.clicked.connect(lambda: self.copy_to_clipboard(PAYMENT_WALLET))
        payment_layout.addWidget(copy_wallet_btn, 0, 2)
        
        network_label = QLabel("Network:")
        network_label.setStyleSheet("font-weight: bold; color: #E65100; font-size: 12px;")
        payment_layout.addWidget(network_label, 1, 0)
        network_value = QLabel(PAYMENT_NETWORK)
        network_value.setStyleSheet("color: #FF9800; font-weight: bold; font-size: 12px;")
        payment_layout.addWidget(network_value, 1, 1, 1, 2)
        
        selected_plan_label = QLabel("Selected Plan:")
        selected_plan_label.setStyleSheet("font-weight: bold; color: #E65100; font-size: 12px;")
        payment_layout.addWidget(selected_plan_label, 2, 0)
        self.selected_plan_display = QLabel("No plan selected")
        self.selected_plan_display.setStyleSheet("color: #666666; font-size: 12px;")
        payment_layout.addWidget(self.selected_plan_display, 2, 1, 1, 2)
        
        amount_label = QLabel("Amount:")
        amount_label.setStyleSheet("font-weight: bold; color: #E65100; font-size: 12px;")
        payment_layout.addWidget(amount_label, 3, 0)
        self.amount_display = QLabel("$0")
        self.amount_display.setStyleSheet("color: #FF9800; font-size: 16px; font-weight: bold;")
        payment_layout.addWidget(self.amount_display, 3, 1, 1, 2)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #FFB74D;")
        payment_layout.addWidget(line, 4, 0, 1, 3)
        
        txid_label = QLabel("Transaction ID (TXID):")
        txid_label.setStyleSheet("font-weight: bold; color: #E65100; font-size: 12px;")
        payment_layout.addWidget(txid_label, 5, 0)
        self.txid_input = QLineEdit()
        self.txid_input.setPlaceholderText("Enter TXID from your wallet")
        self.txid_input.setStyleSheet("padding: 8px; border: 1px solid #FFB74D; border-radius: 4px; font-size: 12px;")
        self.txid_input.textChanged.connect(self.check_form_complete)
        payment_layout.addWidget(self.txid_input, 5, 1, 1, 2)
        
        email_label = QLabel("Your Email Address:")
        email_label.setStyleSheet("font-weight: bold; color: #E65100; font-size: 12px;")
        payment_layout.addWidget(email_label, 6, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email to receive the license key")
        self.email_input.setStyleSheet("padding: 8px; border: 1px solid #FFB74D; border-radius: 4px; font-size: 12px;")
        self.email_input.textChanged.connect(self.check_form_complete)
        payment_layout.addWidget(self.email_input, 6, 1, 1, 2)
        
        image_label = QLabel("Payment Screenshot:")
        image_label.setStyleSheet("font-weight: bold; color: #E65100; font-size: 12px;")
        payment_layout.addWidget(image_label, 7, 0)
        image_layout = QHBoxLayout()
        self.image_path_display = QLabel("No image selected")
        self.image_path_display.setStyleSheet("color: #666666; background-color: white; padding: 8px; border: 1px solid #FFB74D; border-radius: 4px; font-size: 11px;")
        image_layout.addWidget(self.image_path_display, 1)
        self.select_image_btn = QPushButton("📷 Choose Image")
        self.select_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.select_image_btn.clicked.connect(self.select_image)
        image_layout.addWidget(self.select_image_btn)
        payment_layout.addLayout(image_layout, 7, 1, 1, 2)
        
        telegram_layout = QHBoxLayout()
        telegram_layout.setSpacing(15)
        telegram_label = QLabel("📱 Support:")
        telegram_label.setStyleSheet("font-weight: bold; color: #E65100; font-size: 12px;")
        telegram_layout.addWidget(telegram_label)
        dev_link = QLabel(f'<a href="{TELEGRAM_DEV}" style="color: #FF9800; text-decoration: none; font-size: 12px;">Developer</a>')
        dev_link.setOpenExternalLinks(True)
        telegram_layout.addWidget(dev_link)
        group_link = QLabel(f'<a href="{TELEGRAM_GROUP}" style="color: #FF9800; text-decoration: none; font-size: 12px;">Support Group</a>')
        group_link.setOpenExternalLinks(True)
        telegram_layout.addWidget(group_link)
        channel_link = QLabel(f'<a href="{TELEGRAM_CHANNEL}" style="color: #FF9800; text-decoration: none; font-size: 12px;">Signals Channel</a>')
        channel_link.setOpenExternalLinks(True)
        telegram_layout.addWidget(channel_link)
        telegram_layout.addStretch()
        payment_layout.addLayout(telegram_layout, 8, 0, 1, 3)
        
        instructions = QLabel(
            "📌 After payment, send the screenshot and TXID. The license key will be sent to your email within 24 hours.\n"
            "⚠️ License required ONLY for REAL accounts."
        )
        instructions.setStyleSheet("color: #FF9800; font-size: 11px; font-style: italic; padding: 8px; background-color: #FFF3E0; border-radius: 4px;")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setWordWrap(True)
        payment_layout.addWidget(instructions, 9, 0, 1, 3)
        
        payment_group.setLayout(payment_layout)
        content_layout.addWidget(payment_group)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.send_btn = QPushButton("📨 Submit Payment Request")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.send_btn.clicked.connect(self.send_payment_request)
        self.send_btn.setEnabled(False)
        button_layout.addWidget(self.send_btn)
        
        cancel_btn = QPushButton("❌ Close")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        content_layout.addLayout(button_layout)
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
    
    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, "✅ Copied", "Wallet address copied to clipboard")
    
    def select_plan(self, index):
        self.selected_plan = SUBSCRIPTION_PLANS[index]
        self.selected_plan_display.setText(f"{self.selected_plan['name']} - {self.selected_plan['days']} days")
        self.amount_display.setText(f"${self.selected_plan['price']}")
        for i, btn in enumerate(self.plan_buttons):
            if i == index:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        padding: 8px;
                        border: none;
                        border-radius: 4px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FF9800;
                        color: white;
                        padding: 8px;
                        border: none;
                        border-radius: 4px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #F57C00;
                    }
                """)
        self.check_form_complete()
    
    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Payment Screenshot", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        )
        if file_path:
            self.image_path = file_path
            self.image_path_display.setText(os.path.basename(file_path))
            self.check_form_complete()
    
    def check_form_complete(self):
        if (self.selected_plan and 
            self.txid_input.text().strip() and 
            self.email_input.text().strip() and 
            hasattr(self, 'image_path') and self.image_path):
            self.send_btn.setEnabled(True)
        else:
            self.send_btn.setEnabled(False)
    
    def send_payment_request(self):
        txid = self.txid_input.text().strip()
        email = self.email_input.text().strip()
        if not txid or not email:
            QMessageBox.warning(self, "❌ Error", "Please enter TXID and email")
            return
        if not hasattr(self, 'image_path') or not self.image_path:
            QMessageBox.warning(self, "❌ Error", "Please select payment screenshot")
            return
        
        success = self.license_manager.process_payment_request(
            email=email,
            plan_name=self.selected_plan['name'],
            amount=self.selected_plan['price'],
            txid=txid,
            image_path=self.image_path
        )
        
        if success:
            summary = f"""
            🎯 Payment Request Submitted Successfully!
            ======================================
            📋 Plan: {self.selected_plan['name']}
            💰 Amount: ${self.selected_plan['price']}
            📧 Your Email: {email}
            🔗 TXID: {txid}
            📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            ✅ The admin has been notified and will verify your payment.
            📧 License key will be sent to your email within 24 hours.
            ⚠️ License required ONLY for REAL accounts.
            Thank you for your purchase!
            """
            QMessageBox.information(self, "✅ Payment Request Submitted", summary)
            self.accept()
        else:
            QMessageBox.warning(self, "❌ Error", "Failed to submit payment request. Please try again or contact support.")

class OrangePushButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #EF6C00;
            }
            QPushButton:disabled {
                background-color: #FFB74D;
                color: #FFF3E0;
            }
        """)

class OrangeGroupBox(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #FF9800;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 8px;
                background-color: #FFF3E0;
                color: #E65100;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
                color: #FF9800;
            }
        """)

class SwitchAccountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔄 Switch Account")
        self.setMinimumSize(400, 300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        title = QLabel("🔄 Enter New Account Details")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FF9800;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        info = QLabel("Please enter the credentials for the new Quotex account.")
        info.setStyleSheet("color: #666666;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        form_widget = QWidget()
        form_layout = QGridLayout(form_widget)
        form_layout.setVerticalSpacing(12)
        form_layout.setHorizontalSpacing(10)
        
        email_label = QLabel("📧 Email:")
        email_label.setStyleSheet("font-weight: bold; color: #E65100;")
        form_layout.addWidget(email_label, 0, 0)
        self.new_email_input = QLineEdit()
        self.new_email_input.setPlaceholderText("your@email.com")
        self.new_email_input.setStyleSheet("padding: 8px; border: 1px solid #FFB74D; border-radius: 4px;")
        form_layout.addWidget(self.new_email_input, 0, 1)
        
        password_label = QLabel("🔑 Password:")
        password_label.setStyleSheet("font-weight: bold; color: #E65100;")
        form_layout.addWidget(password_label, 1, 0)
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setPlaceholderText("********")
        self.new_password_input.setStyleSheet("padding: 8px; border: 1px solid #FFB74D; border-radius: 4px;")
        form_layout.addWidget(self.new_password_input, 1, 1)
        
        account_label = QLabel("📊 Account Type:")
        account_label.setStyleSheet("font-weight: bold; color: #E65100;")
        form_layout.addWidget(account_label, 2, 0)
        self.new_account_combo = QComboBox()
        self.new_account_combo.addItems(["PRACTICE", "REAL"])
        self.new_account_combo.setStyleSheet("padding: 8px; border: 1px solid #FFB74D; border-radius: 4px;")
        form_layout.addWidget(self.new_account_combo, 2, 1)
        
        layout.addWidget(form_widget)
        
        button_layout = QHBoxLayout()
        self.switch_btn = QPushButton("🔄 Switch Account")
        self.switch_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.switch_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.switch_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        self.setLayout(layout)
        
    def get_new_credentials(self):
        return {
            'email': self.new_email_input.text().strip(),
            'password': self.new_password_input.text().strip(),
            'account_mode': self.new_account_combo.currentText().lower()
        }

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.enabled = True
        
    def play(self, sound_type):
        if not self.enabled:
            return
        try:
            if sound_type in ["trade", "win", "loss", "stop_loss", "take_profit", "reset", "blocked"]:
                QApplication.beep()
        except:
            pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = None
        self.connected = False
        self.file_watcher_thread = None
        self.balance = 0.0
        self.trade_manager = None
        self.available_assets = []
        self.auto_relogin_thread = None
        self.last_relogin_time = None
        self.relogin_count = 0
        self.relogin_failures = 0
        self.balance_timer = None
        self.connect_thread = None
        self.balance_thread = None
        self.assets_loader = None
        self._update_ui_timer = None
        self.sound_manager = SoundManager()
        self.connection_manager = None
        self.signal_file_path = None
        
        self.sound_enabled = True
        self.current_language = 'en'
        
        self.license_manager = SupabaseLicenseManager()
        self.license_check_timer = QTimer()
        self.license_check_timer.timeout.connect(self.check_license_status)
        self.license_check_timer.start(1000)
        
        self.martingale_settings = {
            'enabled': False,
            'martingale_type': MartingaleType.DISABLED,
            'max_steps': 5
        }
        
        self.global_stop_loss = 0.0
        self.global_take_profit = 0.0
        
        self.memory_manager = MemoryManager()
        self.thread_manager = ThreadManager()
        self.mt4_reconnect_thread = None
        
        self.watchdog_timer = QTimer()
        self.watchdog_timer.timeout.connect(self.check_bot_health)
        self.watchdog_timer.start(30000)
        self.last_heartbeat = time.time()
        
        self.memory_cleanup_timer = QTimer()
        self.memory_cleanup_timer.timeout.connect(self.cleanup_memory)
        self.memory_cleanup_timer.start(MEMORY_CLEANUP_INTERVAL * 1000)
        
        self.load_config()
        self.setup_ui()
        self.apply_orange_theme()
        
        if not self.license_manager.is_valid:
            QTimer.singleShot(1000, self.show_activation_dialog)
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_active_trades_list)
        self.update_timer.start(200)
        
        self.relogin_display_timer = QTimer()
        self.relogin_display_timer.timeout.connect(self.update_relogin_display)
        self.relogin_display_timer.start(1000)
        
        self.session_refresh_timer = QTimer()
        self.session_refresh_timer.timeout.connect(self.refresh_session)
        self.session_refresh_timer.start(600000)
        
        self.license_timer = QTimer()
        self.license_timer.timeout.connect(self.update_license_display)
        self.license_timer.start(1000)
        
        self.start_file_watcher()
        self.start_mt4_reconnect()
    
    def tr(self, key):
        return LANGUAGES[self.current_language].get(key, key)
    
    def start_file_watcher(self):
        """تشغيل مراقب الملفات لقراءة الإشارات"""
        self.file_watcher_thread = FileWatcherThread(self.signal_file_path)
        self.file_watcher_thread.signal_received.connect(self.on_trade_signal)
        self.file_watcher_thread.log_signal.connect(self.log_message)
        self.file_watcher_thread.start()
        self.log_message(self.tr('file_watcher_started').format(
            path=self.file_watcher_thread.file_path if self.file_watcher_thread.file_path else "Searching..."
        ))
    
    def start_mt4_reconnect(self):
        self.mt4_reconnect_thread = MT4ReconnectThread()
        self.mt4_reconnect_thread.log_signal.connect(self.log_message)
        self.mt4_reconnect_thread.start()
        self.log_message("🔄 MT4 file check enabled (every 5 minutes)")
    
    def check_bot_health(self):
        try:
            current_time = time.time()
            try:
                self.update_status_bar()
                self.last_heartbeat = current_time
            except:
                pass
            if current_time - self.last_heartbeat > 60:
                self.log_message(self.tr('bot_frozen'))
                if self.trade_manager:
                    self.trade_manager.stop()
                    self.trade_manager = None
                if self.connection_manager:
                    self.connection_manager.stop()
                if self.auto_relogin_thread:
                    self.auto_relogin_thread.stop()
                if self.client:
                    try:
                        self.client = None
                    except:
                        pass
                QTimer.singleShot(3000, self.reconnect_bot)
        except Exception as e:
            pass
    
    def reconnect_bot(self):
        self.log_message("🔄 Forcing bot restart...")
        if hasattr(self, 'email_input') and hasattr(self, 'password_input'):
            email = self.email_input.text().strip()
            password = self.password_input.text().strip()
            if email and password:
                self.connect_to_quotex()
    
    def cleanup_memory(self):
        try:
            gc.collect()
            if hasattr(self, 'log_area') and self.log_area.document().characterCount() > 50000:
                self.log_area.clear()
                self.log_message("🧹 Log cleared")
        except Exception as e:
            pass
    
    def disconnect_from_quotex(self):
        self.log_message(self.tr('disconnecting'))
        self.connected = False
        
        if self.trade_manager:
            self.trade_manager.stop()
            self.trade_manager = None
        
        if self.connection_manager:
            self.connection_manager.stop()
            self.connection_manager = None
        
        if self.auto_relogin_thread:
            self.auto_relogin_thread.stop()
            self.auto_relogin_thread = None
        
        if self.balance_timer:
            self.balance_timer.stop()
        
        self.balance = 0.0
        self.balance_label.setText("$0.00")
        
        self.conn_status.setText(self.tr('disconnected'))
        self.conn_status.setStyleSheet("color: #f44336; font-weight: bold;")
        self.connect_btn.setText(self.tr('connect'))
        self.refresh_balance_btn.setEnabled(False)
        self.refresh_assets_btn.setEnabled(False)
        self.manual_call_btn.setEnabled(False)
        self.manual_put_btn.setEnabled(False)
        
        if self.client:
            try:
                self.client = None
            except:
                pass
    
    def switch_account(self):
        if not self.connected:
            self.log_message("⚠️ Please connect to an account first before switching.")
            return
            
        dialog = SwitchAccountDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_creds = dialog.get_new_credentials()
            
            if not new_creds['email'] or not new_creds['password']:
                self.log_message("❌ Please enter both email and password for the new account.")
                return
            
            self.log_message(self.tr('switching_account').format(email=new_creds['email']))
            
            self.disconnect_from_quotex()
            
            self.email_input.setText(new_creds['email'])
            self.password_input.setText(new_creds['password'])
            
            account_text = self.tr('practice') if new_creds['account_mode'] == 'practice' else self.tr('real')
            index = self.account_combo.findText(account_text)
            if index >= 0:
                self.account_combo.setCurrentIndex(index)
            
            self.license_manager.activated_key = None
            self.license_manager.is_valid = False
            self.license_manager.remaining_seconds = 0
            
            self.connect_to_quotex()
    
    def update_ui_language(self):
        self.setWindowTitle(self.tr('app_title'))
        self.email_label.setText(self.tr('email'))
        self.password_label.setText(self.tr('password'))
        self.account_label.setText(self.tr('account'))
        self.connect_btn.setText(self.tr('connect'))
        self.switch_account_btn.setText(self.tr('switch_account'))
        self.account_combo.setItemText(0, self.tr('practice'))
        self.account_combo.setItemText(1, self.tr('real'))
        self.assets_group.setTitle(self.tr('assets'))
        self.refresh_assets_btn.setText(self.tr('refresh'))
        self.auto_trade_check.setText(self.tr('auto_trade'))
        self.manual_call_btn.setText(self.tr('call'))
        self.manual_put_btn.setText(self.tr('put'))
        self.martingale_status_group.setTitle(self.tr('martingale'))
        self.martingale_status_label_text.setText(self.tr('martingale_status'))
        self.martingale_type_label_text.setText(self.tr('martingale_type'))
        self.martingale_pending_label_text.setText(self.tr('martingale_pending'))
        self.log_group.setTitle(self.tr('log'))
        self.tabs.setTabText(0, self.tr('active_trades'))
        self.tabs.setTabText(1, self.tr('not_executed'))
        self.tabs.setTabText(2, self.tr('history'))
        self.tabs.setTabText(3, self.tr('stats'))
        self.tabs.setTabText(4, self.tr('payment'))
        self.tabs.setTabText(5, self.tr('settings'))
        self.stats_active_label.setText(self.tr('active_trades') + ':')
        self.stats_total_label.setText(self.tr('total_trades') + ':')
        self.stats_wins_label.setText(self.tr('wins') + ':')
        self.stats_losses_label.setText(self.tr('losses') + ':')
        self.stats_break_even_label.setText(self.tr('break_even') + ':')
        self.stats_win_rate_label.setText(self.tr('win_rate') + ':')
        self.stats_total_pl_label.setText(self.tr('total_pl') + ':')
        self.stats_net_profit_label.setText(self.tr('net_profit') + ':')
        self.stats_avg_win_label.setText(self.tr('avg_win') + ':')
        self.stats_avg_loss_label.setText(self.tr('avg_loss') + ':')
        self.stats_not_executed_label.setText(self.tr('not_executed_count') + ':')
        self.stats_martingale_trades_label.setText(self.tr('martingale_trades') + ':')
        self.stats_martingale_wins_label.setText(self.tr('martingale_wins') + ':')
        self.stats_risk_label.setText(self.tr('risk_status') + ':')
        self.refresh_stats_btn.setText(self.tr('refresh_stats'))
        self.reset_risk_btn.setText(self.tr('reset_risk'))
        self.clear_history_btn.setText(self.tr('clear_history'))
        self.clear_not_executed_btn.setText(self.tr('clear_not_executed'))
        self.save_settings_btn.setText(self.tr('save_settings'))
        self.lang_btn.setText(self.tr('language') + (' 🇬🇧' if self.current_language == 'en' else ' 🇸🇦'))
    
    def change_language(self):
        if self.current_language == 'en':
            self.current_language = 'ar'
        else:
            self.current_language = 'en'
        self.update_ui_language()
        self.save_config()
        self.log_message(f"🌐 Language changed to {'Arabic' if self.current_language == 'ar' else 'English'}")
    
    def apply_orange_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #FFF3E0; }
            QTabWidget::pane { border: 2px solid #FF9800; border-radius: 6px; background-color: white; }
            QTabBar::tab { background-color: #FFE0B2; color: #E65100; padding: 8px 16px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; }
            QTabBar::tab:selected { background-color: #FF9800; color: white; }
            QTabBar::tab:hover:!selected { background-color: #FFB74D; }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { padding: 5px; border: 1px solid #FFB74D; border-radius: 3px; background-color: white; color: #333333; }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus { border: 2px solid #FF9800; }
            QTextEdit { border: 1px solid #FFB74D; border-radius: 3px; font-family: Consolas; font-size: 11px; background-color: white; color: #333333; }
            QLabel { color: #E65100; }
            QTableWidget { background-color: white; color: #333333; gridline-color: #FFE0B2; selection-background-color: #FFF3E0; font-size: 11px; }
            QHeaderView::section { background-color: #FFE0B2; color: #E65100; padding: 6px; border: 1px solid #FFB74D; font-weight: bold; font-size: 11px; }
            QListWidget { background-color: white; color: #333333; border: 1px solid #FFB74D; border-radius: 3px; font-size: 11px; }
            QListWidget::item { padding: 6px; border-bottom: 1px solid #FFE0B2; }
            QListWidget::item:selected { background-color: #FFF3E0; color: #E65100; }
            QComboBox QAbstractItemView { background-color: white; color: #333333; selection-background-color: #FFF3E0; selection-color: #E65100; border: 1px solid #FFB74D; }
            QCheckBox { color: #E65100; }
            QCheckBox::indicator:unchecked { border: 2px solid #FFB74D; background-color: white; }
            QCheckBox::indicator:checked { border: 2px solid #FF9800; background-color: #FF9800; }
            QStatusBar { background-color: #FFE0B2; color: #E65100; border-top: 1px solid #FF9800; }
            QScrollBar:vertical { border: none; background-color: #FFE0B2; width: 8px; border-radius: 4px; }
            QScrollBar::handle:vertical { background-color: #FFB74D; border-radius: 4px; }
            QScrollBar::handle:vertical:hover { background-color: #FF9800; }
            QProgressBar { border: 1px solid #FFB74D; border-radius: 3px; text-align: center; background-color: white; }
            QProgressBar::chunk { background-color: #FF9800; border-radius: 3px; }
        """)
    
    def check_license_status(self):
        self.license_manager.check_current_license()
        self.update_license_display()
        if not self.license_manager.is_valid:
            if self.trade_manager:
                self.trade_manager.martingale_settings['enabled'] = False
    
    def update_license_display(self):
        if self.license_manager.is_valid:
            remaining = self.license_manager.remaining_seconds
            if remaining > 0:
                days = remaining // 86400
                hours = (remaining % 86400) // 3600
                minutes = (remaining % 3600) // 60
                seconds = remaining % 60
                if days > 0:
                    time_text = f"{days}d {hours:02d}:{minutes:02d}:{seconds:02d}"
                elif hours > 0:
                    time_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                else:
                    time_text = f"{minutes:02d}:{seconds:02d}"
                if days <= 7:
                    color = "#FF9800"
                    warning = "⚠️"
                else:
                    color = "#4CAF50"
                    warning = "✓"
                plan_names = {"basic": "Basic", "standard": "Standard", "premium": "Premium"}
                plan_text = plan_names.get(self.license_manager.plan_type, self.license_manager.plan_type)
                license_text = f"{warning} {plan_text}: {time_text} remaining"
            else:
                color = "#f44336"
                license_text = "⚠️ Expired - Renew now"
        else:
            color = "#f44336"
            license_text = "⚠️ Not activated - Buy now"
        self.license_status_label.setText(license_text)
        self.license_status_label.setStyleSheet(f"color: {color}; font-weight: bold; padding: 0 10px;")
    
    def show_activation_dialog(self):
        dialog = ActivationDialog(self.license_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            self.license_manager.check_current_license()
            self.update_license_display()
            self.log_message("✅ License activated successfully")
    
    def show_payment_dialog(self):
        dialog = PaymentDialog(self.license_manager, self)
        dialog.exec_()
        self.license_manager.check_current_license()
        self.update_license_display()
    
    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                self.saved_config = config
                self.global_stop_loss = config.get('global_stop_loss', 0.0)
                self.global_take_profit = config.get('global_take_profit', 0.0)
                self.current_language = config.get('language', 'en')
                self.signal_file_path = config.get('signal_file_path', None)
                if 'martingale' in config:
                    martingale_config = config['martingale']
                    self.martingale_settings['enabled'] = martingale_config.get('enabled', False)
                    martingale_type_str = martingale_config.get('martingale_type', 'disabled')
                    for mt in MartingaleType:
                        if mt.value == martingale_type_str:
                            self.martingale_settings['martingale_type'] = mt
                            break
                    self.martingale_settings['max_steps'] = martingale_config.get('max_steps', 5)
                if 'sound_enabled' in config:
                    self.sound_enabled = config.get('sound_enabled', True)
                    self.sound_manager.enabled = self.sound_enabled
            else:
                self.saved_config = {}
        except Exception as e:
            self.saved_config = {}
    
    def save_config(self):
        try:
            config = {
                'email': self.email_input.text().strip(),
                'password': self.password_input.text().strip(),
                'account_mode': self.account_combo.currentText(),
                'default_amount': self.settings_default_amount.value(),
                'default_duration': self.settings_default_duration.value(),
                'auto_trade': self.auto_trade_check.isChecked(),
                'enable_auto_relogin': self.enable_auto_relogin.isChecked(),
                'relogin_retries': self.relogin_retries.value(),
                'sound_enabled': self.sound_enabled,
                'global_stop_loss': self.stop_loss_spin.value(),
                'global_take_profit': self.take_profit_spin.value(),
                'language': self.current_language,
                'signal_file_path': self.signal_file_path,
                'martingale': {
                    'enabled': self.martingale_group.isChecked(),
                    'martingale_type': self.martingale_type_combo.currentData().value if hasattr(self, 'martingale_type_combo') else 'disabled',
                    'max_steps': self.martingale_steps.value()
                }
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            pass
    
    def setup_ui(self):
        self.setWindowTitle(self.tr('app_title'))
        self.setMinimumSize(1200, 750)
        self.resize(1300, 750)
        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)
        main.setSpacing(5)
        main.setContentsMargins(8, 8, 8, 8)
        
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #FF9800; border-radius: 6px; padding: 5px;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(8, 4, 8, 4)
        
        title_label = QLabel("🌋 Volcano Profit (FILE MODE)")
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        self.activate_btn_header = QPushButton(self.tr('activate_license'))
        self.activate_btn_header.setStyleSheet("""
            QPushButton { background-color: white; color: #FF9800; border: none; padding: 4px 12px; border-radius: 4px; font-weight: bold; font-size: 11px; }
            QPushButton:hover { background-color: #FFF3E0; }
        """)
        self.activate_btn_header.clicked.connect(self.show_activation_dialog)
        header_layout.addWidget(self.activate_btn_header)
        
        self.buy_btn_header = QPushButton(self.tr('buy_subscription'))
        self.buy_btn_header.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; border: none; padding: 4px 12px; border-radius: 4px; font-weight: bold; font-size: 11px; }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.buy_btn_header.clicked.connect(self.show_payment_dialog)
        header_layout.addWidget(self.buy_btn_header)
        
        self.lang_btn = QPushButton(self.tr('language') + ' 🇬🇧')
        self.lang_btn.setStyleSheet("""
            QPushButton { background-color: white; color: #FF9800; border: none; padding: 4px 12px; border-radius: 4px; font-weight: bold; font-size: 11px; }
            QPushButton:hover { background-color: #FFF3E0; }
        """)
        self.lang_btn.clicked.connect(self.change_language)
        header_layout.addWidget(self.lang_btn)
        
        self.switch_account_btn = QPushButton(self.tr('switch_account'))
        self.switch_account_btn.setStyleSheet("""
            QPushButton { background-color: #2196F3; color: white; border: none; padding: 4px 12px; border-radius: 4px; font-weight: bold; font-size: 11px; }
            QPushButton:hover { background-color: #1976D2; }
        """)
        self.switch_account_btn.clicked.connect(self.switch_account)
        header_layout.addWidget(self.switch_account_btn)
        
        self.sound_btn = QPushButton("🔊 Sound On")
        self.sound_btn.setStyleSheet("""
            QPushButton { background-color: white; color: #FF9800; border: none; padding: 4px 12px; border-radius: 4px; font-weight: bold; font-size: 11px; }
            QPushButton:hover { background-color: #FFF3E0; }
        """)
        self.sound_btn.clicked.connect(self.toggle_sound)
        header_layout.addWidget(self.sound_btn)
        
        header_layout.addStretch()
        
        dev_link = QLabel(f'<a href="{TELEGRAM_DEV}" style="color: white; text-decoration: none;">Developer</a>')
        dev_link.setOpenExternalLinks(True)
        dev_link.setStyleSheet("color: white; font-size: 11px;")
        header_layout.addWidget(dev_link)
        header_layout.addWidget(QLabel("|"))
        group_link = QLabel(f'<a href="{TELEGRAM_GROUP}" style="color: white; text-decoration: none;">Group</a>')
        group_link.setOpenExternalLinks(True)
        group_link.setStyleSheet("color: white; font-size: 11px;")
        header_layout.addWidget(group_link)
        header_layout.addWidget(QLabel("|"))
        channel_link = QLabel(f'<a href="{TELEGRAM_CHANNEL}" style="color: white; text-decoration: none;">Channel</a>')
        channel_link.setOpenExternalLinks(True)
        channel_link.setStyleSheet("color: white; font-size: 11px;")
        header_layout.addWidget(channel_link)
        
        main.addWidget(header_widget)
        
        main_splitter = QSplitter(Qt.Horizontal)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)
        
        conn_group = OrangeGroupBox(self.tr('connect'))
        conn_layout = QGridLayout()
        conn_layout.setVerticalSpacing(3)
        
        self.email_label = QLabel(self.tr('email'))
        conn_layout.addWidget(self.email_label, 0, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your@email.com")
        conn_layout.addWidget(self.email_input, 0, 1)
        
        self.password_label = QLabel(self.tr('password'))
        conn_layout.addWidget(self.password_label, 1, 0)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("********")
        conn_layout.addWidget(self.password_input, 1, 1)
        
        self.account_label = QLabel(self.tr('account'))
        conn_layout.addWidget(self.account_label, 2, 0)
        self.account_combo = QComboBox()
        self.account_combo.addItems([self.tr('practice'), self.tr('real')])
        self.account_combo.currentTextChanged.connect(self.on_account_changed)
        conn_layout.addWidget(self.account_combo, 2, 1)
        
        self.connect_btn = OrangePushButton(self.tr('connect'))
        self.connect_btn.clicked.connect(self.connect_to_quotex)
        conn_layout.addWidget(self.connect_btn, 3, 0)
        
        self.conn_status = QLabel(self.tr('disconnected'))
        self.conn_status.setStyleSheet("color: #f44336; font-weight: bold; font-size: 11px;")
        conn_layout.addWidget(self.conn_status, 3, 1)
        
        balance_text = QLabel(self.tr('balance'))
        conn_layout.addWidget(balance_text, 4, 0)
        self.balance_label = QLabel("$0.00")
        self.balance_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FF9800;")
        conn_layout.addWidget(self.balance_label, 4, 1)
        
        self.refresh_balance_btn = OrangePushButton(self.tr('refresh'))
        self.refresh_balance_btn.clicked.connect(self.fetch_balance)
        self.refresh_balance_btn.setEnabled(False)
        conn_layout.addWidget(self.refresh_balance_btn, 5, 0, 1, 2)
        
        conn_group.setLayout(conn_layout)
        left_layout.addWidget(conn_group)
        
        self.assets_group = OrangeGroupBox(self.tr('assets'))
        assets_layout = QHBoxLayout()
        self.asset_combo = QComboBox()
        self.asset_combo.setEditable(True)
        self.asset_combo.addItem("EURUSD")
        assets_layout.addWidget(self.asset_combo, 1)
        self.refresh_assets_btn = OrangePushButton(self.tr('refresh'))
        self.refresh_assets_btn.clicked.connect(self.load_available_assets)
        self.refresh_assets_btn.setEnabled(False)
        assets_layout.addWidget(self.refresh_assets_btn)
        self.assets_group.setLayout(assets_layout)
        left_layout.addWidget(self.assets_group)
        
        self.auto_trade_check = QCheckBox(self.tr('auto_trade'))
        self.auto_trade_check.setChecked(True)
        self.auto_trade_check.setStyleSheet("font-weight: bold; color: #FF9800; font-size: 11px;")
        left_layout.addWidget(self.auto_trade_check)
        
        manual_layout = QHBoxLayout()
        self.manual_call_btn = OrangePushButton(self.tr('call'))
        self.manual_call_btn.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; border: none; padding: 10px; border-radius: 4px; font-size: 13px; font-weight: bold; }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.manual_call_btn.clicked.connect(lambda: self.manual_trade("call"))
        self.manual_call_btn.setEnabled(False)
        manual_layout.addWidget(self.manual_call_btn)
        
        self.manual_put_btn = OrangePushButton(self.tr('put'))
        self.manual_put_btn.setStyleSheet("""
            QPushButton { background-color: #f44336; color: white; border: none; padding: 10px; border-radius: 4px; font-size: 13px; font-weight: bold; }
            QPushButton:hover { background-color: #da190b; }
        """)
        self.manual_put_btn.clicked.connect(lambda: self.manual_trade("put"))
        self.manual_put_btn.setEnabled(False)
        manual_layout.addWidget(self.manual_put_btn)
        left_layout.addLayout(manual_layout)
        
        self.martingale_status_group = OrangeGroupBox(self.tr('martingale'))
        status_layout = QGridLayout()
        status_layout.setVerticalSpacing(2)
        
        self.martingale_status_label_text = QLabel(self.tr('martingale_status'))
        status_layout.addWidget(self.martingale_status_label_text, 0, 0)
        self.martingale_status_label = QLabel(self.tr('disabled'))
        self.martingale_status_label.setStyleSheet("color: #f44336; font-weight: bold; font-size: 11px;")
        status_layout.addWidget(self.martingale_status_label, 0, 1)
        
        self.martingale_type_label_text = QLabel(self.tr('martingale_type'))
        status_layout.addWidget(self.martingale_type_label_text, 1, 0)
        self.martingale_type_label = QLabel("-")
        self.martingale_type_label.setStyleSheet("color: #FF9800; font-size: 11px;")
        status_layout.addWidget(self.martingale_type_label, 1, 1)
        
        self.martingale_pending_label_text = QLabel(self.tr('martingale_pending'))
        status_layout.addWidget(self.martingale_pending_label_text, 2, 0)
        self.martingale_pending_label = QLabel("0")
        self.martingale_pending_label.setStyleSheet("color: #FF9800; font-weight: bold; font-size: 11px;")
        status_layout.addWidget(self.martingale_pending_label, 2, 1)
        
        self.martingale_status_group.setLayout(status_layout)
        left_layout.addWidget(self.martingale_status_group)
        
        self.log_group = OrangeGroupBox(self.tr('log'))
        log_layout = QVBoxLayout()
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(120)
        self.log_area.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_area)
        self.log_group.setLayout(log_layout)
        left_layout.addWidget(self.log_group)
        
        left_layout.addStretch()
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)
        
        self.tabs = QTabWidget()
        
        active_tab = QWidget()
        active_layout = QVBoxLayout(active_tab)
        active_group = OrangeGroupBox(self.tr('active_trades'))
        active_group_layout = QVBoxLayout()
        self.active_trades_list = QListWidget()
        self.active_trades_list.setMinimumHeight(200)
        active_group_layout.addWidget(self.active_trades_list)
        active_group.setLayout(active_group_layout)
        active_layout.addWidget(active_group)
        self.tabs.addTab(active_tab, self.tr('active_trades'))
        
        not_executed_tab = QWidget()
        not_executed_layout = QVBoxLayout(not_executed_tab)
        not_executed_group = OrangeGroupBox(self.tr('not_executed'))
        not_executed_group_layout = QVBoxLayout()
        self.not_executed_table = QTableWidget()
        self.not_executed_table.setColumnCount(6)
        self.not_executed_table.setHorizontalHeaderLabels(["Time", "ID", "Symbol", "Dir", "Amount", "Error Reason"])
        header = self.not_executed_table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        self.not_executed_table.setWordWrap(True)
        self.not_executed_table.verticalHeader().setDefaultSectionSize(30)
        self.not_executed_table.setAlternatingRowColors(True)
        self.not_executed_table.setMinimumHeight(200)
        not_executed_group_layout.addWidget(self.not_executed_table)
        self.clear_not_executed_btn = OrangePushButton(self.tr('clear_not_executed'))
        self.clear_not_executed_btn.clicked.connect(self.clear_not_executed)
        not_executed_group_layout.addWidget(self.clear_not_executed_btn)
        not_executed_group.setLayout(not_executed_group_layout)
        not_executed_layout.addWidget(not_executed_group)
        self.tabs.addTab(not_executed_tab, "⚠️ " + self.tr('not_executed'))
        
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        history_group = OrangeGroupBox(self.tr('history'))
        history_group_layout = QVBoxLayout()
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(11)
        self.history_table.setHorizontalHeaderLabels(["Time", "ID", "Symbol", "Dir", "Amount", "Result", "Profit", "ROI%", "Net P/L", "M-Step", "Status"])
        header = self.history_table.horizontalHeader()
        for i in range(11):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        self.history_table.setWordWrap(True)
        self.history_table.verticalHeader().setDefaultSectionSize(30)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setMinimumHeight(300)
        history_group_layout.addWidget(self.history_table)
        history_buttons = QHBoxLayout()
        self.clear_history_btn = OrangePushButton(self.tr('clear_history'))
        self.clear_history_btn.clicked.connect(self.clear_history)
        refresh_btn = OrangePushButton(self.tr('refresh'))
        refresh_btn.clicked.connect(self.refresh_history)
        history_buttons.addWidget(self.clear_history_btn)
        history_buttons.addWidget(refresh_btn)
        history_buttons.addStretch()
        history_group_layout.addLayout(history_buttons)
        history_group.setLayout(history_group_layout)
        history_layout.addWidget(history_group)
        self.tabs.addTab(history_tab, self.tr('history'))
        
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        stats_group = OrangeGroupBox(self.tr('stats'))
        stats_grid = QGridLayout()
        stats_grid.setVerticalSpacing(10)
        stats_grid.setHorizontalSpacing(20)
        
        self.stats_active_label = QLabel(self.tr('active_trades') + ':')
        stats_grid.addWidget(self.stats_active_label, 0, 0)
        self.stats_active_trades = QLabel("0")
        self.stats_active_trades.setStyleSheet("font-weight: bold; color: #FF9800; font-size: 13px;")
        stats_grid.addWidget(self.stats_active_trades, 0, 1)
        
        self.stats_total_label = QLabel(self.tr('total_trades') + ':')
        stats_grid.addWidget(self.stats_total_label, 0, 2)
        self.stats_total_trades = QLabel("0")
        self.stats_total_trades.setStyleSheet("font-weight: bold; color: #FF9800; font-size: 13px;")
        stats_grid.addWidget(self.stats_total_trades, 0, 3)
        
        self.stats_wins_label = QLabel(self.tr('wins') + ':')
        stats_grid.addWidget(self.stats_wins_label, 1, 0)
        self.stats_wins = QLabel("0")
        self.stats_wins.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 13px;")
        stats_grid.addWidget(self.stats_wins, 1, 1)
        
        self.stats_losses_label = QLabel(self.tr('losses') + ':')
        stats_grid.addWidget(self.stats_losses_label, 1, 2)
        self.stats_losses = QLabel("0")
        self.stats_losses.setStyleSheet("color: #f44336; font-weight: bold; font-size: 13px;")
        stats_grid.addWidget(self.stats_losses, 1, 3)
        
        self.stats_break_even_label = QLabel(self.tr('break_even') + ':')
        stats_grid.addWidget(self.stats_break_even_label, 2, 0)
        self.stats_break_even = QLabel("0")
        self.stats_break_even.setStyleSheet("color: #FF9800; font-weight: bold; font-size: 13px;")
        stats_grid.addWidget(self.stats_break_even, 2, 1)
        
        self.stats_win_rate_label = QLabel(self.tr('win_rate') + ':')
        stats_grid.addWidget(self.stats_win_rate_label, 2, 2)
        self.stats_win_rate = QLabel("0%")
        self.stats_win_rate.setStyleSheet("font-weight: bold; color: #FF9800; font-size: 14px;")
        stats_grid.addWidget(self.stats_win_rate, 2, 3)
        
        self.stats_total_pl_label = QLabel(self.tr('total_pl') + ':')
        stats_grid.addWidget(self.stats_total_pl_label, 3, 0)
        self.stats_total_profit = QLabel("$0.00")
        self.stats_total_profit.setStyleSheet("font-weight: bold; font-size: 14px;")
        stats_grid.addWidget(self.stats_total_profit, 3, 1)
        
        self.stats_net_profit_label = QLabel(self.tr('net_profit') + ':')
        stats_grid.addWidget(self.stats_net_profit_label, 3, 2)
        self.stats_net_profit = QLabel("$0.00 (0%)")
        self.stats_net_profit.setStyleSheet("font-weight: bold; font-size: 14px;")
        stats_grid.addWidget(self.stats_net_profit, 3, 3)
        
        self.stats_avg_win_label = QLabel(self.tr('avg_win') + ':')
        stats_grid.addWidget(self.stats_avg_win_label, 4, 0)
        self.stats_avg_win = QLabel("$0.00")
        self.stats_avg_win.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 12px;")
        stats_grid.addWidget(self.stats_avg_win, 4, 1)
        
        self.stats_avg_loss_label = QLabel(self.tr('avg_loss') + ':')
        stats_grid.addWidget(self.stats_avg_loss_label, 4, 2)
        self.stats_avg_loss = QLabel("$0.00")
        self.stats_avg_loss.setStyleSheet("color: #f44336; font-weight: bold; font-size: 12px;")
        stats_grid.addWidget(self.stats_avg_loss, 4, 3)
        
        self.stats_not_executed_label = QLabel(self.tr('not_executed_count') + ':')
        stats_grid.addWidget(self.stats_not_executed_label, 5, 0)
        self.stats_not_executed = QLabel("0")
        self.stats_not_executed.setStyleSheet("color: #FF9800; font-weight: bold; font-size: 12px;")
        stats_grid.addWidget(self.stats_not_executed, 5, 1)
        
        self.stats_martingale_trades_label = QLabel(self.tr('martingale_trades') + ':')
        stats_grid.addWidget(self.stats_martingale_trades_label, 5, 2)
        self.stats_martingale_trades = QLabel("0")
        self.stats_martingale_trades.setStyleSheet("color: #FF9800; font-weight: bold; font-size: 12px;")
        stats_grid.addWidget(self.stats_martingale_trades, 5, 3)
        
        self.stats_martingale_wins_label = QLabel(self.tr('martingale_wins') + ':')
        stats_grid.addWidget(self.stats_martingale_wins_label, 6, 0)
        self.stats_martingale_wins = QLabel("0")
        self.stats_martingale_wins.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 12px;")
        stats_grid.addWidget(self.stats_martingale_wins, 6, 1)
        
        self.stats_risk_label = QLabel(self.tr('risk_status') + ':')
        stats_grid.addWidget(self.stats_risk_label, 6, 2)
        self.stats_risk_status = QLabel(self.tr('risk_active'))
        self.stats_risk_status.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 12px;")
        stats_grid.addWidget(self.stats_risk_status, 6, 3)
        
        stats_group.setLayout(stats_grid)
        stats_layout.addWidget(stats_group)
        
        self.refresh_stats_btn = OrangePushButton(self.tr('refresh_stats'))
        self.refresh_stats_btn.clicked.connect(self.update_statistics)
        stats_layout.addWidget(self.refresh_stats_btn)
        
        self.reset_risk_btn = OrangePushButton(self.tr('reset_risk'))
        self.reset_risk_btn.clicked.connect(self.reset_risk)
        stats_layout.addWidget(self.reset_risk_btn)
        
        stats_layout.addStretch()
        self.tabs.addTab(stats_tab, self.tr('stats'))
        
        payment_tab = QWidget()
        payment_layout = QVBoxLayout(payment_tab)
        payment_layout.setSpacing(10)
        
        plans_group = OrangeGroupBox("📊 Subscription Plans")
        plans_layout = QHBoxLayout()
        plans_layout.setSpacing(10)
        for plan in SUBSCRIPTION_PLANS:
            plan_widget = QFrame()
            plan_widget.setFrameStyle(QFrame.Box)
            plan_widget.setLineWidth(2)
            plan_widget.setMinimumHeight(160)
            plan_widget.setStyleSheet("""
                QFrame { background-color: #FFF3E0; border: 2px solid #FF9800; border-radius: 8px; padding: 8px; }
            """)
            plan_inner_layout = QVBoxLayout(plan_widget)
            name_label = QLabel(plan["name"])
            name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #E65100;")
            name_label.setAlignment(Qt.AlignCenter)
            plan_inner_layout.addWidget(name_label)
            price_label = QLabel(f"${plan['price']}")
            price_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FF9800;")
            price_label.setAlignment(Qt.AlignCenter)
            plan_inner_layout.addWidget(price_label)
            duration_text = f"{plan['days']} days"
            duration_label = QLabel(duration_text)
            duration_label.setStyleSheet("font-size: 11px; color: #666666;")
            duration_label.setAlignment(Qt.AlignCenter)
            plan_inner_layout.addWidget(duration_label)
            features_text = ""
            for feature in plan["features"]:
                features_text += f"✅ {feature}\n"
            features_label = QLabel(features_text)
            features_label.setStyleSheet("font-size: 9px; color: #333333; padding: 4px; background-color: white; border-radius: 2px;")
            features_label.setAlignment(Qt.AlignLeft)
            features_label.setWordWrap(True)
            plan_inner_layout.addWidget(features_label)
            plans_layout.addWidget(plan_widget)
        plans_group.setLayout(plans_layout)
        payment_layout.addWidget(plans_group)
        
        payment_info_group = OrangeGroupBox("💳 Payment Information")
        info_layout = QGridLayout()
        info_layout.setVerticalSpacing(8)
        
        info_layout.addWidget(QLabel("Wallet (TRON):"), 0, 0)
        wallet_display = QLineEdit(PAYMENT_WALLET)
        wallet_display.setReadOnly(True)
        wallet_display.setStyleSheet("font-family: monospace; font-size: 11px;")
        info_layout.addWidget(wallet_display, 0, 1)
        copy_wallet_btn = QPushButton("📋 Copy")
        copy_wallet_btn.setStyleSheet("""
            QPushButton { background-color: #FF9800; color: white; padding: 4px 8px; border: none; border-radius: 3px; font-size: 10px; }
        """)
        copy_wallet_btn.clicked.connect(lambda: self.copy_to_clipboard(PAYMENT_WALLET))
        info_layout.addWidget(copy_wallet_btn, 0, 2)
        
        info_layout.addWidget(QLabel("Network:"), 1, 0)
        network_label = QLabel(PAYMENT_NETWORK)
        network_label.setStyleSheet("color: #FF9800; font-weight: bold; font-size: 11px;")
        info_layout.addWidget(network_label, 1, 1, 1, 2)
        
        info_layout.addWidget(QLabel("Admin Email:"), 2, 0)
        admin_email = QLabel(ADMIN_EMAIL)
        admin_email.setStyleSheet("color: #FF9800; font-size: 11px;")
        info_layout.addWidget(admin_email, 2, 1, 1, 2)
        
        instructions = QLabel(
            "📌 To purchase: Send the amount to the wallet above, then submit the form with TXID and screenshot.\n"
            "The activation key will be sent to your email within 24 hours.\n"
            "⚠️ License required ONLY for REAL accounts."
        )
        instructions.setStyleSheet("color: #666666; font-size: 10px; padding: 8px; background-color: #FFF3E0; border-radius: 3px;")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setWordWrap(True)
        info_layout.addWidget(instructions, 3, 0, 1, 3)
        
        payment_info_group.setLayout(info_layout)
        payment_layout.addWidget(payment_info_group)
        
        telegram_group = OrangeGroupBox("📱 Support")
        telegram_layout = QHBoxLayout()
        dev_link_tab = QLabel(f'<a href="{TELEGRAM_DEV}" style="color: #FF9800; font-size: 12px; text-decoration: none;">👨‍💻 Developer</a>')
        dev_link_tab.setOpenExternalLinks(True)
        telegram_layout.addWidget(dev_link_tab)
        group_link_tab = QLabel(f'<a href="{TELEGRAM_GROUP}" style="color: #FF9800; font-size: 12px; text-decoration: none;">👥 Support Group</a>')
        group_link_tab.setOpenExternalLinks(True)
        telegram_layout.addWidget(group_link_tab)
        channel_link_tab = QLabel(f'<a href="{TELEGRAM_CHANNEL}" style="color: #FF9800; font-size: 12px; text-decoration: none;">📢 Signals Channel</a>')
        channel_link_tab.setOpenExternalLinks(True)
        telegram_layout.addWidget(channel_link_tab)
        telegram_layout.addStretch()
        telegram_group.setLayout(telegram_layout)
        payment_layout.addWidget(telegram_group)
        
        buy_btn = QPushButton("💳 Start Purchase")
        buy_btn.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; padding: 10px; border: none; border-radius: 4px; font-weight: bold; font-size: 13px; }
            QPushButton:hover { background-color: #45a049; }
        """)
        buy_btn.clicked.connect(self.show_payment_dialog)
        payment_layout.addWidget(buy_btn)
        
        payment_layout.addStretch()
        self.tabs.addTab(payment_tab, "💳 " + self.tr('payment'))
        
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        trading_group = OrangeGroupBox("TRADING SETTINGS")
        trading_layout = QGridLayout()
        trading_layout.addWidget(QLabel("Default Amount ($):"), 0, 0)
        self.settings_default_amount = QDoubleSpinBox()
        self.settings_default_amount.setRange(1, 10000)
        self.settings_default_amount.setValue(10)
        self.settings_default_amount.setSingleStep(5)
        trading_layout.addWidget(self.settings_default_amount, 0, 1)
        trading_layout.addWidget(QLabel("Duration (min):"), 1, 0)
        self.settings_default_duration = QSpinBox()
        self.settings_default_duration.setRange(1, 5)
        self.settings_default_duration.setValue(1)
        trading_layout.addWidget(self.settings_default_duration, 1, 1)
        trading_group.setLayout(trading_layout)
        settings_layout.addWidget(trading_group)
        
        risk_group = OrangeGroupBox("GLOBAL RISK MANAGEMENT (Based on Net Profit)")
        risk_layout = QGridLayout()
        risk_layout.addWidget(QLabel("Global Stop Loss (%):"), 0, 0)
        self.stop_loss_spin = QDoubleSpinBox()
        self.stop_loss_spin.setRange(0, 100)
        self.stop_loss_spin.setValue(self.global_stop_loss)
        self.stop_loss_spin.setSingleStep(5)
        self.stop_loss_spin.setSuffix("%")
        self.stop_loss_spin.setToolTip("Stops trading when net loss reaches this percentage")
        self.stop_loss_spin.valueChanged.connect(self.on_risk_changed)
        risk_layout.addWidget(self.stop_loss_spin, 0, 1)
        risk_layout.addWidget(QLabel("Global Take Profit (%):"), 1, 0)
        self.take_profit_spin = QDoubleSpinBox()
        self.take_profit_spin.setRange(0, 200)
        self.take_profit_spin.setValue(self.global_take_profit)
        self.take_profit_spin.setSingleStep(10)
        self.take_profit_spin.setSuffix("%")
        self.take_profit_spin.setToolTip("Stops trading when net profit reaches this percentage")
        self.take_profit_spin.valueChanged.connect(self.on_risk_changed)
        risk_layout.addWidget(self.take_profit_spin, 1, 1)
        risk_desc = QLabel(
            "• These limits apply to TOTAL NET PROFIT (all trades combined)\n"
            "• Example: Start with $1000, Stop Loss 20% = Stop at $800 (-$200)\n"
            "• Take Profit 50% = Stop at $1500 (+$500)\n"
            "• Set to 0% to disable\n"
            "• Click 'Reset Risk' to resume trading after limit is reached"
        )
        risk_desc.setStyleSheet("color: #666666; font-size: 10px; padding: 8px; background-color: white; border-radius: 3px;")
        risk_layout.addWidget(risk_desc, 2, 0, 1, 2)
        risk_group.setLayout(risk_layout)
        settings_layout.addWidget(risk_group)
        
        self.martingale_group = QGroupBox("MARTINGALE SYSTEM")
        self.martingale_group.setCheckable(True)
        self.martingale_group.setChecked(self.martingale_settings['enabled'])
        self.martingale_group.toggled.connect(self.on_martingale_toggled)
        self.martingale_group.setStyleSheet("""
            QGroupBox { font-weight: bold; border: 2px solid #FF9800; border-radius: 6px; margin-top: 10px; padding-top: 8px; background-color: #FFF3E0; color: #E65100; font-size: 12px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 8px; color: #FF9800; }
        """)
        martingale_layout = QGridLayout()
        martingale_layout.addWidget(QLabel("Type:"), 0, 0)
        self.martingale_type_combo = QComboBox()
        self.martingale_type_combo.addItem("Disabled", MartingaleType.DISABLED)
        self.martingale_type_combo.addItem("Next Opportunity (Same)", MartingaleType.NEXT_OPPORTUNITY_SAME)
        self.martingale_type_combo.addItem("Next Opportunity (Any)", MartingaleType.NEXT_OPPORTUNITY_ANY)
        current_type = self.martingale_settings['martingale_type']
        for i in range(self.martingale_type_combo.count()):
            if self.martingale_type_combo.itemData(i) == current_type:
                self.martingale_type_combo.setCurrentIndex(i)
                break
        self.martingale_type_combo.currentIndexChanged.connect(self.on_martingale_type_changed)
        martingale_layout.addWidget(self.martingale_type_combo, 0, 1)
        martingale_layout.addWidget(QLabel("Max Steps:"), 1, 0)
        self.martingale_steps = QSpinBox()
        self.martingale_steps.setRange(1, 10)
        self.martingale_steps.setValue(self.martingale_settings['max_steps'])
        martingale_layout.addWidget(self.martingale_steps, 1, 1)
        desc_text = QLabel("• On loss: double the amount on next signal\n• Break-even counts as win (no martingale)")
        desc_text.setStyleSheet("color: #4CAF50; font-size: 10px; padding: 5px; background-color: white; border-radius: 3px; font-weight: bold;")
        martingale_layout.addWidget(desc_text, 2, 0, 1, 2)
        self.martingale_group.setLayout(martingale_layout)
        settings_layout.addWidget(self.martingale_group)
        
        relogin_group = OrangeGroupBox("AUTO RE-LOGIN")
        relogin_layout = QGridLayout()
        self.enable_auto_relogin = QCheckBox("Enable (30 min)")
        self.enable_auto_relogin.setChecked(True)
        relogin_layout.addWidget(self.enable_auto_relogin, 0, 0, 1, 2)
        relogin_layout.addWidget(QLabel("Retries:"), 1, 0)
        self.relogin_retries = QSpinBox()
        self.relogin_retries.setRange(1, 10)
        self.relogin_retries.setValue(3)
        relogin_layout.addWidget(self.relogin_retries, 1, 1)
        stats_widget = QWidget()
        stats_layout_h = QHBoxLayout(stats_widget)
        stats_layout_h.setContentsMargins(0, 0, 0, 0)
        stats_layout_h.addWidget(QLabel("Count:"))
        self.relogin_count_label = QLabel("0")
        stats_layout_h.addWidget(self.relogin_count_label)
        stats_layout_h.addWidget(QLabel("Next:"))
        self.next_relogin_label = QLabel("--:--")
        stats_layout_h.addWidget(self.next_relogin_label)
        relogin_layout.addWidget(stats_widget, 2, 0, 1, 2)
        relogin_group.setLayout(relogin_layout)
        settings_layout.addWidget(relogin_group)
        
        self.save_settings_btn = OrangePushButton(self.tr('save_settings'))
        self.save_settings_btn.clicked.connect(self.save_config)
        settings_layout.addWidget(self.save_settings_btn)
        settings_layout.addStretch()
        self.tabs.addTab(settings_tab, self.tr('settings'))
        
        right_layout.addWidget(self.tabs)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([400, 800])
        main.addWidget(main_splitter)
        
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("color: #E65100; background-color: #FFE0B2; font-size: 11px;")
        self.license_status_label = QLabel("")
        self.status_bar.addPermanentWidget(self.license_status_label)
        self.update_license_display()
        self.update_status_bar()
        
        if hasattr(self, 'saved_config'):
            config = self.saved_config
            if 'email' in config:
                self.email_input.setText(config['email'])
            if 'password' in config:
                self.password_input.setText(config['password'])
            if 'account_mode' in config:
                index = self.account_combo.findText(config['account_mode'])
                if index >= 0:
                    self.account_combo.setCurrentIndex(index)
            if 'default_amount' in config:
                self.settings_default_amount.setValue(config['default_amount'])
            if 'default_duration' in config:
                self.settings_default_duration.setValue(config['default_duration'])
            if 'auto_trade' in config:
                self.auto_trade_check.setChecked(config['auto_trade'])
            if 'enable_auto_relogin' in config:
                self.enable_auto_relogin.setChecked(config['enable_auto_relogin'])
            if 'relogin_retries' in config:
                self.relogin_retries.setValue(config['relogin_retries'])
            if 'sound_enabled' in config:
                self.sound_enabled = config['sound_enabled']
                self.sound_manager.enabled = self.sound_enabled
                self.update_sound_button()
            if 'global_stop_loss' in config:
                self.stop_loss_spin.setValue(config['global_stop_loss'])
            if 'global_take_profit' in config:
                self.take_profit_spin.setValue(config['global_take_profit'])
    
    def on_risk_changed(self):
        self.global_stop_loss = self.stop_loss_spin.value()
        self.global_take_profit = self.take_profit_spin.value()
        if self.trade_manager:
            self.trade_manager.set_risk_parameters(self.global_stop_loss, self.global_take_profit)
        self.save_config()
    
    def reset_risk(self):
        if self.trade_manager:
            self.trade_manager.reset_risk()
            self.log_message("✅ Risk reset complete. Trading resumed.")
            self.update_statistics()
    
    def on_account_changed(self, account_type):
        if self.connected and self.client:
            self.log_message(f"🔄 Account changed to: {account_type}")
            self.log_message("💰 Updating balance...")
            QTimer.singleShot(1000, self.fetch_balance)
            if self.trade_manager:
                self.trade_manager.reset_risk()
                self.log_message("🔄 Risk parameters reset for new account")
    
    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        self.sound_manager.enabled = self.sound_enabled
        self.update_sound_button()
        self.save_config()
        if self.sound_enabled:
            self.log_message("🔊 Sound enabled")
        else:
            self.log_message("🔇 Sound disabled")
    
    def update_sound_button(self):
        if self.sound_enabled:
            self.sound_btn.setText("🔊 Sound On")
            self.sound_btn.setStyleSheet("""
                QPushButton { background-color: white; color: #FF9800; border: none; padding: 4px 12px; border-radius: 4px; font-weight: bold; font-size: 11px; }
                QPushButton:hover { background-color: #FFF3E0; }
            """)
        else:
            self.sound_btn.setText("🔇 Sound Off")
            self.sound_btn.setStyleSheet("""
                QPushButton { background-color: #f44336; color: white; border: none; padding: 4px 12px; border-radius: 4px; font-weight: bold; font-size: 11px; }
                QPushButton:hover { background-color: #da190b; }
            """)
    
    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, "✅ Copied", "Address copied to clipboard")
    
    def play_trade_sound(self, sound_type):
        if not self.sound_enabled:
            return
        try:
            QApplication.beep()
        except:
            pass
    
    def on_martingale_toggled(self, checked):
        self.martingale_settings['enabled'] = checked
        if self.trade_manager:
            self.trade_manager.update_martingale_settings(self.martingale_settings)
        if checked:
            self.martingale_status_label.setText(self.tr('enabled'))
            self.martingale_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self.martingale_status_label.setText(self.tr('disabled'))
            self.martingale_status_label.setStyleSheet("color: #f44336; font-weight: bold;")
        self.update_martingale_display()
    
    def on_martingale_type_changed(self, index):
        self.martingale_settings['martingale_type'] = self.martingale_type_combo.currentData()
        if self.trade_manager:
            self.trade_manager.update_martingale_settings(self.martingale_settings)
        self.update_martingale_display()
    
    def update_martingale_display(self):
        if self.martingale_settings['enabled']:
            martingale_type = self.martingale_settings['martingale_type']
            type_names = {
                MartingaleType.DISABLED: "Disabled",
                MartingaleType.NEXT_OPPORTUNITY_SAME: "Next Same",
                MartingaleType.NEXT_OPPORTUNITY_ANY: "Next Any"
            }
            self.martingale_type_label.setText(type_names.get(martingale_type, "Unknown"))
        if self.trade_manager:
            pending_count = len(self.trade_manager.pending_martingale) if hasattr(self.trade_manager, 'pending_martingale') else 0
            self.martingale_pending_label.setText(str(pending_count))
    
    def update_status_bar(self):
        if self.license_manager.is_valid:
            days = self.license_manager.get_remaining_days()
            license_info = f" | License: {days} days"
        else:
            license_info = " | ⚠️ License NOT ACTIVATED"
        not_executed_count = len(self.trade_manager.get_not_executed_trades()) if self.trade_manager else 0
        net_profit_info = ""
        if self.trade_manager:
            net_profit, profit_pct = self.trade_manager.get_net_profit()
            net_profit_info = f" | Net P/L: ${net_profit:.2f} ({profit_pct:+.1f}%)"
        risk_status = ""
        if self.trade_manager and hasattr(self.trade_manager, 'stop_loss_triggered'):
            if self.trade_manager.stop_loss_triggered:
                risk_status = " | ⛔ STOP LOSS TRIGGERED"
            elif self.trade_manager.take_profit_triggered:
                risk_status = " | 🎯 TAKE PROFIT TRIGGERED"
        status = (f"Balance: ${self.balance:.2f} | Active: {len(self.trade_manager.get_active_trades()) if self.trade_manager else 0} | "
                 f"Not Executed: {not_executed_count} | "
                 f"Martingale: {'ON' if self.martingale_settings['enabled'] else 'OFF'}"
                 f"{net_profit_info}{risk_status}{license_info}")
        self.status_bar.showMessage(status)
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")
        cursor = self.log_area.textCursor()
        cursor.movePosition(cursor.End)
        self.log_area.setTextCursor(cursor)
        if self.log_area.document().characterCount() > MAX_LOG_SIZE * 10:
            self.log_area.setPlainText(self.log_area.toPlainText()[-MAX_LOG_SIZE * 5:])
    
    def refresh_session(self):
        if self.connected and self.client and self.trade_manager:
            if hasattr(self.trade_manager, '_refresh_session'):
                self.trade_manager._refresh_session()
    
    def refresh_history(self):
        if self.trade_manager:
            history = self.trade_manager.get_trade_history()
            self.history_table.setRowCount(len(history))
            for i, trade in enumerate(history):
                self.update_history_row(i, trade)
    
    def start_auto_relogin(self):
        if not self.connected or not self.client:
            return
        if self.auto_relogin_thread and self.auto_relogin_thread.isRunning():
            self.auto_relogin_thread.stop()
            self.auto_relogin_thread.wait()
        if self.enable_auto_relogin.isChecked():
            email = self.email_input.text().strip()
            password = self.password_input.text().strip()
            account_mode = self.account_combo.currentText()
            self.auto_relogin_thread = AutoReloginThread(email, password, account_mode)
            self.auto_relogin_thread.login_successful.connect(self.on_auto_relogin_success)
            self.auto_relogin_thread.login_failed.connect(self.on_auto_relogin_failed)
            self.auto_relogin_thread.log_signal.connect(self.log_message)
            self.auto_relogin_thread.max_retries = self.relogin_retries.value()
            self.auto_relogin_thread.start()
            self.last_relogin_time = datetime.now()
    
    def on_auto_relogin_success(self, success, new_client):
        if success and new_client:
            self.client = new_client
            if self.trade_manager:
                self.trade_manager.update_client(new_client)
            if self.connection_manager:
                self.connection_manager.set_client(new_client)
            self.last_relogin_time = datetime.now()
            self.relogin_count += 1
            self.relogin_count_label.setText(str(self.relogin_count))
            self.log_message("💰 Updating balance after reconnection...")
            QTimer.singleShot(1000, self.fetch_balance)
            if self.trade_manager:
                self.trade_manager.reset_risk()
            self.update_relogin_display()
    
    def on_auto_relogin_failed(self, error_msg):
        self.relogin_failures += 1
        self.next_relogin_label.setText("--:--")
    
    def update_relogin_display(self):
        if self.last_relogin_time and self.auto_relogin_thread and self.auto_relogin_thread.isRunning():
            next_relogin = self.last_relogin_time + timedelta(seconds=RELOGIN_INTERVAL)
            now = datetime.now()
            if next_relogin > now:
                remaining = next_relogin - now
                minutes = int(remaining.total_seconds() // 60)
                seconds = int(remaining.total_seconds() % 60)
                self.next_relogin_label.setText(f"{minutes:02d}:{seconds:02d}")
            else:
                self.next_relogin_label.setText("00:00")
        else:
            self.next_relogin_label.setText("--:--")
    
    def start_connection_monitor(self):
        if self.connection_manager and self.connection_manager.isRunning():
            self.connection_manager.stop()
            self.connection_manager.wait()
        if self.connected and self.client:
            email = self.email_input.text().strip()
            password = self.password_input.text().strip()
            account_mode = self.account_combo.currentText()
            self.connection_manager = RobustConnectionManager(email, password, account_mode)
            self.connection_manager.set_client(self.client)
            self.connection_manager.connection_lost.connect(self.on_connection_lost)
            self.connection_manager.connection_restored.connect(self.on_connection_restored)
            self.connection_manager.reconnecting.connect(self.on_reconnecting)
            self.connection_manager.log_signal.connect(self.log_message)
            self.connection_manager.start()
    
    def on_connection_lost(self):
        self.connected = False
        self.conn_status.setText(self.tr('disconnected'))
        self.conn_status.setStyleSheet("color: #f44336; font-weight: bold;")
        self.log_message(self.tr('connection_lost'))
        self.manual_call_btn.setEnabled(False)
        self.manual_put_btn.setEnabled(False)
    
    def on_connection_restored(self):
        self.connected = True
        self.conn_status.setText(self.tr('connected'))
        self.conn_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
        self.log_message(self.tr('connection_restored'))
        self.manual_call_btn.setEnabled(True)
        self.manual_put_btn.setEnabled(True)
        if self.trade_manager and self.connection_manager:
            self.trade_manager.update_client(self.connection_manager.client)
        QTimer.singleShot(1000, self.fetch_balance)
    
    def on_reconnecting(self, attempt, max_attempts):
        self.log_message(f"🔄 Reconnecting to Quotex... (Attempt {attempt}/{max_attempts})")
    
    def connect_to_quotex(self):
        if not HAS_QUOTEX:
            QMessageBox.critical(self, "Error", "quotexapi not installed")
            return
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        if not email or not password:
            self.log_message("⚠️ Enter email and password")
            return
        self.connect_btn.setEnabled(False)
        self.connect_btn.setText(self.tr('connecting'))
        self.log_message("🔄 Connecting...")
        self.connect_thread = ConnectThread(email, password, self.account_combo.currentText())
        self.connect_thread.progress.connect(self.log_message)
        self.connect_thread.finished.connect(self.on_connect_finished)
        self.connect_thread.start()
    
    def on_connect_finished(self, success, msg, client):
        self.connect_btn.setEnabled(True)
        if success and client:
            self.connected = True
            self.client = client
            self.conn_status.setText(self.tr('connected'))
            self.conn_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.connect_btn.setText(self.tr('connect'))
            self.refresh_balance_btn.setEnabled(True)
            self.refresh_assets_btn.setEnabled(True)
            self.manual_call_btn.setEnabled(True)
            self.manual_put_btn.setEnabled(True)
            self.log_message("✅ Connected")
            self.trade_manager = TradeManager(
                self.client, 
                self.martingale_settings,
                self.global_stop_loss,
                self.global_take_profit,
                self.connection_manager
            )
            self.trade_manager.log_signal.connect(self.log_message)
            self.trade_manager.trade_started.connect(self.on_trade_started)
            self.trade_manager.trade_completed.connect(self.on_trade_completed)
            self.trade_manager.trade_not_executed.connect(self.on_trade_not_executed)
            self.trade_manager.martingale_triggered.connect(self.on_martingale_triggered)
            self.trade_manager.balance_updated.connect(self.on_balance_updated)
            self.trade_manager.sound_signal.connect(self.play_trade_sound)
            self.trade_manager.active_trades_updated.connect(self.update_active_trades_list)
            QTimer.singleShot(1000, self.fetch_balance)
            QTimer.singleShot(2000, self.load_available_assets)
            self.start_balance_timer()
            self.start_auto_relogin()
            self.start_connection_monitor()
        else:
            self.connected = False
            self.client = None
            self.conn_status.setText(self.tr('disconnected'))
            self.conn_status.setStyleSheet("color: #f44336; font-weight: bold;")
            self.connect_btn.setText(self.tr('connect'))
            self.refresh_balance_btn.setEnabled(False)
            self.refresh_assets_btn.setEnabled(False)
            self.manual_call_btn.setEnabled(False)
            self.manual_put_btn.setEnabled(False)
            self.log_message(f"❌ Failed: {msg}")
        self.update_status_bar()
    
    def on_balance_updated(self, new_balance):
        self.balance = new_balance
        self.balance_label.setText(f"${new_balance:.2f}")
        self.update_status_bar()
    
    def on_martingale_triggered(self, parent_id, martingale_info):
        step = martingale_info['step']
        symbol = martingale_info['symbol']
        amount = martingale_info['amount']
        mtype = martingale_info['type']
        if mtype == "next_opportunity_same":
            self.log_message(f"⏳ M{step}: {symbol} ${amount:.2f}")
        elif mtype == "next_opportunity_any":
            self.log_message(f"⏳ M{step}: ANY ${amount:.2f}")
        self.update_martingale_display()
    
    def load_available_assets(self):
        if not self.connected or not self.client:
            self.log_message(self.tr('no_connection'))
            return
        self.refresh_assets_btn.setEnabled(False)
        self.refresh_assets_btn.setText(self.tr('refresh'))
        self.assets_loader = AssetsLoader(self.client)
        self.assets_loader.progress.connect(self.log_message)
        self.assets_loader.finished.connect(self.on_assets_loaded)
        self.assets_loader.start()
    
    def on_assets_loaded(self, assets):
        self.refresh_assets_btn.setEnabled(True)
        self.refresh_assets_btn.setText(self.tr('refresh'))
        self.asset_combo.clear()
        if assets and isinstance(assets, list) and len(assets) > 0:
            self.available_assets = assets
            self.asset_combo.addItems(assets)
            if assets:
                self.asset_combo.setCurrentIndex(0)
            self.log_message(f"✅ Loaded {len(assets)} assets from Quotex")
        else:
            self.log_message("⚠️ No assets loaded, using fallback")
            self.asset_combo.addItem("EURUSD")
    
    def start_balance_timer(self):
        if hasattr(self, 'balance_timer') and self.balance_timer:
            self.balance_timer.stop()
        self.balance_timer = QTimer()
        self.balance_timer.timeout.connect(self.fetch_balance)
        self.balance_timer.start(30000)
    
    def fetch_balance(self):
        if not self.connected or not self.client:
            return
        if not hasattr(self, 'balance_thread') or not self.balance_thread or not self.balance_thread.isRunning():
            self.balance_thread = BalanceThread(self.client)
            self.balance_thread.finished.connect(self.on_balance_fetched)
            self.balance_thread.start()
    
    def on_balance_fetched(self, bal, success):
        if success and bal > 0:
            self.balance = bal
            self.balance_label.setText(f"${bal:.2f}")
            self.update_status_bar()
    
    def on_trade_signal(self, symbol, direction, amount, duration):
        """معالجة الإشارة المستلمة من ملف الإشارات"""
        account_type = self.account_combo.currentText()
        if account_type == self.tr('real'):
            if not self.license_manager.is_valid:
                self.log_message(self.tr('license_required'))
                return
            if self.license_manager.remaining_seconds <= 0:
                self.log_message(self.tr('license_expired'))
                return
        if not self.connected or not self.client or not self.trade_manager:
            self.log_message(self.tr('no_connection'))
            return
        if not self.auto_trade_check.isChecked():
            self.log_message(self.tr('auto_trade_disabled'))
            return
        if amount <= 0:
            amount = self.settings_default_amount.value()
        pending_martingale = self.trade_manager.check_pending_martingale(symbol)
        if pending_martingale:
            amount = pending_martingale.calculate_next_amount()
            self.log_message(f"🎯 M{pending_martingale.current_step}: {symbol} ${amount:.2f}")
        internal_id = self.trade_manager.open_trade(
            symbol, direction, amount, duration, 
            martingale_info=pending_martingale,
            signal_source="FILE"
        )
        if internal_id and not pending_martingale:
            self.log_message(f"📊 {symbol} {direction.upper()} ${amount:.2f}")
    
    def manual_trade(self, direction):
        if not self.license_manager.is_valid and self.account_combo.currentText() == self.tr('real'):
            self.log_message(self.tr('license_required'))
            return
        if self.license_manager.remaining_seconds <= 0 and self.account_combo.currentText() == self.tr('real'):
            self.log_message(self.tr('license_expired'))
            return
        if not self.connected or not self.client or not self.trade_manager:
            self.log_message(self.tr('no_connection'))
            return
        selected_asset = self.asset_combo.currentText().strip()
        if not selected_asset:
            selected_asset = "EURUSD"
        pending_martingale = self.trade_manager.check_pending_martingale(selected_asset)
        if pending_martingale:
            amount = pending_martingale.calculate_next_amount()
            self.log_message(f"🎯 M{pending_martingale.current_step}: {selected_asset} ${amount:.2f}")
        else:
            amount = self.settings_default_amount.value()
        internal_id = self.trade_manager.open_trade(
            selected_asset, direction, amount,
            self.settings_default_duration.value(),
            martingale_info=pending_martingale,
            signal_source="Manual"
        )
    
    def on_trade_started(self, internal_id, trade_info):
        self.update_active_trades_list()
        self.update_status_bar()
    
    def on_trade_completed(self, internal_id, result):
        self.update_history_table(result)
        self.update_statistics()
        self.update_active_trades_list()
        self.update_martingale_display()
        self.update_status_bar()
    
    def on_trade_not_executed(self, trade_info):
        self.update_not_executed_table(trade_info)
        self.update_statistics()
        self.update_status_bar()
    
    def update_active_trades_list(self):
        if not self.trade_manager:
            return
        self.active_trades_list.clear()
        trades = self.trade_manager.get_active_trades()
        if not trades:
            self.active_trades_list.addItem(QListWidgetItem(self.tr('no_active_trades')))
            return
        for t in trades:
            color = {
                'pending': '#FF9800',
                'running': '#2196F3',
                'waiting_candle': '#4CAF50',
                'checking_result': '#9C27B0',
                'completed': '#4CAF50',
                'error': '#f44336'
            }.get(t['status'], '#333333')
            martingale_text = f" M{t.get('martingale_step', 0)}" if t.get('martingale_step', 0) > 0 else ""
            source_text = f" [{t.get('signal_source', '')}]" if t.get('signal_source') else ""
            retry_text = f" [R{t.get('retry_count', 0)}]" if t.get('retry_count', 0) > 0 else ""
            item = QListWidgetItem(
                f"[{t['internal_id']}{martingale_text}{source_text}{retry_text}] {t['symbol']} {t['direction'].upper()} ${t['amount']:.2f}"
            )
            item.setForeground(QColor(color))
            self.active_trades_list.addItem(item)
    
    def update_not_executed_table(self, trade_info):
        row = self.not_executed_table.rowCount()
        self.not_executed_table.insertRow(0)
        time_str = trade_info.get('entry_time', 'N/A')
        if len(time_str) > 8:
            time_str = time_str[-8:]
        self.not_executed_table.setItem(0, 0, QTableWidgetItem(time_str))
        self.not_executed_table.setItem(0, 1, QTableWidgetItem(trade_info.get('internal_id', 'N/A')[:8]))
        self.not_executed_table.setItem(0, 2, QTableWidgetItem(trade_info.get('symbol', 'N/A')))
        dir_item = QTableWidgetItem(trade_info.get('direction', 'N/A').upper())
        dir_item.setForeground(QColor('#4CAF50') if trade_info.get('direction') == 'call' else QColor('#f44336'))
        self.not_executed_table.setItem(0, 3, dir_item)
        self.not_executed_table.setItem(0, 4, QTableWidgetItem(f"${trade_info.get('amount',0):.2f}"))
        error_item = QTableWidgetItem(trade_info.get('error_message', 'Unknown error'))
        error_item.setForeground(QColor('#f44336'))
        self.not_executed_table.setItem(0, 5, error_item)
    
    def update_history_table(self, t):
        self.history_table.insertRow(0)
        self.update_history_row(0, t)
    
    def update_history_row(self, row, t):
        time_str = t.get('completion_time', 'N/A')
        if len(time_str) > 8:
            time_str = time_str[-8:]
        self.history_table.setItem(row, 0, QTableWidgetItem(time_str))
        self.history_table.setItem(row, 1, QTableWidgetItem(t.get('internal_id', 'N/A')[:8]))
        sym = t.get('symbol', 'N/A')
        self.history_table.setItem(row, 2, QTableWidgetItem(sym))
        dir_item = QTableWidgetItem(t.get('direction', 'N/A').upper())
        dir_item.setForeground(QColor('#4CAF50') if t.get('direction') == 'call' else QColor('#f44336'))
        self.history_table.setItem(row, 3, dir_item)
        self.history_table.setItem(row, 4, QTableWidgetItem(f"${t.get('amount',0):.2f}"))
        result_type = t.get('result_type', 'unknown')
        if result_type == 'win':
            result_text = "WIN"
            result_color = '#4CAF50'
        elif result_type == 'break_even':
            result_text = "BREAK EVEN"
            result_color = '#FF9800'
        else:
            result_text = "LOSS"
            result_color = '#f44336'
        res_item = QTableWidgetItem(result_text)
        res_item.setForeground(QColor(result_color))
        self.history_table.setItem(row, 5, res_item)
        profit = t.get('profit', 0)
        amount = t.get('amount', 0)
        if profit > 0:
            total_returned = amount + profit
            profit_text = f"+${profit:.2f} (${total_returned:.2f})"
            profit_color = '#4CAF50'
        elif profit < 0:
            profit_text = f"-${abs(profit):.2f}"
            profit_color = '#f44336'
        else:
            profit_text = "$0.00 (Refund)"
            profit_color = '#FF9800'
        prof_item = QTableWidgetItem(profit_text)
        prof_item.setForeground(QColor(profit_color))
        prof_item.setFont(QFont("", -1, QFont.Bold))
        self.history_table.setItem(row, 6, prof_item)
        if amount > 0:
            if profit > 0:
                roi = (profit / amount) * 100
                roi_text = f"+{roi:.0f}%"
                roi_color = '#4CAF50'
            elif profit < 0:
                roi = (abs(profit) / amount) * 100
                roi_text = f"-{roi:.0f}%"
                roi_color = '#f44336'
            else:
                roi_text = "0%"
                roi_color = '#FF9800'
        else:
            roi_text = "-"
            roi_color = '#666666'
        roi_item = QTableWidgetItem(roi_text)
        roi_item.setForeground(QColor(roi_color))
        self.history_table.setItem(row, 7, roi_item)
        net_profit, profit_pct = self.trade_manager.get_net_profit() if self.trade_manager else (0, 0)
        net_profit_text = f"${net_profit:.2f} ({profit_pct:+.1f}%)"
        net_item = QTableWidgetItem(net_profit_text)
        net_item.setForeground(QColor("#FF9800"))
        self.history_table.setItem(row, 8, net_item)
        m_step = t.get('martingale_step', 0)
        m_text = f"M{m_step}" if m_step > 0 else "-"
        m_item = QTableWidgetItem(m_text)
        if m_step > 0:
            m_item.setForeground(QColor("#FF9800"))
        self.history_table.setItem(row, 9, m_item)
        status_text = t.get('status', 'completed').upper()
        status_item = QTableWidgetItem(status_text)
        status_item.setForeground(QColor("#4CAF50") if status_text == "COMPLETED" else QColor("#FF9800"))
        self.history_table.setItem(row, 10, status_item)
    
    def clear_history(self):
        if QMessageBox.question(self, "Clear History", 
                                "Are you sure you want to clear all trade history?", 
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            if self.trade_manager:
                self.trade_manager.trade_history.clear()
            self.history_table.setRowCount(0)
            self.log_message("📜 Trade history cleared")
            self.update_statistics()
    
    def clear_not_executed(self):
        if self.trade_manager:
            self.trade_manager.not_executed_trades.clear()
        self.not_executed_table.setRowCount(0)
        self.log_message("⚠️ Not executed list cleared")
        self.update_status_bar()
    
    def update_statistics(self):
        if not self.trade_manager:
            return
        stats = self.trade_manager.get_stats()
        
        self.stats_active_trades.setText(str(stats.get('active_trades', 0)))
        self.stats_total_trades.setText(str(stats.get('total_trades', 0)))
        self.stats_wins.setText(str(stats.get('wins', 0)))
        self.stats_losses.setText(str(stats.get('losses', 0)))
        self.stats_break_even.setText(str(stats.get('break_even', 0)))
        self.stats_win_rate.setText(f"{stats.get('win_rate', 0):.1f}%")
        self.stats_total_profit.setText(f"${stats.get('total_profit', 0):.2f}")
        
        net_profit, profit_pct = self.trade_manager.get_net_profit()
        self.stats_net_profit.setText(f"${net_profit:.2f} ({profit_pct:+.1f}%)")
        
        self.stats_avg_win.setText(f"${stats.get('avg_win', 0):.2f}")
        self.stats_avg_loss.setText(f"${stats.get('avg_loss', 0):.2f}")
        self.stats_not_executed.setText(str(stats.get('not_executed_trades', 0)))
        self.stats_martingale_trades.setText(str(stats.get('martingale_trades', 0)))
        self.stats_martingale_wins.setText(str(stats.get('martingale_wins', 0)))
        
        if stats.get('stop_loss_triggered', False):
            self.stats_risk_status.setText(self.tr('risk_sl_triggered'))
            self.stats_risk_status.setStyleSheet("color: #f44336; font-weight: bold;")
        elif stats.get('take_profit_triggered', False):
            self.stats_risk_status.setText(self.tr('risk_tp_triggered'))
            self.stats_risk_status.setStyleSheet("color: #FF9800; font-weight: bold;")
        else:
            self.stats_risk_status.setText(self.tr('risk_active'))
            self.stats_risk_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
        
        self.update_status_bar()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())