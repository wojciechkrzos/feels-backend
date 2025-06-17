# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY ./feels_backend /app

RUN ls

CMD ["python", "manage.py", "runserver", "0.0.0.0:8002"]