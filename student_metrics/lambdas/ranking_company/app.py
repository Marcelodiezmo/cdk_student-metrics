import json
import botocore
import boto3
import os
import dao as dao
import constants

from response_factory import ResponseFactory, ResponseError
from student_values import StudentValues

s3 = boto3.client('s3')


def exception_handler(response):
    if response.error_message == None or response.error_message == '':
        response.error_message = 'General Error'

    response = ResponseFactory.error_client(response.code, response).toJSON()

    print(response)
    return response


def query_data(student_id):
    # try:
    return dao.get_student_name(student_id)
    # except Exception as e:
    #     response = ResponseError(404, e.args[0])
    #     print('ERROR: ', e.args[0])
    #     return exception_handler(response)


def handler(event, context):
    bucket = os.environ['bucket_name']
    key = constants.KEY

    dataToReturn = []
    student_values = StudentValues()
    company_id = int(event['pathParameters']['companyId'])

    try:
        responseS3 = s3.get_object(Bucket=bucket, Key=key)
        content = responseS3['Body']
        jsonObject = json.loads(content.read())

        dataJson = list(filter(lambda x: x["company_id"] == company_id, jsonObject))

        for record in dataJson:
            student_values.studentId = record['user_id']
            student_values.studentName = query_data(student_values.studentId)

            if student_values.studentName != '':
                responseBody = {
                    "student_id": student_values.studentId,
                    "student_name": student_values.studentName
                }
                dataToReturn.append(responseBody)
            else:
                raise Exception('Estudiante no encontrado')

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
