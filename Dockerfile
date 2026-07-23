FROM python:3.11-slim

WORKDIR /app

# OpenCV headless runtime libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY server/requirements.txt /app/server/requirements.txt
RUN pip install --no-cache-dir -r /app/server/requirements.txt

COPY server /app/server
COPY UI /app/UI

# Hugging Face Spaces expects port 7860
ENV PORT=7860
EXPOSE 7860

CMD ["gunicorn", "--chdir", "server", "-b", "0.0.0.0:7860", "--timeout", "120", "--workers", "1", "server:app"]
