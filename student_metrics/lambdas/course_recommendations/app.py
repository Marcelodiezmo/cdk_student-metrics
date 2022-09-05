import boto3
import main
import response_factory

s3 = boto3.client('s3')
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
        student_id = main_functions.get_param(event, event_type='pathParameters', param_name='studentId')
        main_functions.set_student_id(student_id=student_id)
        
        # Just in case not number of recommendations are provided return 10
        try: number_recomendations = main_functions.get_param(event, event_type='queryStringParameters', param_name='n')
        except Exception as e: number_recomendations = 10
            
        main_functions.set_number_recomendations(number_recomendations=number_recomendations)     

        response_body = main_functions.get_student_course_recommendations(student_id=student_id,number_recomendations=number_recomendations)
        response = response_factory.ResponseFactory.ok_status(response_body).toJSON()
        return response

    except Exception as e:
        return exception_handler(e)
