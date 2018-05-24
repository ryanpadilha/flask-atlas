import os
import logging

SECRET_KEY = '8fpEQzmkXzxRfbAtiXQLMus6BhNS9gWocrNxM2ggCnw'

WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'Cmy7R2I3DfVptP4BcyVS'

TEMPLATES_AUTO_RELOAD = True

# https://docs.python.org/3/howto/logging.html
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOGGING_LOCATION = 'flask-atlas.log'
LOGGING_LEVEL = logging.DEBUG

DEBUG = True
USE_RELOADER = False
JSON_SORT_KEYS = False

RUN_HOST = '0.0.0.0'
RUN_PORT = int(os.environ.get('PORT', 8000))

BACKDOOR_ACCESS_KEY = 'nBheqThb8rw9-MJZLbnFRTMZ3!gc5cfeDyeQXh'
PROVIDER_SIGNATURE = 'eC^PCK#&W:eS<Un]k8n4sJf*)a_AnT,'
JWT_SECRET = 'pole=Risk2Numb!radio3Trophy$Movie@U7hs3rV3rS3CR31'
