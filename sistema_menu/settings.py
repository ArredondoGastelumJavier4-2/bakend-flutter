"""
Django settings for sistema_menu project.
"""

from pathlib import Path
import os
from django.contrib.messages import constants as messages


# ============================================
# BASE DIR
# ============================================
BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================
# SECURITY
# ============================================
SECRET_KEY = 'django-insecure-i+s(n(emm0i^h^r9x4a=a5bcmqh^0&40^xe&#fj)248mofpab6'
DEBUG = True
ALLOWED_HOSTS = [    "127.0.0.1",
    "localhost",
    "192.168.1.10",
    '*'
]  #172.16.100.216', 'localhost'


# ============================================
# APPS INSTALADAS   
# ============================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Crispy Forms
    'crispy_forms',
    'crispy_bootstrap5',

    # Nuestra app
    'menu',
]


# ============================================
# CRISPY SETTINGS
# ============================================
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


# ============================================
# MIDDLEWARE
# ============================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ============================================
# URLS
# ============================================
ROOT_URLCONF = 'sistema_menu.urls'


# ============================================
# TEMPLATES
# ============================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'menu' / 'templates',  # carpeta de templates
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # 👇 nuestro contador global de carrito
                'menu.views.carrito_items_count',
            ],
        },
    },
]


# ============================================
# WSGI
# ============================================
WSGI_APPLICATION = 'sistema_menu.wsgi.application'


# ============================================
# BASE DE DATOS (MySQL 3308)
# ============================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'menu_db',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': '3308',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'; SET innodb_strict_mode=1;",
        },
        'TEST': {
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_general_ci',
        },
    }
}


# ============================================
# VALIDACIÓN DE CONTRASEÑAS
# ============================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]


# ============================================
# INTERNACIONALIZACIÓN
# ============================================
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Hermosillo'
USE_I18N = True
USE_TZ = True


# ============================================
# ARCHIVOS STATIC (CSS, JS, imágenes)
# ============================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"


# ============================================
# ARCHIVOS MEDIA (fotos de perfil, productos)
# ============================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ============================================
# MENSAJES (estilos de Bootstrap)
# ============================================
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}


# ============================================
# DEFAULT PRIMARY KEY
# ============================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
