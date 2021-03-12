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


def getParamId(event, paramId):
    paramValue = None
    try:
        paramValue = str(event['pathParameters'][paramId])
    except Exception:
        paramValue = ''
    finally:
        return paramValue
    

def handler(event, context):
    bucket = os.environ['bucket_name']
    path = 'students/finished_courses/'
    key = path + 'finished_courses.json'
    studen_param_id = getParamId(event, constants.STUDENT_ID_PARAM)

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
    student = StudentFinishedCourses(
        record[constants.USER_ID], 
        record[constants.FINISHED_DATE],
        record.get(constants.FREE_COURSES_COUNT, 0),
        record.get(constants.MANDATORY_COURSES, 0),
        record[constants.COMPANY_ID]
    )
    return student




##############################################
# TEST AREA
def test_get_data_from_json_object():
    # path = "/lambdas/finished_courses/test/"
    filepath = 'C:/Desarrollo/Proyectos/Ubits/student-metrics/student_metrics/lambdas/finished_courses/test/finished_courses.json'
    content = open(filepath + '', "r")
    json_object = json.loads(content.read())
    # result = get_data_from_json_object(json_object, 11969)
    handler()
    # result = get_data_from_json_object(json_object, '')
    print ('###################################')
    print_iterator(result)
    print(len(result))

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
    # test_get_data_from_json_object()
    test_handler()
    
