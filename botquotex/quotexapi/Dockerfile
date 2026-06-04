# استخدام نسخة بايثون مستقرة وخفيفة
FROM python:3.11-slim

# تحديد مجلد العمل داخل الحاوية المعزولة
WORKDIR /app

# نسخ ملف المتطلبات أولاً وتثبيته
COPY botquotex/quotexapi/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ بقية ملفات المشروع بالكامل
COPY . .

# ضبط مسار بايثون ليتعرف على المجلدات تلقائياً لتفادي خطأ ModuleNotFoundError
ENV PYTHONPATH="/app/botquotex/quotexapi:/app/botquotex"

# أمر تشغيل السيرفر على البورت الصحيح لـ Render
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "botquotex.quotexapi.app:app"]
