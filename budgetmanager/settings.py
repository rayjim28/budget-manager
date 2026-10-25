from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

def load_local_env():
    # Local-only convenience. Production configuration stays in the host's environment.
    path = BASE_DIR / '.env'
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

load_local_env()
DEBUG = os.environ.get('DJANGO_DEBUG', 'false').lower() in ('true', '1', 'yes')
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') or os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'local-development-only-please-do-not-use-in-production'
    else:
        raise RuntimeError('Set DJANGO_SECRET_KEY in the environment before starting production.')

ALLOWED_HOSTS = [host.strip() for host in os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if host.strip()]
if os.environ.get('RENDER_EXTERNAL_HOSTNAME'):
    ALLOWED_HOSTS.append(os.environ['RENDER_EXTERNAL_HOSTNAME'])
CSRF_TRUSTED_ORIGINS = [host.strip() for host in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if host.strip()]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

INSTALLED_APPS = [
    'main_app',
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.humanize', 'django.contrib.staticfiles',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'budgetmanager.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'], 'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]
WSGI_APPLICATION = 'budgetmanager.wsgi.application'
DATABASES = {'default': dj_database_url.config(
    default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
    conn_max_age=600 if not DEBUG else 0,
    conn_health_checks=True,
)}
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_URL = '/accounts/login/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
