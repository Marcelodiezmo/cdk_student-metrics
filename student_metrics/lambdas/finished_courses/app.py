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


def queryData(studentId):
    rds_host = os.environ['rds_host']
    db_user = os.environ['db_user']
    db_pass = os.environ['db_pass']
    db_name = os.environ['db_name']
    db_port = int(os.environ['db_port'])

    response = Response()

    # RDS connection
    try:
        conn = pymysql.connect(host=rds_host, user=db_user, passwd=db_pass, db=db_name, port=db_port,
                               connect_timeout=25)

        cursor = conn.cursor()
        queryName = constants.STUDENT_QUERY_BY_USERID.format(student_id = str(studentId))

        cursor.execute(queryName)
        result = cursor.fetchall()
        conn.close()

        if result:
            queryData = str(result[0][0])
        else:
            queryData = ''
        
        return queryData

    except pymysql.Error as e:
        response.code = e.args[0]
        response.error_message = e.args[1]
        return response

def getParamId(paramId):
    paramValue = None
    try:
        paramValue = str(event['pathParameters'][paramId])
    except Exception:
        paramValue = ''
    finally:
        return paramValue
    

def handler(event, context):
    bucket = os.environ['bucket_name']
    key = 'finished_courses.json'

    response = Response()

    try:
        responseS3 = s3.get_object(Bucket=bucket, Key=key)
        content = responseS3['Body']
        jsonObject = json.loads(content.read())
        response.data = getDataFromJsonObject(jsonObject)

        if response.code == 200:
            course = responseQuery.course

            return {
                'statusCode': response.code,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(response.data)
            }
        else:
            raise Exception

    except botocore.exceptions.ClientError as error:
        response.error_message = str(error.response['Error']['Message'])
        response.code = str(error.response['ResponseMetadata']['HTTPStatusCode'])
        return exception_handler(response)
    except Exception:
        response.code = 404
        return exception_handler(response)

def getDataFromJsonObject(iterableList, studentIdParam):
    if(studentIdParam != ''):
        iterableList = filter(lambda record : find_student_by_id(record, studentIdParam), iterableList)
    map_iterator = map(map_finished_courses, iterableList)
    return list(map_iterator)

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
def testGetDataFromJsonObject():
    # path = "/lambdas/finished_courses/test/"
    filepath = 'C:/Desarrollo/Proyectos/Ubits/student-metrics/student_metrics/lambdas/finished_courses/test/finished_courses.json'
    content = open(filepath + '', "r")
    jsonObject = json.loads(content.read())
    result = getDataFromJsonObject(jsonObject, 11969)
    # result = getDataFromJsonObject(jsonObject, '')
    print ('###################################')
    print_iterator(result)
    print(len(result))

    
def print_iterator(it):
    for x in it:
        print(x, end=' ')
    print('')  # for new line

if __name__ == '__main__':
    testGetDataFromJsonObject()
