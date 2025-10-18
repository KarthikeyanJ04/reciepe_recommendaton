# Use CUDA base for GPU, or python:3.10 if CPU only
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# System dependencies
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*
# Copy requirements and install
WORKDIR /app
COPY requirements.txt ./
RUN python3 -m pip install --upgrade pip && pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# Copy all code (src/, app.py, etc.)
COPY . /app

# Expose Flask API port
EXPOSE 5000

CMD ["python3", "app.py"]
