import json
import botocore
import boto3
import os

import constants
from student_finished_courses import StudentFinishedCourses
from response_factory import ResponseFactory, ResponseError

s3 = boto3.client('s3')

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
        response = ResponseFactory.ok_status(data)

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
    )
    return student

def exception_handler(response):
    if response.error_message == None or response.error_message == '':
        response.error_message = 'General Error'

    response = ResponseFactory.error_client(response.code, response).toJSON()
    
    print(response)
    return response