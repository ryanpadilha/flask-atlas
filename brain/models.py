import json

from flask_login import UserMixin
from .util.library import epoch_to_date
from .integrations import build_service_unavailable_message_rest


class Credential(object):
    def __init__(self, provider, authorization, expires):
        self.provider = provider
        self.authorization = authorization
        self.expires = expires

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @classmethod
    def from_dict(cls, json_data):
        provider = json_data.get('provider')
        authorization = json_data.get('authorization')
        expires = json_data.get('expires')
        return Credential(provider=provider, authorization=authorization, expires=expires)

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)


class ErrorObject(object):
    def __init__(self, name, message, status_code, timestamp, issues):
        self.name = name
        self.message = message
        self.status_code = status_code
        self.timestamp = timestamp
        self.issues = issues

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @classmethod
    def throw_service_unavailable(cls, url):
        json_data = build_service_unavailable_message_rest(url)
        return ErrorObject.from_dict(json_data)

    @classmethod
    def from_dict(cls, json_data):
        name = json_data.get('name')
        message = json_data.get('message')
        status_code = json_data.get('status_code')
        timestamp = json_data.get('timestamp')
        issues = json_data.get('issues')
        return ErrorObject(name=name, message=message, status_code=status_code, timestamp=timestamp, issues=issues)

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)


class BaseModel(object):
    def __init__(self, credentials):
        self.credentials = credentials

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class AuthenticationObject(BaseModel):
    def __init__(self, username, password):
        self.username = username
        self.password = password


class UserObject(UserMixin):
    def __init__(self, internal, created, active, name, phone, document_main, username, password, user_email,
                 last_password_reset_date, file_name, file_url, company, occupation, roles):
        self.internal = internal
        self.created = created
        self.active = active
        self.name = name
        self.phone = phone
        self.document_main = document_main
        self.username = username
        self.password = password
        self.user_email = user_email
        self.last_password_reset_date = last_password_reset_date
        self.file_name = file_name
        self.file_url = file_url
        self.company = company
        self.occupation = occupation
        self.roles = roles

    def get_id(self):
        return self.internal

    @classmethod
    def from_dict(cls, json_data):
        internal = json_data.get('internal')
        created = json_data.get('created')
        active = json_data.get('active')
        name = json_data.get('name')
        phone = json_data.get('phone')
        document_main = json_data.get('document_main')
        username = json_data.get('username')
        password = json_data.get('password')
        user_email = json_data.get('user_email')
        last_password_reset_date = json_data.get('last_password_reset_date')
        file_name = json_data.get('file_name')
        file_url = json_data.get('file_url')
        company = json_data.get('company', '')
        occupation = json_data.get('occupation', '')
        type_role = json_data.get('roles')

        if isinstance(type_role, list):
            roles = []
            for g in type_role:
                roles.append(RoleObject.from_dict(g))
        else:
            roles = RoleObject.from_dict(type_role)

        return UserObject(internal=internal, created=created, active=active, name=name, phone=phone,
                          document_main=document_main, username=username, password=password, user_email=user_email,
                          last_password_reset_date=last_password_reset_date, file_name=file_name, file_url=file_url,
                          company=company, occupation=occupation, roles=roles)

    @classmethod
    def to_list_of_object(cls, json_data):
        if isinstance(json_data, list):
            collection = []
            for o in json_data:
                collection.append(UserObject.from_dict(o))
            return collection
        else:
            UserObject.from_dict(json_data)


class RoleObject(BaseModel):
    def __init__(self, name, type, description, internal=None, created=None):
        self.name = name
        self.type = type
        self.description = description
        self.internal = internal
        self.created = created

    @classmethod
    def from_dict(cls, json_data):
        name = json_data.get('name')
        type = json_data.get('type')
        description = json_data.get('description')
        internal = json_data.get('internal')
        created = epoch_to_date(json_data.get('created'))
        return RoleObject(name=name, type=type, description=description, internal=internal, created=created)

    @classmethod
    def to_list_of_object(cls, json_data):
        if isinstance(json_data, list):
            collection = []
            for o in json_data:
                collection.append(RoleObject.from_dict(o))
            return collection
        else:
            RoleObject.from_dict(json_data)


