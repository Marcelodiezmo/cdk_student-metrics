import json
import botocore
import boto3
import pymysql
import os

import constants
import parquet as parquet
import dao as dao
from student_progress_plan import StudentProgressPlan
from response_factory import ResponseFactory, ResponseError

s3 = boto3.client('s3')

def handler(event, context):
    print('PROGRESS PLAN LAMBDA STARTED')
    bucket = os.environ['bucket_name']
    student_param_id = get_param_id(event, constants.STUDENT_ID_PARAM)
    if student_param_id == None or student_param_id == '':
        response = ResponseError(400, 'Bad request, student id in path no found')
        print('ERROR: ', str(response))
        return exception_handler(response)
    
    try:
        int(student_param_id)
    except ValueError:
        response = ResponseError(400, 'Bad request, student id must be a numeric value')
        print('ERROR: ', str(response))
        return exception_handler(response)

    try:
        print('student_param_id: ' + (student_param_id))
        company_id = dao.get_company_id(student_param_id)
        print('company id: ' + str(company_id))
        path = constants.RESOURCE_PATH + (constants.RESOURCE_COMPANY_PATH.format(company_id = str(company_id)))
        print('key ' + path )
        print('Trying to read parquet Object')
        search_student = parquet.AccessParquet().pd_read_s3_multiple_parquets(
            path,
            bucket=bucket,
            filters=[(constants.USER_ID, '=', student_param_id)]
        )

        if not search_student.empty:
            search_student = search_student.iloc[0].to_dict()

        data = map_progress_plan(search_student)
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
    param_value = None
    try:
        param_value = str(event['pathParameters'][paramId])
    finally:
        return param_value


def map_progress_plan(record):
    student = StudentProgressPlan(
        user_id = int(record.get(constants.USER_ID)),
        progress_percent = float("{:.2f}".format(record.get(constants.PROGRESS_PERCENT, 0)))
    )
    return student

def exception_handler(response):
    if response.error_message == None or response.error_message == '':
        response.error_message = 'General Error'

    response = ResponseFactory.error_client(response.code, response).toJSON()
    
    return response
