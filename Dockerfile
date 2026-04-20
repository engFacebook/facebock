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

# فتح المنفذ
EXPOSE 5000

# تشغيل التطبيق
WORKDIR /app/backend
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
