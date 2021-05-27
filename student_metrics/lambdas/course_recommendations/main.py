import boto3

s3 = boto3.client('s3')


class Main:

    def __init__(self, student_id=None):
        self._student_id = student_id

    def set_student_id(self, student_id):
        self._student_id = student_id

    def get_student_id(self):
        return self._student_id

    @staticmethod
    def get_param(event, event_type, param_name):
        return int(event[event_type][param_name])

    def get_student_course_recommendations(self):
        user_id = self.get_student_id()
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('recommendations')
        response = table.get_item(
            Key={
                'Id_Usuario': int(user_id)
            }
        )

        if 'Item' not in response:
            response = table.get_item(
                Key={
                    'Id_Usuario': 0
                }
            )

        item = response['Item']

        courses = []

        for i in range(0, len(item['course_id'])):
            courses.append({
                'course_id': int(item['course_id'][i]),
                'fullname': item['fullname'][i],
                'course_summary': item['course_summary'][i],
                'cant_modules': int(float(item['numero_secciones'][i])),
                'course_duration_in_minutes': int(float(item['course_duration_in_minutes'][i]))
            })

        request_response = [{
            'student_id': int(item['Id_Usuario']),
            'recommended_courses': courses
        }]
        print(request_response)
        return request_response
