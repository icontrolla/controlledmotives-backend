from pathlib import Path
import os
from decouple import config
import dj_database_url
import warnings

# Suppress specific deprecation warnings
warnings.filterwarnings("ignore", message=".*USERNAME_REQUIRED is deprecated.*", module="dj_rest_auth.registration.serializers")
warnings.filterwarnings("ignore", message=".*EMAIL_REQUIRED is deprecated.*", module="dj_rest_auth.registration.serializers")

DJANGO_ENV = os.getenv("DJANGO_ENV", "development")

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'skdummy123'
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = [
    "https://controntrolledmotives-frontend-1.onrender.com",
    "https://controlledmotives-backend.onrender.com",
    "controlledmotives-backend.onrender.com",
    "localhost",
    "127.0.0.1",
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_REDIRECT_URL = 'https://controntrolledmotives-frontend-1.onrender.com'

CSRF_TRUSTED_ORIGINS = [
    "https://controntrolledmotives-frontend-1.onrender.com",
    "https://controlledmotives-backend.onrender.com",
    "https://controlledmotives.art",
]

SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'frontend/static')]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

CSP_SCRIPT_SRC = ("'self'", "'unsafe-eval'")
CSP_IMG_SRC = (
    "'self'",
    "data:",
    "https://controlled-media.s3.us-east-005.backblazeb2.com",
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework_simplejwt.authentication.JWTAuthentication'],
}

CORS_ALLOWED_ORIGINS = [
    "http://controlledmotives-backend.onrender.com",
    "https://controntrolledmotives-frontend-1.onrender.com",
    "https://controlledmotives.art",
    "http://localhost:3000",
]
CORS_ALLOW_CREDENTIALS = True
CORS_URLS_REGEX = r"^/.*$"

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'profiles',
    'django_q',
    "django_extensions",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'csp.middleware.CSPMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'profiles.urls'
WSGI_APPLICATION = 'controlledmotives.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'frontend')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTH_USER_MODEL = 'profiles.CustomUser'

# Signup/Login unified setup
ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_SIGNUP_FIELDS = ['username', 'email', 'password1', 'password2']
ACCOUNT_EMAIL_VERIFICATION = 'optional'
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_REQUIRED = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'}
    }
}


AUTHENTICATION_BACKENDS = [
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'walternyika20@gmail.com'
EMAIL_HOST_PASSWORD = 'Controll3r@123'

# AWS (Backblaze B2)
DEFAULT_FILE_STORAGE = 'controlledmotives.storage_backends.MediaStorage'
AWS_ACCESS_KEY_ID = '0051d74288f85ef0000000003'
AWS_SECRET_ACCESS_KEY = 'K005DrjWYhvXjb2Csfg/MlXTQMfmBWg'
AWS_STORAGE_BUCKET_NAME = 'controlled-media'
AWS_S3_REGION_NAME = 'us-east-005'
AWS_S3_ENDPOINT_URL = 'https://s3.us-east-005.backblazeb2.com'
AWS_S3_ADDRESSING_STYLE = "virtual"
AWS_QUERYSTRING_AUTH = False
AWS_DEFAULT_ACL = None

# Database
if DJANGO_ENV == "production":
    DATABASES = {
        'default': dj_database_url.config(
            default='postgresql://icontrolla:ImdOPLXHEEJufurvE7TJpuzyjATIBp3D@dpg-d0hmaa3uibrs739stkqg-a.render.com:5432/controlledmotives'
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Redis (optional)
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')

# Sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Cache (local)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Q Cluster for task queueing
Q_CLUSTER = {
    "name": "controlled-motives",
    "workers": 4,
    "retry": 3600,
    "timeout": 3000,
    "queue_limit": 50,
    "bulk": 10,
    "orm": "default",
}

# Serializers
ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter'
REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'controlledmotives.serializers.UserSerializer'
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Admin
ADMIN_URL = config('ADMIN_URL', default='admin/')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler'}},
    'loggers': {'django': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': True}},
}

# Localization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
