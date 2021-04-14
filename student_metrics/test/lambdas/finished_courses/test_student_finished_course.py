def test_get_data_from_json_object():
    # path = "/lambdas/finished_courses/test/"
    filepath = 'C:/Desarrollo/Proyectos/Ubits/student-metrics/student_metrics/test/lambdas/finished_courses/resource/finished_courses.json'
    content = open(filepath + '', "r")
    json_object = json.loads(content.read())

    try:
        result = get_data_from_json_object(json_object, 35442)
        # result = get_data_from_json_object(json_object, None)

        response = ResponseFactory.ok_status(result).toJSON()

        print ('###################################')
        print(response)
        # print_iterator(result)
        # print(len(result))
    except Exception as e:
        response = ResponseError(404, e.args[0])
        print('ERROR: ', e.args[0])
        return exception_handler(response)

def test_handler():
    param_id = None
    event = {'pathParameters':{constants.STUDENT_ID_PARAM : param_id}}
    os.environ['bucket_name'] = 'student-metrics-dev'
    result = handler(event, None)
    print (result)

    
def print_iterator(it):
    for x in it:
        print(x, end=' ')
    print('')  # for new line

if __name__ == '__main__':
    test_get_data_from_json_object()
    # test_handler()
