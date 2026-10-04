"""
Django settings for the Simple E-commerce Store.

This file is kept short and commented so it is easy to follow.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# NOTE: This key is for local demo use only. Change it before deploying anywhere.
SECRET_KEY = "django-insecure-demo-key-change-me-before-deploying"

DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",          # built-in users, login, logout, passwords
    "django.contrib.contenttypes",
    "django.contrib.sessions",      # the shopping cart is stored in the session
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "store",                        # our shop app
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Gives every template the number of items in the cart.
                "store.context_processors.cart_summary",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database: SQLite (a single file called db.sqlite3, no setup needed)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript) and uploaded media (product images)
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Where to send people after login/logout (names come from store/urls.py)
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
