# -*- coding: utf-8 -*-
import os

# أبسط تطبيق Flask ممكن
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "status": "Bot is running",
        "message": "تم تشغيل البوت بنجاح على Render"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
