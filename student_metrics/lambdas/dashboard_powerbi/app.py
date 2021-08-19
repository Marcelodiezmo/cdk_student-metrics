from powerBI_client import PowerBIClientService
from response_factory import ResponseFactory, ResponseError


# Handle exception and create response http object
def exception_handler(e):
    if len(e.args) > 1:
        print('ERROR: ', e.args[0], e.args[1])
        response = ResponseError(e.args[0], e.args[1])
        response = ResponseFactory.error_client(response.code, response).toJSON()
    else:
        print('ERROR: ', e.args[0])
        response = ResponseError(500, e.args[0] if e.args[0] != '' else 'General Error')
        response = ResponseFactory.error_lambda(response).toJSON()

    return response


def getParam(event, param_name):
    try:
        return int(event["queryStringParameters"][param_name])
    except:
        return None

def handler(event, context):
    print("Init Lambda")
    try:
        new_token = getParam(event, 'newtoken')

        if new_token:
            response_body = PowerBIClientService().get_token(True)
        else:
            response_body = PowerBIClientService().get_token(False)

        response = ResponseFactory.ok_status(response_body).toJSON()
        print(response)

        return response
    except Exception as e:
        return exception_handler(e)