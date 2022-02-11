import pymysql
import os
import base64
import secret
import json

def get_course_data(course):

    # Create a Secrets Manager client and values
    secret_values = secret.get_secret(os.environ['secret_name'], 'us-east-1')
    data = json.loads(secret_values)

    # Use with AWS Secret Manager
    rds_host = data['host']
    db_user = data['username']
    db_pass = data['password']
    db_name = os.environ['db_name']
    db_port = int(data['port'])

    #rds_host = os.environ['rds_host']
    #db_user = os.environ['db_user']
    #db_pass = os.environ['db_pass']
    #db_name = os.environ['db_name']
    #db_port = int(os.environ['db_port'])

    try:
        conn = pymysql.connect(host=rds_host, user=db_user, passwd=db_pass, db=db_name, port=db_port,
                               connect_timeout=25)

        cursor = conn.cursor()
        queryName = "select fullname, summary from mdl_course where id = " + str(course.courseId)

        queryDuration = f"""
                        SELECT mbi.configdata
                        FROM mdl_course mc
                            LEFT JOIN mdl_context mc2 ON mc2.instanceid = mc.id AND contextlevel = 50
                            LEFT JOIN mdl_block_instances mbi ON mbi.parentcontextid = mc2.id
                        WHERE mc.category != 0
                        And mbi.blockname like '%_course_features'
                        And mbi.configdata != ''
                        And mc2.instanceid = {str(course.courseId)}"""

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
            duration_encode = result[0][0]
            duration_decode = base64.b64decode(duration_encode)
            print(duration_decode)
            course.courseDuration = duration_decode
        else:
            course.courseDuration = "0"

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
