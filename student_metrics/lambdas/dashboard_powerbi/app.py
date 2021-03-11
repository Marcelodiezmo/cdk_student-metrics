import APIPowerBIClient as PowerBIClient
from response_factory import ResponseFactory, ResponseError
import json


def exception_handler(response):
    if response.error_message == None or response.error_message == '':
        response.error_message = 'General Error'

    response = ResponseFactory.error_client(response.code, response.__dict__).toJSON()
    print(response)
    return response


def handler(event, context):
    print("Init Lambda")
    try:
        response_body = PowerBIClient.PowerBIClientService().get_url_dashboard()
        response = ResponseFactory.ok_status(json.dumps(response_body)).toJSON()
        return response
    except Exception as e:
        response = ResponseError(404, e.args)
        print('ERROR: ', e.args)
        return exception_handler(response)

handler()