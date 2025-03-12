# Используем официальный образ Python
FROM python:3.10

# Копируем всё содержимое в /app
COPY . /app
# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Команда для запуска Celery worker
CMD ["celery", "-A", "logic.tasks.celery_app:app", "worker", "--loglevel=info"]