import json
import botocore
import boto3
import pymysql

s3 = boto3.client('s3')


class Course:
    courseId = ''
    courseName = ''
    courseDescription = ''
    courseDuration = ''
    courseModules = ''
    courseIframe = ''
    courseType = ''


class Response:
    code = 200
    error_message = ''
    course = Course()


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

def queryData(course):
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
        queryName = "select fullname, summary from mdl_course where id = " + str(course.courseId)
        queryDuration = "select course_duration_in_minutes from mdl_u_course_additional_info where id = " + str(course.courseId)
        queryModules = "select count(*) as modules from mdl_course_modules where course = " + str(course.courseId) + " and deletioninprogress = 0 and visible = 1"
        queryIframe = "select content from mdl_page where course = " + str(course.courseId) + " and name like '%Bienvenida%'"

        cursor.execute(queryName)
        result = cursor.fetchall()
        course.courseName = str(result[0][0])
        course.courseDescription = str(result[0][1])

        cursor.execute(queryDuration)
        result = cursor.fetchall()
        course.courseDuration = result[0][0]

        cursor.execute(queryModules)
        result = cursor.fetchall()
        course.courseModules = result[0][0]

        if course.courseType == 'Bit':
            cursor.execute(queryIframe)
            result = cursor.fetchall()
            course.courseIframe = result[0][0]
        else:
            course.courseIframe = ''


        conn.close()
        response.course = course
        return response

    except pymysql.Error as e:
        response.code = e.args[0]
        response.error_message = e.args[1]
        return response


def handler(event, context):
    bucket = 'student-metrics'
    key = 'courseMonth.json'

    course = Course()
    response = Response()
    responseQuery = {}
    responseBody = {}

    try:
        responseS3 = s3.get_object(Bucket=bucket, Key=key)
        content = responseS3['Body']
        jsonObject = json.loads(content.read())

        for record in jsonObject:
            course.courseId = record['course_id']
            course.courseType = record['Contenido']

    #try:
        responseQuery = queryData(course)
        response.code = responseQuery.code
        response.error_message = responseQuery.error_message

        if response.code == 200:
            course = responseQuery.course

            responseBody = {
                "course_id": course.courseId,
                "name": course.courseName,
                "description": course.courseDescription,
                "duration": course.courseDuration,
                "modules": course.courseModules,
                "iframe": course.courseIframe,
                "contenido": course.courseType
            }

            return {
                'statusCode': response.code,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(responseBody)
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
