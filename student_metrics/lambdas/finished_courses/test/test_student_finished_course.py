import json
import os

from ..app import get_data_from_json_object

def testGetDataFromJsonObject():
    # path = "/lambdas/finished_courses/test/"
    filepath = 'C:/Desarrollo/Proyectos/Ubits/student-metrics/student_metrics/lambdas/finished_courses/test/finished_courses.json'
    content = open(filepath + '', "r")
    jsonObject = json.loads(content.read())
    result = get_data_from_json_object(jsonObject, 11969)
    # result = getDataFromJsonObject(jsonObject, '')
    print ('###################################')
    print_iterator(result)
    print(len(result))

    
def print_iterator(it):
    for x in it:
        print(x, end=' ')
    print('')  # for new line

if __name__ == '__main__':
    testGetDataFromJsonObject()