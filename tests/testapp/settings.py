from pathlib import Path

SECRET_KEY = 'secret_key'
BASE_DIR = Path(__file__).resolve().parent
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = ['django_fixtures_command']
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}
