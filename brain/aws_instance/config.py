import logging

SECRET_KEY = '8fpEQzmkXzxRfbAtiXQLMus6BhNS9gWocrNxM2ggCnw'

WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'Cmy7R2I3DfVptP4BcyVS'

TEMPLATES_AUTO_RELOAD = True

LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOGGING_LOCATION = 'flask-atlas.log'
LOGGING_LEVEL = logging.DEBUG

DEBUG = True
USE_RELOADER = True
JSON_SORT_KEYS = False

API_URL_BACKEND = 'http://0.0.0.0:9000'
