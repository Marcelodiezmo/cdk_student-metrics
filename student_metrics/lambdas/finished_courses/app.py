import json
import botocore
import boto3
import pymysql
import os

s3 = boto3.client('s3')

STUDENT_ID_PARAM = 'studentId'

USER_ID = 'Id_Usuario'
FINISHED_DATE = 'Fecha_de_Finalizacion'
FREE_COURSES_COUNT = 'sum(Cursos_Obligatorios)'
MANDATORY_COURSES = 'sum(Cursos_Libres)'
COMPANY_ID = 'Id_Empresa'

class StudentFinishedCourses:
    user_id = ''
    finished_date = ''
    free_courses_count = 0
    mandatory_courses_count = 0
    company_id = ''

    # def __init__(self, user_id, finished_date, free_courses_count, mandatory_courses_count, company_id):
    #     self.user_id = user_id
    #     self.finished_date = finished_date
    #     self.free_courses_count = free_courses_count
    #     self.mandatory_courses_count = mandatory_courses_count
    #     self.company_id = company_id

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

class Response:
    code = 200
    error_message = ''
    data = []

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

    studentId = getParamId(STUDENT_ID_PARAM)

    course = Course()
    response = Response()
    responseQuery = {}
    responseBody = {}

    try:
        responseS3 = s3.get_object(Bucket=bucket, Key=key)
        content = responseS3['Body']
        jsonObject = json.loads(content.read())

        result = getDataFromJsonObject(jsonObject)


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

def getDataFromJsonObject(jsonObject, studentIdParam):
    if(studentIdParam != ''):
        result = filter(lambda record : find_student_by_id(record, studentIdParam), jsonObject)
        # print(type(result))
        # print_iterator(result)

    map_iterator = map(map_finished_courses, result)

    # print(type(map_iterator))
    # print_iterator(map_iterator)
    return map_iterator


def print_iterator(it):
    for x in it:
        print(x, end=' ')
    print('')  # for new line

def find_student_by_id(record, studentIdParam):
    return record[USER_ID] == studentIdParam

def map_finished_courses(record):
    print('MAPPING')
    student = StudentFinishedCourses()
    student.user_id = record[USER_ID]
    student.finished_date = record[FINISHED_DATE]
    student.free_courses_count = record.get(FREE_COURSES_COUNT, 0)
    student.mandatory_courses_count = record.get(MANDATORY_COURSES, 0)
    # student.free_courses_count = record[FREE_COURSES_COUNT]
    # student.mandatory_courses_count = record[MANDATORY_COURSES]
    student.company_id = record[COMPANY_ID]
    return student





##############################################
# TEST AREA
def testGetDataFromJsonObject():
    # path = "/lambdas/finished_courses/test/"
    filepath = 'C:/Desarrollo/Proyectos/Ubits/student-metrics/student_metrics/lambdas/finished_courses/test/finished_courses.json'
    content = open(filepath + '', "r")
    jsonObject = json.loads(content.read())
    result = getDataFromJsonObject(jsonObject, 11969)
    print(result)

if __name__ == '__main__':
    testGetDataFromJsonObject()
