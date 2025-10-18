
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive


RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN python3 -m pip install --upgrade pip && pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

COPY . /app


EXPOSE 5000

CMD ["python3", "app.py"]
