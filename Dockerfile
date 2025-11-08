
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

# Install system dependencies, including dos2unix
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libjpeg-dev zlib1g-dev dos2unix \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Create runtime dirs
RUN mkdir -p instance uploads

# Normalize script endings & permissions inside the image
RUN apt-get update && apt-get install -y --no-install-recommends dos2unix \
 && dos2unix docker-entrypoint.sh \
 && chmod +x docker-entrypoint.sh \
 && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "-b", "0.0.0.0:8000", "wsgi:app", "--workers=2", "--timeout=120"]
