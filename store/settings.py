from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url
import cloudinary

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY missing")

DEBUG = os.getenv("DEBUG", "False") == "True"

# ALLOWED_HOSTS configuration
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

# Add DuckDNS domain and EC2 IP for production
ALLOWED_HOSTS.extend([
    "souled-api.duckdns.org",
    "18.60.156.231",
])

INSTALLED_APPS = [
    'django_daisy',
    'django.contrib.humanize',  # Required
    
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "corsheaders",
    "django_filters",

    "cloudinary",
    "cloudinary_storage",

    "accounts",
    "products",
    "cart",
    "orders",
    "panel",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Serve static files in production
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "store.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "store.wsgi.application"

# --- Database ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL missing")

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=False if DEBUG else True,
    )
}

AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.authentication.CookieJWTAuthentication",
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Your API',
    'DESCRIPTION': 'API for ...',
    'VERSION': '1.0.0',
}

# =======================
#   JWT Cookie Settings
# =======================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_COOKIE": "access",
    "AUTH_COOKIE_REFRESH": "refresh",
    "AUTH_COOKIE_SECURE": not DEBUG,  # True in production (HTTPS only)
    "AUTH_COOKIE_HTTP_ONLY": True,  # Prevent JavaScript access
    "AUTH_COOKIE_PATH": "/",
    "AUTH_COOKIE_SAMESITE": "None" if not DEBUG else "Lax",  # Allow cross-origin
}

# ======================
# Cookie & CORS Settings
# ======================
SESSION_COOKIE_SAMESITE = "None" if not DEBUG else "Lax"
CSRF_COOKIE_SAMESITE = "None" if not DEBUG else "Lax"
SESSION_COOKIE_SECURE = not DEBUG  # True in production (HTTPS)
CSRF_COOKIE_SECURE = not DEBUG  # True in production (HTTPS)

CORS_ALLOW_CREDENTIALS = True

# Get CORS origins from environment or use defaults
cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

# Add production frontend URL
CORS_ALLOWED_ORIGINS.extend([
    "https://souled-frontend.vercel.app",
])

csrf_origins = os.getenv("CSRF_TRUSTED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_origins.split(",") if origin.strip()]

# Add DuckDNS domain and frontend URL
CSRF_TRUSTED_ORIGINS.extend([
    "https://souled-api.duckdns.org",
    "http://souled-api.duckdns.org",
    "https://souled-frontend.vercel.app",
])

# Trust X-Forwarded-Proto header from Nginx for HTTPS detection
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookie settings for JWT authentication
COOKIE_SECURE = not DEBUG  # True in production (HTTPS only)
COOKIE_SAMESITE = "None" if not DEBUG else "Lax"  # Allow cross-origin in production

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
X_FRAME_OPTIONS = "DENY"


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise configuration for serving static files
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Cloudinary ---
cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
api_key = os.getenv("CLOUDINARY_API_KEY")
api_secret = os.getenv("CLOUDINARY_API_SECRET")

if not cloud_name or not api_key or not api_secret:
    raise RuntimeError("Cloudinary credentials missing")

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": cloud_name,
    "API_KEY": api_key,
    "API_SECRET": api_secret,
}


cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret,
    secure=True,
)

MEDIA_URL = "/media/"

# --- Stripe ---
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

if not STRIPE_SECRET_KEY or not STRIPE_WEBHOOK_SECRET:
    raise RuntimeError("Stripe keys missing")

# --- Logging ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}


