import json
import botocore
import boto3
import os
import dao as dao
import constants

from response_factory import ResponseFactory, ResponseError
from course_values import CourseValues

s3 = boto3.client('s3')


def exception_handler(response):
    if response.error_message == None or response.error_message == '':
        response.error_message = 'General Error'

    response = ResponseFactory.error_client(response.code, response).toJSON()

    print(response)
    return response

def query_data(course_id):
    # try:
    return dao.get_course_name(course_id)
    # except Exception as e:
    #     response = ResponseError(404, e.args[0])
    #     print('ERROR: ', e.args[0])
    #     return exception_handler(response)


def handler(event, context):
    user=event['pathParameters']['mostpopular']
    print(event)
    
    bucket = os.environ['bucket_name']
    
    if user=='1':
        key = constants.KEY
    elif user=='0':
        key = constants.KEY2
        
    print(key)

    dataToReturn = []
    course_values = CourseValues()
    try:
        responseS3 = s3.get_object(Bucket=bucket, Key=key)
        content = responseS3['Body']
        jsonObject = json.loads(content.read())

        for record in jsonObject:
            course_values.courseId = record['course_id']
            course_values.courseFinish = record['finished_count']

            course_values.courseName = query_data(course_values.courseId)

            responseBody = {
                "course_id": course_values.courseId,
                "name": course_values.courseName,
                "finished_count": course_values.courseFinish
            }

            dataToReturn.append(responseBody)

        dataBody = {
            "data": dataToReturn
        }

        response = ResponseFactory.ok_status(dataBody)
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
