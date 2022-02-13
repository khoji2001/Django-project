
"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import django
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from datetime import timedelta
import jdatetime
jdatetime.set_locale('fa_IR')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "Test.ir", "www.Test.ir", "Test.com", "www.Test.com"]

# Application definition


INSTALLED_APPS = [
	'config.apps.TestAdminConfig',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.humanize',
	'django.forms',
	'djoser',
    'corsheaders',
	'django_crontab',
	'rest_framework',
	'rest_framework.authtoken',
	'jalali_date',
	'users.apps.UsersConfig',
	'contract.apps.ContractConfig',
	'customer.apps.CustomerConfig',
	'supplier.apps.SupplierConfig',
	'document.apps.DocumentConfig',
	'OTP.apps.RegistrationConfig',
	'ckeditor',
	'django_admin_listfilter_dropdown',
]
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True
ROOT_URLCONF = 'config.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME':  'main',
		'USER': 'postgres',
		'PASSWORD': '1234',
		'HOST': 'localhost',
		'PORT': '',
	}
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []

"""    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
"""
CRONJOBS = [
        ('30 4 * * *', 'contract.cron.due_contracts'),
		('30 0 * * *', 'contract.cron.month_summary'),
		('30 4 * * *', 'contract.cron.is_surety'),
		('30 4 * * *' ,'customer.cron.confirmation_expired_sms'),
        ('0 3 * * 6' ,'contract.cron.free_vcc_coffer')
        ]
JALALI_DATE_DEFAULTS = {
   'Strftime': {
        'date': '%y/%m/%d',
        'datetime': "%a, %d %b %Y %H:%M:%S",
    },
    'Static': {
        'js': [
            # loading datepicker
            'admin/js/django_jalali.min.js',
            # OR
            # 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.core.js',
            # 'admin/jquery.ui.datepicker.jalali/scripts/calendar.js',
            # 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc.js',
            # 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc-fa.js',
            # 'admin/js/main.js',
        ],
    'css': {
        'all': [
            'admin/jquery.ui.datepicker.jalali/themes/base/jquery-ui.min.css',
        ]
        }
    },
}
# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

AUTH_USER_MODEL = 'users.User'

LANGUAGE_CODE = 'fa-ir'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = ','
NUMBER_GROUPING = 3

FILE_UPLOAD_PERMISSIONS = 0o644
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

EMAIL_HOST = 'test.eu'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'admin@test.com'
EMAIL_HOST_PASSWORD = 'Test@1234'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_USE_LOCALTIME = True
ADMIN_EMAILS = ['ited.Test@gmail.com',]
REST_FRAMEWORK = {
	'DEFAULT_AUTHENTICATION_CLASSES':
		[
			'rest_framework_simplejwt.authentication.JWTAuthentication',
		],
	'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
	'PAGE_SIZE': 20
}
SIMPLE_JWT = {
	'ACCESS_TOKEN_LIFETIME': timedelta(days=5),
	'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
}
DJOSER = {
	"USER_CREATE_PASSWORD_RETYPE": True,
	"SERIALIZERS": {
		'current_user': "OTP.serializers.UserRegistrationSerializer",
	}
}