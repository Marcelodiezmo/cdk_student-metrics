import json
import botocore
import boto3
import pymysql
import os

s3 = boto3.client('s3')


class DataResponse:
    courseId = ''
    courseName = ''
    courseFinish = ''


class Response:
    code = 200
    error_message = ''
    data = DataResponse()


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

def queryData(data):
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
        queryName = "select fullname from mdl_course where id = " + str(data.courseId)

        cursor.execute(queryName)
        result = cursor.fetchall()
        data.courseName = str(result[0][0])

        conn.close()
        response.data = data
        return response

    except pymysql.Error as e:
        response.code = e.args[0]
        response.error_message = e.args[1]
        return response


def handler(event, context):
    bucket = 'student-metrics'
    key = 'most-popular-bits.json'

    dataToSearch = DataResponse()
    response = Response()
    responseQuery = {}
    responseBody = {}
    jsonObject = []

    try:
        responseS3 = s3.get_object(Bucket=bucket, Key=key)
        content = responseS3['Body']
        jsonObject = json.loads(content.read())

    except botocore.exceptions.ClientError as error:
        response.error_message = str(error.response['Error']['Message'])
        response.code = str(error.response['ResponseMetadata']['HTTPStatusCode'])
        return exception_handler(response)
    except Exception:
        response.code = 404
        return exception_handler(response)

    # Loop for search data in BD
    dataBody = {}
    dataToReturn = []
    try:
        for record in jsonObject:
            dataToSearch.courseId = record['course_id']
            dataToSearch.courseFinish = record['finished_count']

            # search data
            responseQuery = queryData(dataToSearch)
            response.code = responseQuery.code
            response.error_message = responseQuery.error_message

            if response.code == 200:
                responseBody = {
                    "course_id": responseQuery.data.courseId,
                    "name": responseQuery.data.courseName,
                    "finished_count": responseQuery.data.courseFinish
                }

                dataToReturn.append(responseBody)

            else:
                raise Exception

        dataBody = {
            "data": dataToReturn
        }

        # print(dataToReturn)
        return {
            'statusCode': response.code,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(dataBody)
        }
    except Exception:
        response.code = 404
        return exception_handler(response)