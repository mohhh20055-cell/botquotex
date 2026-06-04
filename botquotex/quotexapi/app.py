from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import asyncio
import os
import threading
from bot_engine import QuotexBot

load_dotenv()

app = Flask(__name__)
bot = None
bot_thread = None

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('dashboard.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    """الحصول على حالة البوت"""
    if bot:
        stats = bot.get_statistics()
        return jsonify({
            "connected": True,
            "running": stats.get("running", False),
            "statistics": stats
        })
    return jsonify({"connected": False, "running": False})

@app.route('/api/start', methods=['POST'])
def start_bot():
    """تشغيل البوت"""
    global bot, bot_thread
    
    try:
        data = request.json
        email = os.getenv("QUOTEX_EMAIL")
        password = os.getenv("QUOTEX_PASSWORD")
        
        if not email or not password:
            return jsonify({"error": "بيانات الدخول غير موجودة في المتغيرات البيئية"}), 400
        
        # إنشاء البوت إذا لم يكن موجوداً
        if not bot:
            demo_mode = data.get("demo_mode", True)
            bot = QuotexBot(email, password, demo_mode)
            
            # تشغيل الاتصال
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            connected = loop.run_until_complete(bot.connect())
            
            if not connected:
                bot = None
                return jsonify({"error": "فشل الاتصال بـ Quotex"}), 400
        
        # تغيير الاستراتيجية إذا لزم الأمر
        strategy = data.get("strategy", "combined")
        bot.current_strategy = strategy
        
        # تشغيل البوت في خيط منفصل
        if not bot.is_running:
            asset = data.get("asset", "EURUSD")
            amount = float(data.get("amount", 10))
            duration = int(data.get("duration", 60))
            max_trades = int(data.get("max_trades", 10))
            
            def run_bot():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(bot.start_bot(asset, amount, duration, max_trades))
            
            bot_thread = threading.Thread(target=run_bot)
            bot_thread.start()
            
            return jsonify({"message": "تم تشغيل البوت بنجاح"}), 200
        else:
            return jsonify({"message": "البوت يعمل بالفعل"}), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """إيقاف البوت"""
    global bot
    
    if bot and bot.is_running:
        bot.stop_bot()
        return jsonify({"message": "تم إيقاف البوت"}), 200
    return jsonify({"message": "البوت غير نشط"}), 200

@app.route('/api/balance', methods=['GET'])
def get_balance():
    """الحصول على الرصيد"""
    if bot:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        balance = loop.run_until_complete(bot.get_balance())
        return jsonify({"balance": balance})
    return jsonify({"error": "البوت غير متصل"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)