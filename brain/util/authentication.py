from flask import session
from ..models import Credential
from ..default_settings import PROVIDER_SIGNATURE


class AuthHeader(object):
    @classmethod
    def set_credentials(cls, access_token, expires):
        if 'current_credentials' in session:
            session.pop('current_credentials', None)

        credentials = Credential(provider=PROVIDER_SIGNATURE, authorization=access_token, expires=expires).__dict__
        session['current_credentials'] = credentials

    @classmethod
    def get_credentials(cls):
        if 'current_credentials' in session:
            credentials = session['current_credentials']
            return Credential.from_dict(credentials)
        else:
            return Credential(provider=PROVIDER_SIGNATURE, authorization='', expires=0)
