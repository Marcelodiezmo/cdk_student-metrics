import response_factory
import main

main_functions = main.Main()


def exception_handler(e):
    if len(e.args) > 1:
        print('ERROR: ', e.args[0], e.args[1])
        response = response_factory.ResponseError(e.args[0], e.args[1])
        response = response_factory.error_client(response.code, response).toJSON()
    else:
        print('ERROR: ', e.args[0])
        response = response_factory.ResponseError(500, e.args[0] if e.args[0] != '' else 'General Error')
        response = response_factory.ResponseFactory.error_lambda(response).toJSON()

    return response


def handler(event, context):
    try:
        body = event['body']

        main_functions.validate_body(body)
        file = main_functions.build_file(body)

        response_body = main_functions.put_file(file)
        response = response_factory.ResponseFactory.ok_status(response_body).toJSON()
        return response

    except Exception as e:
        return exception_handler(e)
