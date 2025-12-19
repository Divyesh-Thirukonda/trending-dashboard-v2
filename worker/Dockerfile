FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for yt-dlp/ffmpeg if needed
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables will be injected by App Runner
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
