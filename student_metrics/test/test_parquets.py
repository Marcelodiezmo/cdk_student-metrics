import boto3


def get_student_course_recommendations():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('recommendations')
    response = table.get_item(
        Key={
            'Id_Usuario': 16290
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
            'course_duration_in_minutes': int(float(item['course_duration_in_minutes'][i])),
            'course_progress': int(float(item['Porcentaje_de_Avance_Bit'][i]))
        })

    request_response = [{
        'user_id': int(item['Id_Usuario']),
        'recommended_courses': courses
    }]

    return request_response


if __name__ == '__main__':
    data = get_student_course_recommendations()
    print(data)
