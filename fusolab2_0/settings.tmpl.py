# Django settings for fusoci project.
import os, sys

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('XXXX', 'xxx@xxx.org'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'xxx',                      # Or path to database file if using sqlite3.
        'USER': 'xxx',                      # Not used with sqlite3.
        'PASSWORD': 'xxxxx',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Rome'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'it-IT'

SITE_ID = 1

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
# append apps path
sys.path.insert(0, '%s/apps' % SITE_ROOT)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True


SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
SITE_DOMAIN="soci.fusolab.net"
BASE_URL = 'http://%s' % SITE_DOMAIN

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = '%s/common/media' % SITE_ROOT

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '%s/media/' % BASE_URL

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '%s/common/static/' % SITE_ROOT

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '%s/static/' % BASE_URL


# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '%s/static/admin/' % BASE_URL

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '%s/common/static' % SITE_ROOT,
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'gzw==4hc32u9f9h8saddsddas$0cqc#dfsdfds@7pf*9nzj'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'fusolab2_0.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '%s/common/templates' % SITE_ROOT
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'grappelli',
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'registration',
    'bar',
    'base',
    'ingresso',
    'salutatore',
    'baraled',
    'cancello',
    'reports',
    'django.contrib.humanize',
    'sorl.thumbnail',
    #'easy_thumbnails',
)

ROOT_URLCONF = 'fusolab2_0.urls'
THUMBNAIL_BASEDIR = 'thumbs'


# THUMBNAIL_DEBUG = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
#ROOT_URLCONF = 'urls'
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

DECIMAL_SEPARATOR = '.'

AUTH_PROFILE_MODULE = 'base.UserProfile'

ACCOUNT_ACTIVATION_DAYS = 365

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"

GRAPPELLI_ADMIN_TITLE="Admin Fusoci"

THUMBNAIL_ALIASES = {
    '': {
        'avatar': {'size': (112, 112), 'crop': True},
    },
}

#Password normale
EMAIL_HOST='smtp.xxx.it'
EMAIL_PORT=25
EMAIL_HOST_USER='xxx'
EMAIL_HOST_PASSWORD='xxxx'
#EMAIL_USE_TLS=True
#EMAIL_HOST = 'localhost'
DEFAULT_FROM_EMAIL = 'noreply@fusolab.net'
#url tessera
URL_CARD = 'http://127.0.0.1/cgi-bin/fusocard.cgi'

#lista indirizzi email per i conrolli apertura/chiusura
EMAIL_NOTIFICATION_LIST = ['xxxx@fusolab.net','xxxx.com']
MONEY_DELTA = 10.0

# password aperture cancello
OPEN_GATE_PW = "xxxx" 
OPEN_DOOR_PW = "xxxx"
IP_OPENER = "xxx"
PORT_OPENER = 8888

# arduini bar
BAR_SOPRA_IP = "10.172.0.X"
BAR_SOPRA_PORT = 10000

BAR_SOTTO_IP = "10.172.0.X"
BAR_SOTTO_PORT = 10000

#bara di led
BARALED_IP = "10.172.0.X"
BARALED_PORT = 8888 

