# Django settings for rdc_crawler project.
import os

import couchdb

# Get project root folder
_project_root = os.path.dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('rdc', 'rafaeldurancastaneda@gmail.com'),
)

MANAGERS = ADMINS

# Cache
CACHES = {
    'default': {
         'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
         'LOCATION': '.django_cache',
    }
}

# Databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/path/to/file.sqlite3',
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'notsosecret'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    "html5boilerplate/static",
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'mediagenerator.middleware.MediaMiddleware',
)

ROOT_URLCONF = 'rdc_crawler.urls'

TEMPLATE_DIRS = (
    '{0}/html5boilerplate/templates'.format(_project_root),
    '{0}/html5boilerplate/templates/crawler'.format(_project_root),
    # Put strings here, like "/home/html/django_templates" or
    # "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djcelery',
    'mediagenerator',
    'html5boilerplate',
    'gunicorn',
    'crawler',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
#LOGGING = {
#    'version': 1,
#    'disable_existing_loggers': False,
#    'handlers': {
#        'mail_admins': {
#            'level': 'ERROR',
#            'class': 'django.utils.log.AdminEmailHandler',
#        }
#    },
#    'loggers': {
#        'django.request': {
#            'handlers': ['mail_admins'],
#            'level': 'ERROR',
#            'propagate': True,
#        },
#    }
#}

# LOCAL SETTINGS, OVERRITING GLOBALS
try:
    from rdc_crawler.local.local_settings import *  # @UnusedWildImport
    try:
        server = couchdb.Server(SERVER)  # pylint:disable=C0103
        server.resource.credentials = (COUCH_USER, COUCH_PASS)
        DB = server['crawler']
    except couchdb.http.ResourceNotFound:
        DB = server.create('crawler')
except ImportError as e:
    print("local/local_settings.py not found!")
    print("Use local/local_settings.py.template")
    raise e

if not os.path.exists(EMAIL_FILE_PATH):
    os.mkdir(EMAIL_FILE_PATH)

from rdc_crawler.html5boilerplate.media import HTML5_MEDIA_BUNDLES
MEDIA_BUNDLES = HTML5_MEDIA_BUNDLES


# Set global media search paths
GLOBAL_MEDIA_DIRS = (
    os.path.join(_project_root, 'static'),
)

# Set media URL (important: don't forget the trailing slash!).
# PRODUCTION_MEDIA_URL is used when running manage.py generatemedia
MEDIA_DEV_MODE = DEBUG
DEV_MEDIA_URL = '/devmedia/'
PRODUCTION_MEDIA_URL = '/media/'

# Configure yuicompressor if available
YUICOMPRESSOR_PATH = os.path.join(
    os.path.dirname(_project_root), 'yuicompressor.jar')
if os.path.exists(YUICOMPRESSOR_PATH):
    ROOT_MEDIA_FILTERS = {
        'js': 'mediagenerator.filters.yuicompressor.YUICompressor',
        'css': 'mediagenerator.filters.yuicompressor.YUICompressor',
    }

# Celery
import djcelery
djcelery.setup_loader()
