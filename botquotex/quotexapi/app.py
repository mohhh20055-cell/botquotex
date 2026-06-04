import sys
import os

# إضافة المجلد الحالي إلى مسار Python لضمان العثور على المكتبات
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("=" * 50)
print("🚀 بدء تشغيل بوت Quotex...")
print(f"📁 المجلد الحالي: {os.getcwd()}")
print(f"📂 مسار الملف: {current_dir}")
print(f"🐍 مسارات Python: {sys.path[:3]}...")
print("=" * 50)

# محاولة استيراد المكتبات المطلوبة
try:
    from flask import Flask, jsonify, render_template, request, session
    print("✅ Flask تم استيرادها بنجاح")
except Exception as e:
    print(f"❌ خطأ في استيراد Flask: {e}")
    sys.exit(1)

try:
    import http.client
    print("✅ http.client تم استيراده بنجاح")
except Exception as e:
    print(f"⚠️ تحذير: http.client - {e}")

# محاولة استيراد Quotex (اختياري للتشغيل الأساسي)
quotex_available = False
try:
    from stable_api import Quotex
    quotex_available = True
    print("✅ Quotex API تم استيرادها بنجاح")
except ImportError:
    try:
        from quotexapi.stable_api import Quotex
        quotex_available = True
        print("✅ Quotex API (من quotexapi) تم استيرادها بنجاح")
    except ImportError:
        print("⚠️ Quotex API غير متوفرة - ستعمل واجهة الاختبار فقط")

print("=" * 50)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "quotex-bot-secret-key-2024")

# تخزين مؤقت للبيانات (لأن Render لا يحتفظ بالجلسات بين الطلبات)
user_sessions = {}

@app.route('/')
def index():
    """الصفحة الرئيسية - تعرض حالة البوت"""
    return jsonify({
        "status": "Bot is running",
        "message": "تم تشغيل البوت بنجاح على Render",
        "version": "1.0.0",
        "quotex_api": quotex_available,
        "endpoints": {
            "/": "الصفحة الرئيسية",
            "/health": "فحص صحة البوت",
            "/api/status": "حالة البوت",
            "/api/info": "معلومات إضافية"
        }
    })

@app.route('/health')
def health():
    """نقطة نهاية لفحص صحة التطبيق"""
    return jsonify({
        "status": "healthy",
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "quotex_ready": quotex_available
    })

@app.route('/api/status')
def status():
    """الحصول على حالة البوت"""
    return jsonify({
        "running": True,
        "mode": "production",
        "quotex_connected": quotex_available,
        "python_version": sys.version.split()[0]
    })

@app.route('/api/info')
def info():
    """معلومات إضافية عن البوت"""
    return jsonify({
        "name": "Quotex Trading Bot",
        "version": "1.0.0",
        "author": "Your Name",
        "description": "بوت تداول آلي لمنصة Quotex",
        "features": [
            "تحليل السوق باستخدام RSI",
            "تداول تلقائي ويدوي",
            "واجهة تحكم عن بعد"
        ]
    })

# نقطة نهاية بسيطة للاختبار
@app.route('/api/test')
def test():
    return jsonify({"success": True, "message": "API is working!"})

# خطأ عام للتعامل مع المسارات غير الموجودة
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "المسار غير موجود", "status": 404}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "خطأ داخلي في الخادم", "status": 500}), 500

print("=" * 50)
print("✅ تم تهيئة تطبيق Flask بنجاح")
print(f"🔌 سيتم التشغيل على المنفذ: {os.environ.get('PORT', 10000)}")
print("=" * 50)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    # للتشغيل المحلي فقط
    app.run(host='0.0.0.0', port=port, debug=True)
