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
    bucket = os.environ['bucket_name']
    print('PROGRESS PLAN LAMBDA STARTED')
    student_param_id = get_param_id(event, constants.STUDENT_ID_PARAM)
    print('student_param_id: ' + (student_param_id))
    company_id = dao.get_company_id(student_param_id)
    print('company id: ' + str(company_id))
    path = constants.RESOURCE_PATH + (constants.RESOURCE_COMPANY_PATH.format(company_id = str(company_id)))
    print('key ' + path )

    try:

        print('Trying to read parquet Object')
        df = parquet.AccessParquet().pd_read_s3_multiple_parquets(path, bucket=bucket)
        data = get_data_from_parquet_by_student_id(df, student_param_id)
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

def get_data_from_parquet_by_student_id(df, student_param_id):
    data = None
    search_company = df.loc[df[constants.USER_ID] == student_param_id]     
    if not search_company.empty:
        company_info = search_company.iloc[0].to_dict()
        data = map_progress_plan(company_info)
    return list(data)

def map_progress_plan(record):
    student = StudentProgressPlan(
        user_id=record[constants.USER_ID], 
        progress_percent=record.get(constants.PROGRESS_PERCENT, 0)
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
    param_id = '29043'
    event = {'pathParameters':{constants.STUDENT_ID_PARAM : param_id}}
    os.environ['bucket_name'] = 'student-metrics-dev'
    result = handler(event, None)
    print (result)

    
def print_iterator(it):
    for x in it:
        print(x, end=' ')
    print('')  # for new line

if __name__ == '__main__':
    # test_get_data_from_json_object()
    test_handler()
    
