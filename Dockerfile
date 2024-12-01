# Базовый образ
FROM python:3.12-slim

# Устанавливаем зависимости для Python и системы
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY requirements.txt /app/
COPY . /app/

# Устанавливаем зависимости Python
RUN pip install -r requirements.txt

# Создаем миграции
RUN python manage.py makemigrations

# Выполняем миграции
RUN python manage.py migrate

# Команда по умолчанию
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "fur_store.wsgi:application"]
