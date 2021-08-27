import json
import botocore
import boto3
import os
import dao as dao
import constants

from response_factory import ResponseFactory, ResponseError
from course import Course
from phpserialize import *


s3 = boto3.client('s3')


def exception_handler(response):
    if response.error_message == None or response.error_message == '':
        response.error_message = 'General Error'

    response = ResponseFactory.error_client(response.code, response).toJSON()

    print(response)
    return response


def query_data(course):
    # try:
    return dao.get_course_data(course)
    # except Exception as e:
    #     response = ResponseError(404, e.args[0])
    #     print('ERROR: ', e.args[0])
    #     return exception_handler(response)


def unserialize_php(serialized_obj):
    data = loads(serialized_obj, decode_strings=True, object_hook=phpobject)
    return data


def format_iframe(original_iframe):
    index_iframe_1 = original_iframe.index("<iframe")
    index_iframe_2 = original_iframe.index("</iframe>")

    iframe = original_iframe[index_iframe_1:index_iframe_2]

    index_http_1 = iframe.index("https://")
    index_http_2 = iframe.index("?")

    final_iframe = iframe[index_http_1:index_http_2]

    return final_iframe


def handler(event, context):
    bucket = os.environ['bucket_name']
    key = constants.KEY

    print(bucket)
    print(key)

    course = Course()
    try:
        responseS3 = s3.get_object(Bucket=bucket, Key=key)

        content = responseS3['Body']
        jsonObject = json.loads(content.read())

        for record in jsonObject:
            course.courseId = record['course_id']
            course.courseType = record['Contenido']

        course = query_data(course)

        # unserialize PHP for course_duration
        if course.courseDuration != "0":
            course_info = unserialize_php(course.courseDuration)
            course.courseDuration = course_info.duration

        if course.courseIframe != "":
            course.courseIframe = format_iframe(course.courseIframe)

        responseBody = {
            "course_id": course.courseId,
            "name": course.courseName,
            "description": course.courseDescription,
            "duration": course.courseDuration,
            "modules": course.courseModules,
            "iframe": course.courseIframe,
            "contenido": course.courseType
        }


        response = ResponseFactory.ok_status(responseBody)
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
