import boto3
import pymongo
import os

s3 = boto3.client('s3')


class Main:
    def __init__(self, student_id=None):
        self._student_id = student_id

    def set_student_id(self, student_id):
        print("El id a asignar es ", student_id)
        self._student_id = student_id

    def get_student_id(self):
        return self._student_id

    @staticmethod
    def get_param(event, event_type, param_name):
        return int(event[event_type][param_name])

    def get_student_course_recommendations(self, student_id):
        user_id = self.get_student_id()

        conn_str = "mongodb://" + os.environ['mongodb_user'] + ":" + os.environ['mongodb_password'] + \
            "@" + os.environ['mongodb_ip'] + "/" + os.environ['mongodb_db'] + "?retryWrites=true&w=majority"
        client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
        db = client[os.environ['mongodb_db']]

        item = []
        for x in db.recommendations.find({'Id_Usuario': int(user_id)}):
            item.append(x)

        if not item:
            for x in db.recommendations.find({'Id_Usuario': 0}):
                item.append(x)

        courses=[]
        for i in range(0, len(item[0]['course_id'])):
            courses.append({
                'course_id': int(item[0]['course_id'][i]),
                'fullname': item[0]['fullname'][i],
                'course_summary': item[0]['course_summary'][i],
                'cant_modules': int(float(item[0]['numero_secciones'][i])),
                'course_duration_in_minutes': (item[0]['course_duration_in_minutes'][i]),
                'course_progress': int(float(item[0]['Porcentaje_de_Avance_Bit'][i]))
            })

        request_response = [{
            'student_id': int(item[0]['Id_Usuario']),
            'recommended_courses': courses
        }]
        return request_response

