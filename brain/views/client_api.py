import json
import requests

from flask import current_app as app
from ..models import UserObject, RoleObject, ErrorObject


mode = ''

if mode == 'prd':
    from ..prd_instance import config
    API_BASE_URL = config.API_BASE_URL
else:
    from ..dev_instance import config
    API_BASE_URL = config.API_BASE_URL


API_USER = {
    'login': API_BASE_URL + '/api/v1/auth/login',
    'find_by_username': API_BASE_URL + '/api/v1/auth/users/search/?username={}',
    'list': API_BASE_URL + '/api/v1/auth/users',
    'get_by_internal': API_BASE_URL + '/api/v1/auth/users/{}',
    'persist': API_BASE_URL + '/api/v1/auth/users',
    'update': API_BASE_URL + '/api/v1/auth/users/{}',
    'delete': API_BASE_URL + '/api/v1/auth/users/{}',
}

API_USER_GROUP = {
    'list': API_BASE_URL + '/api/v1/auth/roles',
    'get_by_internal': API_BASE_URL + '/api/v1/auth/roles/{}',
    'persist': API_BASE_URL + '/api/v1/auth/roles',
    'update': API_BASE_URL + '/api/v1/auth/roles/{}',
    'delete': API_BASE_URL + '/api/v1/auth/roles/{}',
}


class IntegrationResource(object):
    def __init__(self, credentials, url=None, timeout=120):
        self.credentials = credentials
        self.url = url
        self.timeout = timeout

    def headers(self):
        return {
            'content-type': 'application/json',
            'xf-provider-signature': self.credentials.provider,
            'Authorization': 'Bearer {}'.format(self.credentials.authorization)
        }

    @classmethod
    def parser_response_error(cls, response, url=None):
        content = response.content.decode('utf-8') if response.content else None
        if content:
            result = json.loads(content)
            return ErrorObject.from_dict(result)
        return ErrorObject.throw_service_unavailable(url)

    def get(self, **kwargs):
        try:
            result = []
            r = requests.Response()
            r = requests.get(url=self.url, headers=self.headers(), allow_redirects=False, timeout=self.timeout, **kwargs)
            r.raise_for_status()

            if r.content:
                result = json.loads(r.content.decode('utf-8'))
        except requests.exceptions.Timeout as e:
            app.logger.error('Timeout Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=self.url)
        except requests.exceptions.HTTPError as e:
            app.logger.error('HTTP Error Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=self.url)
        except requests.exceptions.ConnectionError as e:
            app.logger.error('ConnectionError Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=self.url)
        except requests.exceptions.RequestException as e:
            app.logger.error('Request Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=self.url)

        return result

    def post(self, data=None, **kwargs):
        try:
            result = []
            if data:
                data = data.encode('utf-8')

            r = requests.Response()
            r = requests.post(url=self.url, data=data, headers=self.headers(),
                              allow_redirects=False, verify=False, **kwargs)
            r.raise_for_status()

            if r.content:
                result = json.loads(r.content.decode('utf-8'))
        except requests.exceptions.Timeout as e:
            app.logger.error('Timeout Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=self.url)
        except requests.exceptions.HTTPError as e:
            app.logger.error('HTTP Error Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=self.url)
        except requests.exceptions.ConnectionError as e:
            app.logger.error('ConnectionError Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=self.url)
        except requests.exceptions.RequestException as e:
            app.logger.error('Request Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=self.url)

        return result

    def put(self, data=None, **kwargs):
        try:
            result = []
            if data:
                data = data.encode('utf-8')

            r = requests.Response()
            r = requests.put(url=self.url, data=data, headers=self.headers(),
                             allow_redirects=False, verify=False, **kwargs)
            r.raise_for_status()

            if r.content:
                result = json.loads(r.content.decode('utf-8'))
        except requests.exceptions.Timeout as e:
            app.logger.error('Timeout Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=self.url)
        except requests.exceptions.HTTPError as e:
            app.logger.error('HTTP Error Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=self.url)
        except requests.exceptions.ConnectionError as e:
            app.logger.error('ConnectionError Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=self.url)
        except requests.exceptions.RequestException as e:
            app.logger.error('Request Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=self.url)

        return result

    def delete(self, data=None, **kwargs):
        try:
            result = []
            if data:
                data = data.encode('utf-8')

            r = requests.Response()
            r = requests.delete(url=self.url, data=data, headers=self.headers(),
                                allow_redirects=False, verify=False, **kwargs)
            r.raise_for_status()

            if r.content:
                result = json.loads(r.content.decode('utf-8'))
        except requests.exceptions.Timeout as e:
            app.logger.error('Timeout Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=self.url)
        except requests.exceptions.HTTPError as e:
            app.logger.error('HTTP Error Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=self.url)
        except requests.exceptions.ConnectionError as e:
            app.logger.error('ConnectionError Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=self.url)
        except requests.exceptions.RequestException as e:
            app.logger.error('Request Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=self.url)

        return result


class LoginResource(IntegrationResource):
    def __init__(self, credentials):
        super(LoginResource, self).__init__(credentials)

    def authentication(self, data):
        self.url = API_USER['login']
        return self.post(data=data)


class UserResource(IntegrationResource):
    def __init__(self, credentials):
        super(UserResource, self).__init__(credentials)

    def find_by_username(self, username):
        self.url = API_USER['find_by_username'].format(username)
        data = self.get()
        return UserObject.from_dict(data)

    def list(self):
        self.url = API_USER['list']
        collection = self.get()
        return UserObject.to_list_of_object(collection)

    def get_by_internal(self, internal):
        self.url = API_USER['get_by_internal'].format(internal)
        data = self.get()
        return UserObject.from_dict(data)

    def persist(self, data):
        self.url = API_USER['persist']
        data = self.post(data=data)

        return UserObject.from_dict(data)

    def update(self, internal, data):
        self.url = API_USER['update'].format(internal)
        obj = self.put(data=data)
        return UserObject.from_dict(obj)

    def delete_entity(self, internal):
        self.url = API_USER['delete'].format(internal)
        return self.delete()


class RoleResource(IntegrationResource):
    def __init__(self, credentials):
        super(RoleResource, self).__init__(credentials)

    def list(self):
        self.url = API_USER_GROUP['list']
        obj = self.get()
        return [] if isinstance(obj, ErrorObject) else RoleObject.to_list_of_object(obj)

    def get_by_internal(self, internal):
        self.url = API_USER_GROUP['get_by_internal'].format(internal)
        obj = self.get()
        return obj if isinstance(obj, ErrorObject) else RoleObject.from_dict(obj)

    def persist(self, data):
        self.url = API_USER_GROUP['persist']
        obj = self.post(data=data)
        return obj if isinstance(obj, ErrorObject) else RoleObject.from_dict(obj)

    def update(self, internal, data):
        self.url = API_USER_GROUP['update'].format(internal)
        return self.put(data=data)

    def delete_entity(self, internal):
        self.url = API_USER_GROUP['delete'].format(internal)
        return self.delete()
