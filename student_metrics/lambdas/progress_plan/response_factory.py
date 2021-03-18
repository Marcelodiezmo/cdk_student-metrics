from json import dumps


class ResponseError:
    def __init__(self, code, error_message):
        self.code = code
        self.error_message = error_message

    code = ''
    error_message = ''


class Response(object):

    def __init__(self, status_code: int):
        self.statusCode = status_code
        self.headers = {'Content-Type': 'application/json'}

    def toJSON(self):
        return {
            "statusCode": self.statusCode,
            "headers": self.headers,
            "body": dumps(self.body, default=self.obj_dict),
            "isBase64Encoded": False
        }
    
    def obj_dict(self, obj):
        return obj.__dict__


class ResponseFactory(Response):
    def __init__(self, status_code, body=None):
        super(ResponseFactory, self).__init__(status_code)
        self.body = body

    @classmethod
    def ok_status(cls, body):
        return cls(200, body)

    @classmethod
    def error_client(cls, status_code, body):
        return cls(status_code, body)

    @classmethod
    def error_lambda(cls, message=None):
        return cls(503, {"message": message if message else 'Internal Server Error'})
