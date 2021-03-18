import powerBI_client as PowerBIClient
from response_factory import ResponseFactory, ResponseError


def exception_handler(response):
    if response.error_message == None or response.error_message == '':
        response.error_message = 'General Error'

    response = ResponseFactory.error_client(response.code, response).toJSON()
    print(response)
    return response


def handler(event, context):
    print("Init Lambda")
    try:
        response_body = PowerBIClient.PowerBIClientService().get_dashboard_url()
        response = ResponseFactory.ok_status(response_body).toJSON()
        print(response)
        return response
    except Exception as e:
        response = ResponseError(e.args[0], e.args[1])
        print('ERROR: ', e.args[0], e.args[1])
        return exception_handler(response)