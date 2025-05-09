
# Use the official Python 3.11 image from Docker Hub
FROM python:3.11

# Install system dependencies for Pillow
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    python3-dev \
    libtiff5-dev \
    libopenjp2-7-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y gcc libpq-dev curl \
    && apt-get clean

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Collect static files (ensure DJANGO_SETTINGS_MODULE is set for this to succeed)
ENV DJANGO_SETTINGS_MODULE=green_exchange.settings
RUN python manage.py collectstatic --noinput

# Start app with Gunicorn
CMD ["gunicorn", "controlledmotives.wsgi:application", "--bind", "0.0.0.0:8000"]
