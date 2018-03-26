from enum import Enum


class FlashMessagesCategory(Enum):
    MESSAGE = 'message'
    ERROR = 'error'
    INFO = 'info'
    WARNING = 'warning'


class RequestMethod(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
