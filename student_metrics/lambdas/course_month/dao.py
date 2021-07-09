import pymysql
import os
from course import Course


def get_course_data(course_id):
    course = Course()
    course.courseId = course_id

    rds_host = os.environ['rds_host']
    db_user = os.environ['db_user']
    db_pass = os.environ['db_pass']
    db_name = os.environ['db_name']
    db_port = int(os.environ['db_port'])

    try:
        conn = pymysql.connect(host=rds_host, user=db_user, passwd=db_pass, db=db_name, port=db_port,
                               connect_timeout=25)

        cursor = conn.cursor()
        queryName = "select fullname, summary from mdl_course where id = " + str(course.courseId)
        queryDuration = "select course_duration_in_minutes from mdl_u_course_additional_info where id = " + str(
            course.courseId)
        queryModules = "select count(*) as modules from mdl_course_sections where course =  " + str(
            course.courseId) + " and (name not like '%ierre%' and name not like '%Introduc%') and (name like '%Bit%' or name like '%bit%') "
        queryIframe = "select content from mdl_page where course = " + str(
            course.courseId) + " and name like '%Bienvenida%'"

        cursor.execute(queryName)
        result = cursor.fetchall()
        course.courseName = str(result[0][0])
        course.courseDescription = str(result[0][1])

        cursor.execute(queryDuration)
        result = cursor.fetchall()

        if result:
            course.courseDuration = result[0][0]
        else:
            course.courseDuration = 0

        cursor.execute(queryModules)
        result = cursor.fetchall()

        if result:
            course.courseModules = result[0][0]
        else:
            course.courseModules = 0

        if course.courseType == 'Bit':
            cursor.execute(queryIframe)
            result = cursor.fetchall()

            if result:
                course.courseIframe = result[0][0]
            else:
                course.courseIframe = ''
        else:
            course.courseIframe = ''

        conn.close()
        return course

    except pymysql.Error as e:
        raise Exception(e.args[1])
