import boto3
from io import StringIO
import json
import constants
import csv


class Main:
    @staticmethod
    def build_file(body):
        print("Entra en build")
        json_object = json.loads(body)

        carousel_index = json_object['carouselIndex']
        user_id = json_object['userId']
        user_agent = json_object['userAgent']
        course_id = json_object['courseId']
        date_time = json_object['dateTime']

        si = StringIO()
        cw = csv.writer(si)
        cw.writerow([carousel_index, user_id, user_agent, course_id, date_time])
        print(si.getvalue().strip('\r\n'))
        return si.getvalue().strip('\r\n')


    @staticmethod
    def put_file(body):
        print("Entra en put")

        client = boto3.resource('s3')
        bucket = constants.bucket

        response = client.Object(bucket, constants.path + '/test.csv').put(Body=body)
        print(response["ResponseMetadata"]["HTTPStatusCode"])

        return response["ResponseMetadata"]["HTTPStatusCode"]

    @staticmethod
    def validate_body(body):
        print("Entra en validate")
        json_object = json.loads(body)

        for key in constants.json_keys:
            if key not in json_object:
                raise Exception(f"The key {str(key)} not found")
