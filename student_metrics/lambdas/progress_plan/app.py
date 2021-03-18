import json
import botocore
import boto3
import pymysql
import os

import constants
from student_progress_plan import StudentProgressPlan
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


def get_param_id(event, paramId):
    paramValue = None
    try:
        paramValue = str(event['pathParameters'][paramId])
    except Exception:
        paramValue = ''
    finally:
        return paramValue
    

def handler(event, context):
    studen_param_id = get_param_id(event, constants.STUDENT_ID_PARAM)
    bucket = os.environ['bucket_name']
    path = 'students/progress_training_plan/'
    key = path + 'progress_plan.json'

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
            'body': json.dumps(response.data, default=obj_dict)
        }

        return response

    except botocore.exceptions.ClientError as error:
        response.error_message = str(error.response['Error']['Message'])
        response.code = str(error.response['ResponseMetadata']['HTTPStatusCode'])
        return exception_handler(response)
    except Exception:
        response.code = 404
        return exception_handler(response)

def get_data_from_json_object(iterableList, studentIdParam):
    if(studentIdParam != ''):
        iterableList = filter(lambda record : find_student_by_id(record, studentIdParam), iterableList)
    map_iterator = map(map_finished_courses, iterableList)
    return list(map_iterator)


def obj_dict(obj):
    return obj.__dict__
    
def find_student_by_id(record, studentIdParam):
    return str(record[constants.USER_ID]) == str(studentIdParam)

def map_finished_courses(record):
    student = StudentProgressPlan(
        record[constants.USER_ID], 
        record.get(constants.PROGRESS_PERCENT, 0)
    )
    return student