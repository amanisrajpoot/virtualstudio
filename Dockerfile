FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The application code is expected to be mounted via docker-compose volumes
# or copied in a production build.
