import json
import botocore
import boto3
import pymysql
import os

import constants
from student_progress_plan import StudentProgressPlan
from response_factory import ResponseFactory, ResponseError

s3 = boto3.client('s3')

def handler(event, context):
    student_param_id = get_param_id(event, constants.STUDENT_ID_PARAM)
    bucket = os.environ['bucket_name']
    path = constants.RESOURCE_PATH
    key = path + constants.RESOURCE_FILE_NAME
    
    try:

        print('Trying read S3 Object')
        responseS3 = s3.get_object(Bucket=bucket, Key=key)
        content = responseS3['Body']
        print ('trying get body en content')
        jsonObject = json.loads(content.read())
        print ('trying get jsonObject')
        student_param_id = 50
        print(student_param_id)
        data = get_data_from_json_object_2(jsonObject, student_param_id)
        print(len(data))
        response = ResponseFactory.ok_status(data)
        print ('Data ')
        print (data)

        return response.toJSON()

    except botocore.exceptions.ClientError as error:
        error_message = str(error.response['Error']['Message'])
        code = str(error.response['ResponseMetadata']['HTTPStatusCode'])
        response = ResponseError(code, error_message)
        return exception_handler(response)
    except Exception as e:
        response = ResponseError(404, e.args[0])
        print('ERROR: ', e.args[0])
        return exception_handler(response)

def get_param_id(event, paramId):
    param_value = ''
    try:
        param_value = str(event['pathParameters'][paramId])
    finally:
        return param_value

def get_data_from_json_object_2(iterableList, studentIdParam):
    filtered_list = []
    if(studentIdParam != ''):
        for record in iterableList:
            if str(record[constants.USER_ID]) == str(studentIdParam):
                filtered_list.append(record) 
                break 
                
    map_iterator = map(map_finished_courses, filtered_list)
    return list(map_iterator)

def get_data_from_json_object(iterableList, studentIdParam):
    if(studentIdParam != ''):
        iterableList = filter(lambda record : str(record[constants.USER_ID]) == str(studentIdParam), iterableList)
    map_iterator = map(map_finished_courses, iterableList)
    return list(map_iterator)

def map_finished_courses(record):
    student = StudentProgressPlan(
        record[constants.USER_ID], 
        record.get(constants.PROGRESS_PERCENT, 0)
    )
    return student

def exception_handler(response):
    if response.error_message == None or response.error_message == '':
        response.error_message = 'General Error'

    response = ResponseFactory.error_client(response.code, response).toJSON()
    
    print(response)
    return response

def test_get_data_from_json_object():
    filepath = 'C:/Desarrollo/Proyectos/Ubits/student-metrics/student_metrics/test/lambdas/progress_plan/resource/progress_plan.json'
    content = open(filepath + '', "r")
    json_object = json.loads(content.read())
    # result = get_data_from_json_object(json_object, '')
    result = get_data_from_json_object_2(json_object, 50)
    print ('###################################')
    print_iterator(result)
    print(len(result))

def test_handler():
    param_id = '4340'
    event = {'pathParameters':{constants.STUDENT_ID_PARAM : param_id}}
    os.environ['bucket_name'] = 'student-metrics-dev'
    result = handler(event, None)
    print (result)

    
def print_iterator(it):
    for x in it:
        print(x, end=' ')
    print('')  # for new line

if __name__ == '__main__':
    test_get_data_from_json_object()
    # test_handler()
    
