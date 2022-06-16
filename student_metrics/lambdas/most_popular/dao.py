import pymysql
import os


def get_course_name(course_id):


        # Create a Secrets Manager client and values
    #secret_values = secret.get_secret(os.environ['secret_name'], 'us-east-1')
    #data = json.loads(secret_values)

    rds_host = os.environ['rds_host']
    db_user = os.environ['db_user']
    db_pass = os.environ['db_pass']
    db_name = os.environ['db_name']
    db_port = int(os.environ['db_port'])

    try:
        conn = pymysql.connect(host=rds_host, user=db_user, passwd=db_pass, db=db_name, port=db_port,
                               connect_timeout=25)

        cursor = conn.cursor()
        queryName = "select fullname from mdl_course where id = " + str(course_id)

        cursor.execute(queryName)
        result = cursor.fetchall()
        courseName = str(result[0][0])

        conn.close()
        return courseName

    except pymysql.Error as e:
        raise Exception(e.args[1])
