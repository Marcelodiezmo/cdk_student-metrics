import json
import botocore
import boto3
import pymysql
import os

import constants
from student_finished_courses import StudentFinishedCourses
from response import Response

s3 = boto3.client('s3')

def exception_handler(response):
    if response.error_message == None or response.error_message == '':
        response.error_message = 'General Error'

    responseBody = {
        "code": response.code,
        "error_message": response.error_message,
    }

    return {
        'statusCode': response.code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(responseBody)
    }

def handler(event, context):
    studen_param_id = get_param_id(event, constants.STUDENT_ID_PARAM)
    bucket = os.environ['bucket_name']
    path = constants.RESOURCE_PATH
    key = path + constants.RESOURCE_FILE_NAME

    response = Response()

    try:
        responseS3 = s3.get_object(Bucket=bucket, Key=key)
        content = responseS3['Body']
        jsonObject = json.loads(content.read())
        response.data = get_data_from_json_object(jsonObject, studen_param_id)

        response =  {
            'statusCode': response.code,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(response.data, default = obj.__dict__)
        }

        return response

    except botocore.exceptions.ClientError as error:
        response.error_message = str(error.response['Error']['Message'])
        response.code = str(error.response['ResponseMetadata']['HTTPStatusCode'])
        return exception_handler(response)
    except Exception:
        response.code = 404
        return exception_handler(response)

        
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
    )
    return student
