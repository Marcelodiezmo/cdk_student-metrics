import json
import botocore
import boto3
import os

import constants
from student_finished_courses import StudentFinishedCourses
# from response_factory_utils import ResponseFactory, ResponseError
# from ..dashboard_powerbi.response_factory import ResponseFactory, ResponseError
from response_factory_utils import ResponseFactory, ResponseError

s3 = boto3.client('s3')

def exception_handler(response):
    if response.error_message == None or response.error_message == '':
        response.error_message = 'General Error'

    response = ResponseFactory.error_client(response.code, response).toJSON()
    
    print(response)
    return response

def handler(event, context):
    studen_param_id = get_param_id(event, constants.STUDENT_ID_PARAM)
    bucket = os.environ['bucket_name']
    path = constants.RESOURCE_PATH
    key = path + constants.RESOURCE_FILE_NAME

    try:
        responseS3 = s3.get_object(Bucket=bucket, Key=key)
        content = responseS3['Body']
        jsonObject = json.loads(content.read())
        data = get_data_from_json_object(jsonObject, studen_param_id)
        response = ResponseFactory.ok_status(json.dumps(data, default=obj_dict)).toJSON()

                    # 'body': json.dumps(response.data, default=obj_dict)

        return response

    except botocore.exceptions.ClientError as error:
        error_message = str(error.response['Error']['Message'])
        code = str(error.response['ResponseMetadata']['HTTPStatusCode'])
        response = ResponseError(code, error_message)
        return exception_handler(response)
    except Exception as e:
        response = ResponseError(404, e.args[0])
        print('ERROR: ', e.args[0])
        return exception_handler(response)

def obj_dict(obj):
    return obj.__dict__

        
def get_param_id(event, paramId):
    paramValue = None
    try:
        paramValue = str(event['pathParameters'][paramId])
    except Exception:
        paramValue = ''
    finally:
        return paramValue

def get_data_from_json_object(iterableList, studentIdParam):
    if(studentIdParam != ''):
        iterableList = filter(lambda record : str(record[constants.USER_ID]) == str(studentIdParam), iterableList)
    map_iterator = map(map_finished_courses, iterableList)
    return list(map_iterator)

def map_finished_courses(record):
    student = StudentFinishedCourses(
        record[constants.USER_ID], 
        record[constants.FINISHED_DATE],
        record.get(constants.FREE_COURSES_COUNT, 0),
        record.get(constants.MANDATORY_COURSES, 0),
        record[constants.COMPANY_ID]
    ).__dict__
    return student


    
def test_get_data_from_json_object():
    # path = "/lambdas/finished_courses/test/"
    filepath = 'C:/Desarrollo/Proyectos/Ubits/student-metrics/student_metrics/test/lambdas/finished_courses/resource/finished_courses.json'
    content = open(filepath + '', "r")
    json_object = json.loads(content.read())
    # result = get_data_from_json_object(json_object, 11969)
    result = get_data_from_json_object(json_object, '')
    response = ResponseFactory.ok_status(result).toJSON()
    # response = ResponseFactory.ok_status(json.dumps(data, default=obj_dict)).toJSON()
    
    print ('###################################')
    print(response)
    # print_iterator(result)
    # print(len(result))

def test_handler():
    param_id = ''
    event = {'pathParameters':{constants.STUDENT_ID_PARAM : param_id}}
    os.environ['bucket_name'] = 'student-metrics'
    result = handler(event, None)
    print (result)

    
def print_iterator(it):
    for x in it:
        print(x, end=' ')
    print('')  # for new line

if __name__ == '__main__':
    test_get_data_from_json_object()
    # test_handler()