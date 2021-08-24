from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%tb&oljj%p01l3&tsb66h1y$frc_j8u4#bik%x%$xklkg3s*@w'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'channels',
    'account',
    'mainapp',
    'paygate',
    'static_app',
    'notification',
    'admin_panel',
]

AUTH_USER_MODEL = 'account.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'discordauto.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'discordauto.wsgi.application'
ASGI_APPLICATION = 'discordauto.asgi.application'


# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             "hosts": [("127.0.0.1", 6379)],
#         },
#     },
# }


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}



# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
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
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "assets"),
]

# STATIC_ROOT = os.path.join(BASE_DIR, "assets")

COINBASE_API_VERSION = '2018-03-22'
COINBASE_API_KEY = '1d44876e-db0f-45a2-9f9d-a5a7f71ad746'


EMAIL_BACKEND= 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT= 587
EMAIL_USE_TLS= True
EMAIL_HOST_USER = "netrobeweb@gmail.com"
EMAIL_HOST_PASSWORD = "wpcgtxfwmiqnlbwv"
# Custom user defined mail username
DEFAULT_FROM_EMAIL = "lunarpromos@gmail.com"
DEFAULT_COMPANY_EMAIL = "lunarpromos@gmail.com"



LOGIN_REDIRECT_URL="account:login"
LOGIN_URL="account:login"
LOGOUT_URL = 'account:logout'

BOT_MAX = 10
BOT_CONNECTION_TIME = 5 #in minutes


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'basic': {
            'handlers': ['basic_h'],
            'level': 'DEBUG',
        },
        'basic.error': {
            'handlers': ['basic_e'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
    'handlers': {
        'basic_h': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': './logs/debug.log',
            'formatter' : 'simple',
        },
        'basic_e': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': './logs/error.log',
            'formatter' : 'simple',
        },
    },
    'formatters':{
        'simple': {
            'format': '{levelname} : {asctime} : {message}',
            'style': '{',
        }
    }
}




"""
168.80.195.202:3128
168.80.98.64:3128
168.80.177.145:3128
168.80.177.238:3128
168.80.98.136:3128
168.80.96.142:3128
168.80.178.25:3128
168.80.177.58:3128
168.80.176.151:3128
168.80.98.49:3128
168.80.96.148:3128
168.80.97.196:3128
168.80.179.103:3128
168.80.178.214:3128
168.80.177.115:3128
168.80.193.16:3128
168.80.176.133:3128
168.80.178.61:3128
168.80.96.31:3128
168.80.177.34:3128

"""


