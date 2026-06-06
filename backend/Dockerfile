FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev ffmpeg && rm -rf /var/lib/apt/lists/*

# Устанавливаем setuptools с pkg_resources (версия <81)
RUN pip install --upgrade pip "setuptools<81" wheel

COPY requirements.txt .

# --no-build-isolation: заставляет pip использовать уже установленный
# setuptools<81 вместо скачивания свежего (82+) в изолированную среду
RUN pip install --no-cache-dir --no-build-isolation -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]