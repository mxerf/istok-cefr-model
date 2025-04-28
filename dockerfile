FROM python:3.11-slim

WORKDIR /app

# Установим зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY app app

# Запускаем сервер
CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]