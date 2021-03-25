import pymysql
import os
import secret
import json


def get_company_id(student_id):
    rds_host = os.environ['rds_host']
    db_user = os.environ['db_user']
    db_pass = os.environ['db_pass']
    db_name = os.environ['db_name']
    db_port = int(os.environ['db_port'])

    try:
        conn = pymysql.connect(host=rds_host, user=db_user, passwd=db_pass, db=db_name, port=db_port,
                               connect_timeout=25)
        cursor = conn.cursor()

        query = """Select muuai.mdl_u_company_id As companyId 
                        From mdl_user mu
                        Inner Join mdl_u_user_additional_info muuai on mu.id = muuai.mdl_user_id
                    Where mu.id = """ + str(student_id) + ";"

        cursor.execute(query)
        result = cursor.fetchall()

        if result:
            return result[0][0]
        else:
            raise Exception("Error searching the company id")

        conn.close()

    except pymysql.Error as e:
        raise Exception(e.args[1])
