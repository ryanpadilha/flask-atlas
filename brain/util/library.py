import os
import base64
import pytz

from flask import request
from uuid import uuid4
from werkzeug.utils import secure_filename
from flask_login import current_user
from dateutil.tz import tzlocal
from datetime import datetime
from jose import jwt
from ..default_settings import JWT_SECRET


def jwt_decode(token, secret_key=JWT_SECRET, algorithms='HS512'):
    options = {
        'verify_signature': False
    }

    decode_value = jwt.decode(token=token, key=secret_key, algorithms=algorithms,
                              options=options, audience='web', issuer='wplex-atlas-auth')
    return decode_value


def user_logged_in():
    return current_user.name if current_user is not None else 'REST-API'


def current_timestamp_tz():
    now = datetime.now().replace(tzinfo=tzlocal())
    return now.astimezone(pytz.timezone('America/Sao_Paulo'))


def current_request_ip():
    if 'X-Forwarded-For' in request.headers:
        remote_addr = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
    else:
        remote_addr = request.remote_addr or 'untrackable'

    return remote_addr


def epoch_to_date(value):
    if value:
        date = datetime.fromtimestamp(value).strftime('%d/%m/%Y %H:%M:%S')
        return date
    return None


def generate_secret_key():
    """
        Return a random URL-safe text string, in Base64 encoding.
        The string has *nbytes* random bytes.

    :return: secret key
    """
    token = os.urandom(32)
    key = base64.urlsafe_b64encode(token).rstrip(b'=').decode('ascii')
    return key
