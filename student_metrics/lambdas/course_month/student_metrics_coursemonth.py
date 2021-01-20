import json
import botocore
import boto3
import pymysql

s3 = boto3.client('s3')

class Response:
    code = 200
    error_message = ''
    course_id = ''
    name = ''
    description = ''
    duration = ''
    modules = ''
    iframe = ''
    contenido = ''

class Course:
    courseId = ''
    courseFinish = 0
    courseName = ''
    courseDescription = ''
    courseDuration = ''
    courseModules = ''
    courseIframe = ''
    courseType = ''

def queryData(course):
    rds_host = 'moodle-test-rds-aurora.cluster-c9maghmfm0zw.us-east-1.rds.amazonaws.com'
    db_user = 'moodle_dev_admin'
    db_pass = 'S2zhSJAw4ZNm'
    db_name = 'bitnami_moodle'
    db_port = 3036

    response = {}

    response['code'] = 200
    response['message'] = ''

    # RDS connection
    try:
        conn = pymysql.connect(host=rds_host, user=db_user, passwd=db_pass, db=db_name, port=db_port, connect_timeout=25)
    except pymysql.Error as e:
        response['code'] = e.args[0]
        response['message'] = e.args[1]

    cursor = conn.cursor()
    queryName = "select fullname, summary from mdl_course where id = " + str(course.courseId)
    queryDuration = "select course_duration_in_minutes from mdl_u_course_additional_info where id = " + str(course.courseId)
    queryModules = "select count(*) as modules from mdl_course_modules where course = " + str(course.courseId) + " and deletioninprogress = 0 and visible = 1"
    queryIframe = "select content from mdl_page where course = " + str(course.courseId) + " and name like '%Bienvenida%'"

    try:
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

        # print(course.__dict__)

    except:
        response['code'] = 404
        response['message']="Error searching data"

    conn.close()

    response['course'] = course
    return response

def handler(event, context):
    bucket = 'student-metrics'
    key = 'courseMonth.json'

    course = Course()
    response = Response()
    responseQuery = {}

    try:
        responseS3 = s3.get_object(Bucket=bucket, Key=key)
        content = responseS3['Body']

        jsonObject = json.loads(content.read())
        courseObject = jsonObject[0]

        course_id = courseObject['course_id']
        finished_count = courseObject['finished_count']
        contenido = courseObject['Contenido']

        course.courseId = course_id
        course.courseFinish = finished_count
        course.courseType = contenido
    except botocore.exceptions.ClientError as error:
        response.error_message = str(error.response['Error']['Message'])
        response.code = str(error.response['ResponseMetadata']['HTTPStatusCode'])

    if not response.error_message:
        responseQuery = queryData(course)
        response.code = responseQuery['code']
        response.error_message = responseQuery['message']

        if not response.error_message:
            course = responseQuery['course']
            response.course_id = course.courseId
            response.name = course.courseName
            response.description = course.courseDescription
            response.duration = course.courseDuration
            response.modules = course.courseModules
            response.iframe = course.courseIframe
            response.contenido = course.courseType
        else:
            response.course_id = ''
            response.name = ''
            response.description = ''
            response.duration = ''
            response.modules = ''
            response.iframe = ''
            response.contenido = ''
    else:
        print('un error')

    responseBody = {
        "code": response.code,
        "error_message": response.error_message,
        "course_id": response.course_id,
        "name": response.name,
        "description": response.description,
        "duration": response.duration,
        "modules": response.modules,
        "iframe": response.iframe,
        "contenido": response.contenido
    }

    # respuesta = {
    #     'statusCode': response.code,
    #     'message': response.error_message,
    #     'headers': {
    #         'Content-Type': 'application/json'
    #     },
    #     'body': json.dumps(responseBody)
    # }

    return {
        'statusCode': response.code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(responseBody)
    }