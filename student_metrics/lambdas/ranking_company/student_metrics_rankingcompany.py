import json
import botocore
import boto3
import pymysql

s3 = boto3.client('s3')


class DataResponse:
    studentId = ''
    studentName = ''


class Response:
    code = 200
    error_message = ''
    data = DataResponse()


def exception_handler(response):
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
    rds_host = 'moodle-test-rds-aurora.cluster-c9maghmfm0zw.us-east-1.rds.amazonaws.com'
    db_user = 'moodle_dev_admin'
    db_pass = 'S2zhSJAw4ZNm'
    db_name = 'bitnami_moodle'
    db_port = 3036

    response = Response()

    # RDS connection
    try:
        conn = pymysql.connect(host=rds_host, user=db_user, passwd=db_pass, db=db_name, port=db_port,
                               connect_timeout=25)

        cursor = conn.cursor()
        queryName = "select concat_ws(' ', firstname, lastname) as name from mdl_user where id = " + str(data.studentId)

        cursor.execute(queryName)
        result = cursor.fetchall()

        if result:
            data.studentName = str(result[0][0])
        else:
            data.studentName = ''

        conn.close()
        response.data = data
        return response

    except pymysql.Error as e:
        response.code = e.args[0]
        response.error_message = e.args[1]
        return response


def handler(event, context):
    bucket = 'student-metrics'
    key = 'ranking-company.json'

    companyId = int(event['pathParameters']['companyId'])
    dataToSearch = DataResponse()
    response = Response()
    dataJson = []

    try:
        responseS3 = s3.get_object(Bucket=bucket, Key=key)
        content = responseS3['Body']
        jsonObject = json.loads(content.read())

        dataJson = list(filter(lambda x:x["company_id"] == companyId, jsonObject))

    except botocore.exceptions.ClientError as error:
        response.error_message = str(error.response['Error']['Message'])
        response.code = str(error.response['ResponseMetadata']['HTTPStatusCode'])
        return exception_handler(response)

    # Loop for search data in DB
    dataBody = {}
    dataToReturn = []
    try:
        for record in dataJson:
            dataToSearch.studentId = record['user_id']

            # search data
            responseQuery = queryData(dataToSearch)
            response.code = responseQuery.code
            response.error_message = responseQuery.error_message

            if response.code == 200:
                responseBody = {
                    "student_id": responseQuery.data.studentId,
                    "student_name": responseQuery.data.studentName
                }

                dataToReturn.append(responseBody)
            else:
                raise Exception

        dataBody = {
            "data": dataToReturn
        }

        return {
            'statusCode': response.code,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(dataBody)
        }
    except:
        response.code = 404
        return exception_handler(response)