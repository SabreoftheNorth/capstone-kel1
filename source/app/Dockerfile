FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py schema.sql ./
RUN useradd -u 10001 -m appuser
USER 10001
EXPOSE 8080
# Inisialisasi schema (idempotent) lalu jalankan gunicorn
CMD ["sh", "-c", "python -c 'import app; app.init_db()'; exec gunicorn -b 0.0.0.0:8080 -w 2 app:app"]
