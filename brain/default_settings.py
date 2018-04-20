import os
import logging
import datetime


BASEDIR = os.path.abspath(os.path.dirname(__file__))
APP_DIR = os.path.abspath(os.curdir)

SECRET_KEY = '8fpEQzmkXzxRfbAtiXQLMus6BhNS9gWocrNxM2ggCnw'

WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'Cmy7R2I3DfVptP4BcyVS'

TEMPLATES_AUTO_RELOAD = True

LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOGGING_LOCATION = 'flask-atlas.log'
LOGGING_LEVEL = logging.DEBUG

DEBUG = False
SQLALCHEMY_ECHO = False
USE_RELOADER = False
JSON_SORT_KEYS = False

RUN_HOST = '0.0.0.0'
RUN_PORT = int(os.environ.get('PORT', 8000))

BACKDOOR_ACCESS_KEY = 'nBheqThb8rw9-MJZLbnFRTMZ3!gc5cfeDyeQXh'
PROVIDER_SIGNATURE = 'eC^PCK#&W:eS<Un]k8n4sJf*)a_AnT,'
JWT_SECRET = 'pole=Risk2Numb!radio3Trophy$Movie@U7hs3rV3rS3CR31'

# grab the folder of the top-level directory of this project
UPLOADS_DEFAULT_DEST = APP_DIR + '/brain/static/uploads/'
UPLOADS_DEFAULT_URL = 'http://{}:{}/{}'.format(RUN_HOST, RUN_PORT, 'static/uploads/')

UPLOADED_IMAGES_DEST = APP_DIR + '/brain/static/uploads/images/'
UPLOADED_IMAGES_URL = 'http://{}:{}/{}'.format(RUN_HOST, RUN_PORT, 'static/uploads/images/')

REMEMBER_COOKIE_DURATION = datetime.timedelta(hours=24)
PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=10)
