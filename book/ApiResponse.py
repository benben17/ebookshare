from flask import Response, jsonify

class ApiException(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code

class CodeMap:
    success = 200
    created = 201
    bad_request = 400
    unauthorized = 401
    forbidden = 403
    not_found = 404
    internal_server_error = 500

class APIResponse:
    def __init__(self, data=None, msg='', code=CodeMap.success):
        self.data = data
        self.msg = msg
        self.code = code


    def to_dict(self):
        return {'code': self.code, 'data': self.data, 'msg': self.msg}

    def to_json(self, **kwargs):
        return jsonify(self.to_dict(), **kwargs)

    def __repr__(self):
        return f'<APIResponse {self.code}: {self.msg}>'

    @staticmethod
    def success(data=None, msg=''):
        return APIResponse(data=data, msg=msg, code=CodeMap.success).to_json()

    @staticmethod
    def created(data=None, msg=''):
        return APIResponse(data=data, msg=msg, code=CodeMap.created).to_json()

    @staticmethod
    def bad_request(data=None, msg=''):
        return APIResponse(data=data, msg=msg, code=CodeMap.bad_request).to_json()

    @staticmethod
    def unauthorized(data=None, msg=''):
        return APIResponse(data=data, msg=msg, code=CodeMap.unauthorized).to_json()

    @staticmethod
    def forbidden(data=None, msg=''):
        return APIResponse(data=data, msg=msg, code=CodeMap.forbidden).to_json()

    @staticmethod
    def not_found(data=None, msg=''):
        return APIResponse(data=data, msg=msg, code=CodeMap.not_found).to_json()

    @staticmethod
    def internal_server_error(data=None, msg=''):
        return APIResponse(data=data, msg=msg, code=CodeMap.internal_server_error).to_json()

    @staticmethod
    def handle_error(e):
        if isinstance(e, ApiException):
            return APIResponse.bad_request(msg=str(e))
        else:
            return APIResponse.internal_server_error(msg=str(e))
