FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean

WORKDIR /app


COPY requirements.txt /app/
COPY . /app/


RUN pip install -r requirements.txt


CMD ["gunicorn", "--bind", "0.0.0.0:8000", "fur_store.wsgi:application"]
