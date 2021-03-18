
def test_get_data_from_json_object():
    filepath = 'C:/Desarrollo/Proyectos/Ubits/student-metrics/student_metrics/test/lambdas/progress_plan/resource/progress_plan.json'
    content = open(filepath + '', "r")
    json_object = json.loads(content.read())
    result = get_data_from_json_object(json_object, '')
    # result = get_data_from_json_object(json_object, 3051)
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
    
