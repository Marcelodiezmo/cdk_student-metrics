import json
import boto3
import pymysql

s3 = boto3.client('s3')
def handler(event, context):
    bucket = 'student-metrics'
    key = 'courseMonth.json'

    rds_host = 'moodle-dev-rds-aurora.cluster-c9maghmfm0zw.us-east-1.rds.amazonaws.com'
    user_name = 'moodle_dev_admin'
    passwd = 'S2zhSJAw4ZNm'
    db_name = 'bitnami_moodle'

    response = s3.get_object(Bucket=bucket, Key=key)
    content = response['Body']
    jsonObject = json.loads(content.read())

    course_id = jsonObject['course_id']
    finished_count = jsonObject['finished_count']

    print("El id del curso es " + str(course_id))
    print("el total de terminados es " + str(finished_count))

    # RDS connection
    try:
        conn = pymysql.connect(rds_host, user=user_name, passwd=passwd, db=db_name, connect_timeout=5)
        print("Conexion exitosa!!")
    except pymysql.MySQLError as e:
        print("ERROR: Unexpected error: Could not connect to MySQL instance.")
        print("El error es " + e)

    # Construct the body of the response object
    responseBody = {
        "course": course_id,
        "finish": finished_count
    }

    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(responseBody)
    }

    return response