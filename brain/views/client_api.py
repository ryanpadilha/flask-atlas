import json
import requests

from flask import current_app as app
from ..models import UserObject, RoleObject, ErrorObject
from ..util.authentication import AuthHeader
from ..util.enums import RequestMethod


class ApiResource(object):
    def __init__(self):
        self.api_url_backend = app.config['API_URL_BACKEND']

    def get_user(self):
        return {
            'login': self.api_url_backend + '/api/v1/auth/login',
            'find_by_username': self.api_url_backend + '/api/v1/auth/users/search/?username={}',
            'list': self.api_url_backend + '/api/v1/auth/users',
            'get_by_internal': self.api_url_backend + '/api/v1/auth/users/{}',
            'persist': self.api_url_backend + '/api/v1/auth/users',
            'update': self.api_url_backend + '/api/v1/auth/users/{}',
            'delete': self.api_url_backend + '/api/v1/auth/users/{}',
        }

    def get_user_group(self):
        return {
            'list': self.api_url_backend + '/api/v1/auth/roles',
            'get_by_internal': self.api_url_backend + '/api/v1/auth/roles/{}',
            'persist': self.api_url_backend + '/api/v1/auth/roles',
            'update': self.api_url_backend + '/api/v1/auth/roles/{}',
            'delete': self.api_url_backend + '/api/v1/auth/roles/{}',
        }


class IntegrationResource(object):
    def __init__(self, credentials, api_dict, timeout=120):
        self.credentials = credentials
        self.api_dict = api_dict
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
        super(LoginResource, self).__init__(credentials=AuthHeader.get_credentials(), api_dict=ApiResource().get_user())

    def authentication(self, data):
        return self.invoke_request(request_method=RequestMethod.POST, url=self.api_dict.get('login'), data=data)


class UserResource(IntegrationResource):
    def __init__(self):
        super(UserResource, self).__init__(credentials=AuthHeader.get_credentials(), api_dict=ApiResource().get_user())

    def list(self):
        obj = self.invoke_request(RequestMethod.GET, url=self.api_dict.get('list'))
        return [] if isinstance(obj, ErrorObject) else UserObject.to_list_of_object(obj)

    def get_by_internal(self, internal):
        obj = self.invoke_request(RequestMethod.GET, url=self.api_dict.get('get_by_internal').format(internal))
        return obj if isinstance(obj, ErrorObject) else UserObject.from_dict(obj)

    def find_by_username(self, username):
        obj = self.invoke_request(RequestMethod.GET, url=self.api_dict.get('find_by_username').format(username))
        return obj if isinstance(obj, ErrorObject) else UserObject.from_dict(obj)

    def persist(self, data):
        obj = self.invoke_request(RequestMethod.POST, url=self.api_dict.get('persist'), data=data)
        return obj if isinstance(obj, ErrorObject) else UserObject.from_dict(obj)

    def update(self, internal, data):
        return self.invoke_request(RequestMethod.PUT, url=self.api_dict.get('update').format(internal), data=data)

    def delete_entity(self, internal):
        return self.invoke_request(RequestMethod.DELETE, url=self.api_dict.get('delete').format(internal))


class RoleResource(IntegrationResource):
    def __init__(self):
        super(RoleResource, self).__init__(credentials=AuthHeader.get_credentials(),
                                           api_dict=ApiResource().get_user_group())

    def list(self):
        obj = self.invoke_request(RequestMethod.GET, url=self.api_dict.get('list'))
        return [] if isinstance(obj, ErrorObject) else RoleObject.to_list_of_object(obj)

    def get_by_internal(self, internal):
        obj = self.invoke_request(RequestMethod.GET, url=self.api_dict.get('get_by_internal').format(internal))
        return obj if isinstance(obj, ErrorObject) else RoleObject.from_dict(obj)

    def persist(self, data):
        obj = self.invoke_request(RequestMethod.POST, url=self.api_dict.get('persist'), data=data)
        return obj if isinstance(obj, ErrorObject) else RoleObject.from_dict(obj)

    def update(self, internal, data):
        return self.invoke_request(RequestMethod.PUT, url=self.api_dict.get('update').format(internal), data=data)

    def delete_entity(self, internal):
        return self.invoke_request(RequestMethod.DELETE, url=self.api_dict.get('delete').format(internal))
