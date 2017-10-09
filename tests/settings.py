# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

import django
import os
import environ
import logging.config


DEBUG = True
INTERNAL_IPS = ('127.0.0.1')
USE_TZ = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "__________________________________________________"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "test.db",
    }
}

ROOT_URLCONF = "tests.urls"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    'django.contrib.staticfiles',
    'django.contrib.messages',
    "django.contrib.sessions",
    'social_django',
    "django_auth0_user",
    "tests",
    'test_app',
    'django_extensions',
    'debug_toolbar',
]


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates"), ],
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

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]


AUTH_TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(os.path.dirname(__file__), 'templates')],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'social_django.context_processors.backends',
            'social_django.context_processors.login_redirect',
        ],
    },
}]

SITE_ID = 1

MIDDLEWARE_TUPLE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

if django.VERSION >= (1, 10):
    MIDDLEWARE = MIDDLEWARE_TUPLE
else:
    MIDDLEWARE_CLASSES = MIDDLEWARE_TUPLE


# AUTH_USER_MODEL = 'auth.User'
AUTH_USER_MODEL = 'django_auth0_user.Auth0User'


LOGOUT_REDIRECT_URL = '/'

env = environ.Env()
env.read_env(environ.Path(__file__, is_file=True)('.env'))
AUTH0_DOMAIN = env('AUTH0_USER_DOMAIN')
AUTH0_OIDC_URL = 'https://{}'.format(AUTH0_DOMAIN)
AUTH0_MANAGEMENT_API_CLIENT_ID = env('AUTH0_MANAGEMENT_API_CLIENT_ID')
AUTH0_MANAGEMENT_API_CLIENT_SECRET = env('AUTH0_MANAGEMENT_API_CLIENT_SECRET')
CLEAN_USERNAME_FUNCTION = 'django_auth0_user.clean.slugify'


AUTHENTICATION_BACKENDS = (
    'django_auth0_user.backend.Auth0OpenId',
    'django.contrib.auth.backends.ModelBackend',
)


# SOCIAL_AUTH_USER_MODEL = 'django_auth0_user.models.Auth0User'
SOCIAL_AUTH_AUTHENTICATION_BACKENDS = [
    'django_auth0_user.backend.Auth0OpenId'
]
# SOCIAL_AUTH_PIPELINE = (
#     # Get the information we can about the user and return it in a simple
#     # format to create the user instance later. On some cases the details are
#     # already part of the auth response from the provider, but sometimes this
#     # could hit a provider API.
#     'social_core.pipeline.social_auth.social_details',
#
#     # Get the social uid from whichever service we're authing thru. The uid is
#     # the unique identifier of the given user in the provider.
#     'social_core.pipeline.social_auth.social_uid',
#
#     # Verifies that the current auth process is valid within the current
#     # project, this is where emails and domains whitelists are applied (if
#     # defined).
#     'social_core.pipeline.social_auth.auth_allowed',
#
#     # Checks if the current social-account is already associated in the site.
#     'social_core.pipeline.social_auth.social_user',
#
#     # Run our custom get_username to populate using the Auth0 User ID.
#     # 'django_auth0_user.pipeline.user.get_username',
#
#     # Make up a username for this person, appends a random string at the end if
#     # there's any collision.
#     'social_core.pipeline.user.get_username',
#
#     # Send a validation email to the user to verify its email address.
#     # Disabled by default.
#     # 'social_core.pipeline.mail.mail_validation',
#
#     # Associates the current social details with another user account with
#     # a similar email address. Disabled by default.
#     # 'social_core.pipeline.social_auth.associate_by_email',
#
#     # Create a user account if we haven't found one yet.
#     'social_core.pipeline.user.create_user',
#
#     # Create the record that associates the social account with the user.
#     'social_core.pipeline.social_auth.associate_user',
#
#     # Populate the extra_data field in the social record with the values
#     # specified by settings (and the default ones like access_token, etc).
#     'social_core.pipeline.social_auth.load_extra_data',
#
#     # Update the user record with any changed info from the auth service.
#     'social_core.pipeline.user.user_details',
# )
SOCIAL_AUTH_AUTH0_KEY = env('AUTH0_WEB_SITE_CLIENT_ID')
SOCIAL_AUTH_AUTH0_SECRET = env('AUTH0_WEB_SITE_CLIENT_SECRET')
# SOCIAL_AUTH_AUTH0_USER_ID_IS_DJANGO_USERNAME = True


# SOCIAL_AUTH_AUTH0_IGNORE_DEFAULT_SCOPE = True
# SOCIAL_AUTH_AUTH0_SCOPE = ['openid', 'profile', 'email']


# # SOCIAL AUTH AUTH0 BACKEND CONFIG
# SOCIAL_AUTH_TRAILING_SLASH = False
# SOCIAL_AUTH_AUTH0_KEY = os.environ.get('AUTH0_CLIENT_ID')
# SOCIAL_AUTH_AUTH0_SECRET = os.environ.get('AUTH0_CLIENT_SECRET')
# SOCIAL_AUTH_AUTH0_SCOPE = [
#     'openid',
#     'profile'
# ]
# SOCIAL_AUTH_AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN')
# AUDIENCE = os.environ.get('AUTH0_AUDIENCE')
# if AUDIENCE:
#     SOCIAL_AUTH_AUTH0_AUTH_EXTRA_ARGUMENTS = {'audience': AUDIENCE}
# AUTHENTICATION_BACKENDS = {
#     'auth0login.auth0backend.Auth0',
#     'django.contrib.auth.backends.ModelBackend'
# }
#
# LOGIN_URL = "/login/auth0"
# LOGIN_REDIRECT_URL = "/dashboard"
# LOGOUT_REDIRECT_URL = "/"


# ---------------------------------
# Django Rest Framework Stuff
# ---------------------------------

# REST_FRAMEWORK = {
#     'DEFAULT_PERMISSION_CLASSES': (
#         'rest_framework.permissions.IsAuthenticated',
#     ),
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'oidc_auth.authentication.BearerTokenAuthentication',
#         'oidc_auth.authentication.JSONWebTokenAuthentication',
#         # 'oauth2_provider.ext.rest_framework.OAuth2Authentication',
#         # 'rest_framework_social_oauth2.authentication.SocialAuthentication',
#         # 'rest_framework_auth0.authentication.Auth0JSONWebTokenAuthentication',
#     ),
# }

# ---------------------------------
# Logging
# ---------------------------------

LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console':{
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'null': {
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django': {
            'handlers': ['console'],
        },
        'django.db.backends.schema': {
            'handlers': ['null'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'py.warnings': {
            'handlers': ['console'],
        },
        'requests': {
            # The requests library is too verbose in it's logging, reducing the verbosity in our logs.
            'handlers': ['null'],
            'level': 'WARNING',
        },
    }
}

logging.config.dictConfig(LOGGING)

