import os

from .base import *  # noqa: F401,F403

DEBUG = False

ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',')
CSRF_TRUSTED_ORIGINS = os.environ['CSRF_TRUSTED_ORIGINS'].split(',')

# Railway termina TLS num proxy na frente da aplicação; sem isso o Django
# não reconhece a requisição como HTTPS e entra em loop de redirect.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Com DEBUG=False o Django não escreve erros 500 no console; sem isso o
# traceback não aparece nos logs do Railway.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'WARNING'},
    },
}

# Valor conservador para o primeiro deploy — aumentar depois de confirmar
# que HTTPS está estável (subir demais cedo demais pode travar acesso
# via HTTP caso algo dê errado com o certificado/proxy).
SECURE_HSTS_SECONDS = 3600
