# from .student_finished_courses import getDataFromJsonObject
import json
import os

def testGetDataFromJsonObject():
    # path = "/lambdas/finished_courses/test/"
    filepath = 'C:/Desarrollo/Proyectos/Ubits/student-metrics/student_metrics/lambdas/finished_courses/test/finished_courses.json'
    content = open(filepath + '', "r")
    jsonObject = json.loads(content.read())
    getDataFromJsonObject(jsonObject, '11969')



if __name__ == '__main__':
    print('Hello Test')
    testGetDataFromJsonObject()