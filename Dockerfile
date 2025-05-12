# Use the official Python 3.11 image
FROM python:3.11

# Install system dependencies for Pillow and psycopg2
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
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Accept build-time secret key argument
ARG DJANGO_SECRET_KEY
ENV SECRET_KEY=${DJANGO_SECRET_KEY}

# Environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=controlledmotives.settings

# Set working directory
WORKDIR /app

# Copy dependency files first to leverage Docker cache
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . /app/

# Copy the .env file into the container
COPY .env .env

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port for Gunicorn
EXPOSE 8000

# Start Gunicorn server
CMD ["gunicorn", "controlledmotives.wsgi:application", "--bind", "0.0.0.0:8000"]
