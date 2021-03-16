from ....lambdas.finished_courses.app import get_data_from_json_object
from ....lambdas.finished_courses.app import handler

def test_get_data_from_json_object():
    # path = "/lambdas/finished_courses/test/"
    filepath = 'C:/Desarrollo/Proyectos/Ubits/student-metrics/student_metrics/test/lambdas/finished_courses/resource/finished_courses.json'
    content = open(filepath + '', "r")
    json_object = json.loads(content.read())
    # result = get_data_from_json_object(json_object, 11969)
    result = get_data_from_json_object(json_object, '')
    print ('###################################')
    print_iterator(result)
    print(len(result))

def test_handler():
    param_id = ''
    event = {'pathParameters':{constants.STUDENT_ID_PARAM : param_id}}
    os.environ['bucket_name'] = 'student-metrics'
    result = handler(event, None)
    print (result)

    
def print_iterator(it):
    for x in it:
        print(x, end=' ')
    print('')  # for new line

if __name__ == '__main__':
    test_get_data_from_json_object()
    # test_handler()