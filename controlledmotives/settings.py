from pathlib import Path
import os
from decouple import config
import dj_database_url
import warnings


warnings.filterwarnings(
    "ignore",
    message=".*USERNAME_REQUIRED is deprecated.*",
    module="dj_rest_auth.registration.serializers"
)
warnings.filterwarnings(
    "ignore",
    message=".*EMAIL_REQUIRED is deprecated.*",
    module="dj_rest_auth.registration.serializers"
)


DJANGO_ENV = os.getenv("DJANGO_ENV", "development")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

#SECRET_KEY = config('SECRET_KEY')
SECRET_KEY = 'skdummy123'
DEBUG = config('DEBUG', default=False, cast=bool)
#NFT_STORAGE_API_KEY = config('NFT_STORAGE_API_KEY')
#STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='sk_test_dummy1234567890')

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

]

SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True



# Static and Media files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'frontend/static')]



# CORS settings

CORS_ALLOWED_ORIGINS = [
    'http://controlledmotives-backend.onrender.com',  # Render frontend
    "https://controntrolledmotives-frontend-1.onrender.com",
    'https://controlledmotives.com',  # Production frontend
]


# Application definition
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
    "django_extensions",
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'rest_framework',
    'rest_framework.authtoken',
    'profiles',  # Your custom app
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'storages'

]

AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',
)

SITE_ID = 1  # This should match the ID of the site you created


# Middleware settings
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'csp.middleware.CSPMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django.middleware.common.CommonMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# URL configuration
ROOT_URLCONF = 'profiles.urls'


CSP_IMG_SRC = (
    "'self'",
    "data:",
    "https://controlled-media.s3.us-east-005.backblazeb2.com",
)


# Templates settings
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



DEFAULT_FILE_STORAGE = 'controlledmotives.storage_backends.MediaStorage'


AWS_ACCESS_KEY_ID = '1d74288f85ef'
AWS_SECRET_ACCESS_KEY = '0051a461b12ebcda154989f994547b4b0c5e237122'
AWS_STORAGE_BUCKET_NAME = 'controlled-media'
AWS_S3_REGION_NAME = 'us-west-000'  # Always use 'us-west-000' for B2
AWS_S3_ENDPOINT_URL = 'https://s3.us-west-000.backblazeb2.com'
AWS_S3_ADDRESSING_STYLE = "virtual"
AWS_QUERYSTRING_AUTH = False  # Set to True if bucket is private

# Optional cache control for static/media
AWS_DEFAULT_ACL = None


# WSGI application
WSGI_APPLICATION = 'controlledmotives.wsgi.application'

if DJANGO_ENV == "production":
    DATABASES = {
        'default': dj_database_url.config(
            default='postgresql://icontrolla:ImdOPLXHEEJufurvE7TJpuzyjATIBp3D@dpg-d0hmaa3uibrs739stkqg-a.render.com:5432/controlledmotives'
        )
    }
else:
    # SQLite for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

CORS_ALLOW_CREDENTIALS = True
CORS_URLS_REGEX = r"^/.*$"

# Redis configuration (optional, for caching and sessions)
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')




# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

ACCOUNT_SIGNUP_FIELDS = ['email', 'username', 'password1', 'password2']

ACCOUNT_EMAIL_VERIFICATION = "optional"  # or "mandatory" if you want email verification
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_REQUIRED = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}


# Email settings (optional, for sending emails)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'walternyika20@gmail.com'
EMAIL_HOST_PASSWORD = 'Controll3r@123'

# Cache settings (optional, if using Redis for caching)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'


ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter'

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'controlledmotives.serializers.UserSerializer'
}


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Admin settings
ADMIN_URL = config('ADMIN_URL', default='admin/')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}


CSRF_COOKIE_SECURE = True

# Logging configuration (optional)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


