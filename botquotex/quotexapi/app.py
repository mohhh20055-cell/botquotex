import sys
import os
from flask import Flask, jsonify

print("Python path:", sys.path)
print("Current directory:", os.getcwd())

# محاولة استيراد http.client للتأكد من عمله
try:
    import http.client
    print("✅ http.client imported successfully")
except Exception as e:
    print(f"❌ Failed to import http.client: {e}")

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "status": "Bot is running",
        "message": "تم تشغيل البوت بنجاح على Render باستخدام Docker"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
