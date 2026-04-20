FROM python:3.11-slim

WORKDIR /app

# تثبيت الاعتماديات
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الكود
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# متغيرات البيئة
ENV PYTHONUNBUFFERED=1
ENV PORT=5000
ENV ENVIRONMENT=production

# فتح المنفذ
EXPOSE 5000

WORKDIR /app/backend

# تشغيل التطبيق
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
