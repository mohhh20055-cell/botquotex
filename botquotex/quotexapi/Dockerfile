FROM python:3.11-slim

WORKDIR /app

# تثبيت الاعتمادات الأساسية
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات وتثبيتها أولاً (للاستفادة من Cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي المشروع
COPY . .

# إنشاء مجلد للإعدادات
RUN mkdir -p settings

# تعيين متغيرات البيئة
ENV PYTHONUNBUFFERED=1
ENV PORT=10000

# تشغيل التطبيق
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
