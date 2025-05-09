# Use the official Python 3.11 image from Docker Hub
FROM python:3.11

# Install system dependencies for Pillow and others
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
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=controlledmotives.settings.production

# Set working directory
WORKDIR /app

# Copy requirements.txt first to leverage Docker caching
COPY requirements.txt /app/

RUN pip install psycopg2-binary

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . /app/

# Collect static files (ensure DJANGO_SETTINGS_MODULE is set for this to succeed)
RUN python manage.py collectstatic --noinput

# Expose the port Gunicorn will run on
EXPOSE 8000

SECRET_KEY='5qw33wsoda+_&**8*k&-m(-$08%svttlzzv0692ah7ethouql8'

# Start app with Gunicorn
CMD ["gunicorn", "controlledmotives.wsgi:application", "--bind", "0.0.0.0:8000"]
