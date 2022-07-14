import pymysql
import os
from student_values import StudentValues


def get_student_name(student_id):
    rds_host = os.environ['rds_host']
    db_user = os.environ['db_user']
    db_pass = os.environ['db_pass']
    db_name = os.environ['db_name']
    db_port = int(os.environ['db_port'])

    try:
        conn = pymysql.connect(host=rds_host, user=db_user, passwd=db_pass, db=db_name, port=db_port,
                               connect_timeout=25)

        cursor = conn.cursor()
        queryName = "select concat_ws(' ', firstname, lastname) as name from mdl_user where id = " + str(student_id)

        cursor.execute(queryName)
        result = cursor.fetchall()

        if result:
            studentName = str(result[0][0])
        else:
            studentName = ''

        conn.close()
        return studentName

    except pymysql.Error as e:
        raise Exception(e.args[1])
