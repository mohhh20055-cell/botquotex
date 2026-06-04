import sys
import os

# حذف المجلد الحالي والمجلدات الفرعية من مسارات البحث الأولى لبايثون مؤقتاً
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir in sys.path:
    sys.path.remove(current_dir)
if '' in sys.path:
    sys.path.remove('')

# إعادة إضافة مسار المشروع في نهاية القائمة ليعمل كمسار فرعي لا يتعارض مع بايثون
sys.path.append(current_dir)
from flask import Flask, render_template, request, jsonify, session
from botquotex.quotexapi.stable_api import Quotex
import asyncio
import os
import json
import threading
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key-here")

# تخزين حالة البوت لكل مستخدم
bots = {}

class QuotexBot:
    def __init__(self, email, password, mode="PRACTICE"):
        self.email = email
        self.password = password
        self.mode = mode
        self.client = None
        self.is_running = False
        self.current_asset = "EURUSD"
        self.trade_history = []
        
    async def connect(self):
        """الاتصال بـ Quotex"""
        try:
            self.client = Quotex(
                email=self.email,
                password=self.password,
                lang="ar"
            )
            self.client.set_account_mode(self.mode)
            check, reason = await self.client.connect()
            if check:
                return True, "تم الاتصال بنجاح"
            return False, reason
        except Exception as e:
            return False, str(e)
    
    async def get_balance(self):
        """الحصول على الرصيد"""
        if self.client:
            return await self.client.get_balance()
        return 0
    
    async def get_available_assets(self):
        """الحصول على الأصول المتاحة"""
        if self.client:
            assets = await self.client.get_all_assets()
            return list(assets.keys())[:50]  # أول 50 زوج
        return []
    
    async def analyze_market(self, asset, duration=60):
        """تحليل السوق باستخدام المؤشرات"""
        try:
            # جلب بيانات الشموع
            candles = await self.client.get_candles(asset, None, duration * 30, duration)
            
            if not candles or len(candles) < 20:
                return {"signal": "neutral", "reason": "بيانات غير كافية"}
            
            # استخراج الأسعار
            prices = [float(c["close"]) for c in candles]
            
            # حساب RSI بسيط
            rsi = self.calculate_rsi(prices)
            
            # حساب المتوسطات المتحركة
            sma_fast = sum(prices[-10:]) / 10 if len(prices) >= 10 else prices[-1]
            sma_slow = sum(prices[-20:]) / 20 if len(prices) >= 20 else prices[-1]
            
            current_price = prices[-1]
            
            # تحليل الاتجاه
            trend = "UP" if sma_fast > sma_slow else "DOWN"
            
            # اتخاذ القرار
            signal = "neutral"
            reason = ""
            
            if rsi < 30 and trend == "UP":
                signal = "call"
                reason = f"RSI منخفض ({rsi:.1f}) مع اتجاه صاعد"
            elif rsi > 70 and trend == "DOWN":
                signal = "put"
                reason = f"RSI مرتفع ({rsi:.1f}) مع اتجاه هابط"
            elif rsi < 30:
                signal = "call"
                reason = f"RSI في منطقة تشبع بيعي ({rsi:.1f})"
            elif rsi > 70:
                signal = "put"
                reason = f"RSI في منطقة تشبع شرائي ({rsi:.1f})"
            else:
                reason = f"RSI محايد ({rsi:.1f}) - انتظار إشارة أوضح"
            
            return {
                "signal": signal,
                "reason": reason,
                "rsi": round(rsi, 2),
                "current_price": current_price,
                "trend": trend,
                "sma_fast": round(sma_fast, 5),
                "sma_slow": round(sma_slow, 5)
            }
            
        except Exception as e:
            return {"signal": "neutral", "reason": f"خطأ في التحليل: {str(e)}"}
    
    def calculate_rsi(self, prices, period=14):
        """حساب مؤشر RSI"""
        if len(prices) < period + 1:
            return 50
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if len(gains) < period:
            return 50
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    async def execute_trade(self, asset, amount, direction, duration):
        """تنفيذ صفقة"""
        try:
            success, result = await self.client.buy(amount, asset, direction, duration)
            
            trade_record = {
                "id": result if success else None,
                "asset": asset,
                "direction": direction,
                "amount": amount,
                "duration": duration,
                "time": datetime.now().isoformat(),
                "status": "executed" if success else "failed",
                "error": result if not success else None
            }
            
            if success:
                # انتظار النتيجة
                await asyncio.sleep(duration + 2)
                win = await self.client.check_win(result)
                trade_record["result"] = "win" if win else "loss"
                if win:
                    profit = amount * 0.8
                    trade_record["profit"] = profit
                else:
                    trade_record["profit"] = -amount
            
            self.trade_history.insert(0, trade_record)
            return success, trade_record
            
        except Exception as e:
            return False, {"error": str(e)}
    
    async def auto_trade(self, asset, amount, duration, max_trades=5):
        """التداول التلقائي"""
        self.is_running = True
        trades_done = 0
        results = []
        
        while self.is_running and trades_done < max_trades:
            # تحليل السوق
            analysis = await self.analyze_market(asset, duration)
            
            if analysis["signal"] != "neutral":
                success, trade = await self.execute_trade(
                    asset, amount, analysis["signal"], duration
                )
                results.append({
                    "analysis": analysis,
                    "trade": trade,
                    "success": success,
                    "time": datetime.now().isoformat()
                })
                trades_done += 1
                
                # انتظار بين الصفقات
                await asyncio.sleep(120)
            else:
                # انتظار 30 ثانية ثم إعادة التحليل
                await asyncio.sleep(30)
        
        self.is_running = False
        return results
    
    def stop(self):
        self.is_running = False
        if self.client:
            self.client.close()


def run_async(coro):
    """تشغيل دوال غير متزامنة"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('dashboard.html')


@app.route('/api/login', methods=['POST'])
def login():
    """تسجيل الدخول إلى Quotex"""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    mode = data.get('mode', 'PRACTICE')  # PRACTICE أو REAL
    
    if not email or not password:
        return jsonify({"success": False, "error": "البريد الإلكتروني وكلمة المرور مطلوبان"})
    
    # إنشاء بوت جديد
    bot = QuotexBot(email, password, mode)
    success, message = run_async(bot.connect())
    
    if success:
        # تخزين البوت في الجلسة
        session['user_email'] = email
        bots[email] = bot
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "error": message})


@app.route('/api/assets', methods=['GET'])
def get_assets():
    """الحصول على قائمة الأصول المتاحة"""
    email = session.get('user_email')
    if not email or email not in bots:
        return jsonify({"success": False, "error": "الرجاء تسجيل الدخول أولاً"})
    
    bot = bots[email]
    assets = run_async(bot.get_available_assets())
    return jsonify({"success": True, "assets": assets})


@app.route('/api/balance', methods=['GET'])
def get_balance():
    """الحصول على الرصيد"""
    email = session.get('user_email')
    if not email or email not in bots:
        return jsonify({"success": False, "error": "الرجاء تسجيل الدخول أولاً"})
    
    bot = bots[email]
    balance = run_async(bot.get_balance())
    return jsonify({"success": True, "balance": balance})


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """تحليل السوق لزوج معين"""
    email = session.get('user_email')
    if not email or email not in bots:
        return jsonify({"success": False, "error": "الرجاء تسجيل الدخول أولاً"})
    
    data = request.json
    asset = data.get('asset', 'EURUSD')
    duration = int(data.get('duration', 60))
    
    bot = bots[email]
    analysis = run_async(bot.analyze_market(asset, duration))
    
    return jsonify({"success": True, "analysis": analysis})


@app.route('/api/trade', methods=['POST'])
def trade():
    """تنفيذ صفقة يدوية"""
    email = session.get('user_email')
    if not email or email not in bots:
        return jsonify({"success": False, "error": "الرجاء تسجيل الدخول أولاً"})
    
    data = request.json
    asset = data.get('asset')
    amount = float(data.get('amount', 10))
    direction = data.get('direction')  # call أو put
    duration = int(data.get('duration', 60))
    
    if not asset or not direction:
        return jsonify({"success": False, "error": "بيانات غير مكتملة"})
    
    bot = bots[email]
    success, trade = run_async(bot.execute_trade(asset, amount, direction, duration))
    
    return jsonify({"success": success, "trade": trade})


@app.route('/api/auto_trade', methods=['POST'])
def auto_trade():
    """بدء التداول التلقائي"""
    email = session.get('user_email')
    if not email or email not in bots:
        return jsonify({"success": False, "error": "الرجاء تسجيل الدخول أولاً"})
    
    data = request.json
    asset = data.get('asset', 'EURUSD')
    amount = float(data.get('amount', 10))
    duration = int(data.get('duration', 60))
    max_trades = int(data.get('max_trades', 5))
    
    bot = bots[email]
    
    # تشغيل التداول التلقائي في خلفية منفصلة
    def run_auto():
        results = run_async(bot.auto_trade(asset, amount, duration, max_trades))
        # تخزين النتائج (يمكن إضافتها لاحقاً)
    
    thread = threading.Thread(target=run_auto)
    thread.start()
    
    return jsonify({
        "success": True,
        "message": f"بدأ التداول التلقائي على {asset} بمبلغ ${amount}"
    })


@app.route('/api/stop', methods=['POST'])
def stop_trade():
    """إيقاف التداول التلقائي"""
    email = session.get('user_email')
    if not email or email not in bots:
        return jsonify({"success": False, "error": "الرجاء تسجيل الدخول أولاً"})
    
    bot = bots[email]
    bot.stop()
    
    return jsonify({"success": True, "message": "تم إيقاف التداول"})


@app.route('/api/history', methods=['GET'])
def get_history():
    """الحصول على سجل الصفقات"""
    email = session.get('user_email')
    if not email or email not in bots:
        return jsonify({"success": False, "error": "الرجاء تسجيل الدخول أولاً"})
    
    bot = bots[email]
    return jsonify({"success": True, "history": bot.trade_history})


@app.route('/health')
def health():
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
