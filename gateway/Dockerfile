FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ gateway (bao gồm cả thư mục frontend bên trong) vào container
COPY . .

# Render sẽ cung cấp biến môi trường $PORT tự động. Nếu chạy local, dùng cổng 8000.
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}