import json
import requests

from flask import current_app as app
from ..models import UserObject, RoleObject, ErrorObject
from ..util.authentication import AuthHeader
from ..util.enums import RequestMethod

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
    def __init__(self, credentials, timeout=120):
        self.credentials = credentials
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

    def invoke_request(self, request_method, url, data=None, **kwargs):
        try:
            result = []
            if data:
                data = data.encode('utf-8')

            r = requests.Response()
            app.logger.info('invoke request url: {}'.format(url))

            if request_method == RequestMethod.GET:
                r = requests.get(url=url, headers=self.headers(), allow_redirects=False, timeout=self.timeout, **kwargs)
            elif request_method == RequestMethod.POST:
                r = requests.post(url=url, data=data, headers=self.headers(), allow_redirects=False, verify=False, **kwargs)
            elif request_method == RequestMethod.PUT:
                r = requests.put(url=url, data=data, headers=self.headers(), allow_redirects=False, verify=False, **kwargs)
            elif request_method == RequestMethod.DELETE:
                r = requests.delete(url=url, data=data, headers=self.headers(), allow_redirects=False, verify=False, **kwargs)

            r.raise_for_status()

            if r.content:
                result = json.loads(r.content.decode('utf-8'))
        except requests.exceptions.Timeout as e:
            app.logger.error('Timeout Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=url)
        except requests.exceptions.HTTPError as e:
            app.logger.error('HTTP Error Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=url)
        except requests.exceptions.ConnectionError as e:
            app.logger.error('ConnectionError Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=url)
        except requests.exceptions.RequestException as e:
            app.logger.error('Request Exception: {}'.format(e))
            return self.parser_response_error(response=r, url=url)

        return result


class LoginResource(IntegrationResource):
    def __init__(self):
        super(LoginResource, self).__init__(credentials=AuthHeader.get_credentials())

    def authentication(self, data):
        return self.invoke_request(request_method=RequestMethod.POST, url=API_USER['login'], data=data)


class UserResource(IntegrationResource):
    def __init__(self):
        super(UserResource, self).__init__(credentials=AuthHeader.get_credentials())

    def list(self):
        obj = self.invoke_request(RequestMethod.GET, url=API_USER['list'])
        return [] if isinstance(obj, ErrorObject) else UserObject.to_list_of_object(obj)

    def get_by_internal(self, internal):
        obj = self.invoke_request(RequestMethod.GET, url=API_USER['get_by_internal'].format(internal))
        return obj if isinstance(obj, ErrorObject) else UserObject.from_dict(obj)

    def find_by_username(self, username):
        obj = self.invoke_request(RequestMethod.GET, url=API_USER['find_by_username'].format(username))
        return obj if isinstance(obj, ErrorObject) else UserObject.from_dict(obj)

    def persist(self, data):
        obj = self.invoke_request(RequestMethod.POST, url=API_USER['persist'], data=data)
        return obj if isinstance(obj, ErrorObject) else UserObject.from_dict(obj)

    def update(self, internal, data):
        return self.invoke_request(RequestMethod.PUT, url=API_USER['update'].format(internal), data=data)

    def delete_entity(self, internal):
        return self.invoke_request(RequestMethod.DELETE, url=API_USER['delete'].format(internal))


class RoleResource(IntegrationResource):
    def __init__(self):
        super(RoleResource, self).__init__(credentials=AuthHeader.get_credentials())

    def list(self):
        obj = self.invoke_request(RequestMethod.GET, url=API_USER_GROUP['list'])
        return [] if isinstance(obj, ErrorObject) else RoleObject.to_list_of_object(obj)

    def get_by_internal(self, internal):
        obj = self.invoke_request(RequestMethod.GET, url=API_USER_GROUP['get_by_internal'].format(internal))
        return obj if isinstance(obj, ErrorObject) else RoleObject.from_dict(obj)

    def persist(self, data):
        obj = self.invoke_request(RequestMethod.POST, url=API_USER_GROUP['persist'], data=data)
        return obj if isinstance(obj, ErrorObject) else RoleObject.from_dict(obj)

    def update(self, internal, data):
        return self.invoke_request(RequestMethod.PUT, url=API_USER_GROUP['update'].format(internal), data=data)

    def delete_entity(self, internal):
        return self.invoke_request(RequestMethod.DELETE, url=API_USER_GROUP['delete'].format(internal))
