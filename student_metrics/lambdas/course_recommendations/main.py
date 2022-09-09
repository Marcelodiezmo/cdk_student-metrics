import pymongo
import random
import pandas as pd
import pymysql
import os 

def get_realtime_recommendations(cursor, userId,recommendations):
    recommendations = [str(recommendation) for recommendation in recommendations]
    # GET MODULES PER COURSES
    query = f"SELECT id,course FROM mdl_course_modules WHERE completion > 0 AND deletioninprogress = 0 AND course IN({','.join(recommendations)})"
    cursor.execute(query)
    result = cursor.fetchall()
    courses_modules_recommended = pd.DataFrame(columns=["modules","course"],data=result).groupby("course", as_index=False).agg(set)

    query = f"SELECT coursemoduleid FROM mdl_course_modules_completion WHERE userId={userId} AND completionstate>0 AND timemodified > unix_timestamp(DATE_SUB(CURDATE(), INTERVAL 365 DAY))"
    cursor.execute(query)
    result = cursor.fetchall()
    modules_finished = [x[0] for x in result]

    courses_modules_recommended["modules_finished"] = [set(modules_finished)] * len(courses_modules_recommended)
    courses_modules_recommended["finished"] = courses_modules_recommended["modules"] -  courses_modules_recommended["modules_finished"]
    courses_modules_recommended["finished"] = courses_modules_recommended["finished"].apply(len)
    recomendations_final = courses_modules_recommended.loc[courses_modules_recommended["finished"]>0]["course"].tolist()
    
    return recomendations_final

class Main:
    def __init__(self, student_id=None, number_recomendations=10):
        self._student_id = student_id
        self._number_recomendations = number_recomendations

    def set_student_id(self, student_id):
        print("El id a asignar es ", student_id)
        self._student_id = student_id

    def set_number_recomendations(self, number_recomendations):
        print("El número de recomendaciones es ", number_recomendations)
        if (number_recomendations <= 15) & (number_recomendations >= 1):
            self._number_recomendations = number_recomendations
        else:
            self._number_recomendations = 10
            

    def get_student_id(self):
        return self._student_id
        
    def get_number_recomendations(self):
        return self._number_recomendations

    @staticmethod
    def get_param(event, event_type, param_name):
        return int(event[event_type][param_name])

    def get_student_course_recommendations(self, student_id, number_recomendations):
        user_id = self.get_student_id()
        number_recomendations = self.get_number_recomendations()
        rds_host = os.environ['rds_host']
        db_user = os.environ['db_user']
        db_pass = os.environ['db_pass']
        db_name = os.environ['db_name']
        db_port = int(os.environ['db_port'])

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
              
            
        temp_recommendations = [course["course_id"] for course in courses] # Ids totales

        # GET REALTIME RECOMMENDATIONS
        
        # CREATE CONNECTION
        conn = pymysql.connect(host=rds_host, user=db_user, passwd=db_pass, db=db_name, port=db_port,
                                       connect_timeout=25)
        
        cursor = conn.cursor()
        
        # CALL FUNCTION
        filtered_recommendations = get_realtime_recommendations(cursor,user_id,temp_recommendations) # cleaned recommendations
        number_filteredrecommendations = len(filtered_recommendations) # number of not completed recommendations
        if number_recomendations <= number_filteredrecommendations:
            final_recommendations = random.sample(filtered_recommendations, k=number_recomendations)
        else:
            completed_courses = list(set(temp_recommendations)-set(filtered_recommendations))
            completed_recommendations = random.sample(completed_courses, k=number_recomendations-number_filteredrecommendations)
            final_recommendations = filtered_recommendations+completed_recommendations
            
        final_recommendations = [course for course in courses if course['course_id'] in final_recommendations]
        courses = final_recommendations
            
        request_response = [{
            'student_id': int(item[0]['Id_Usuario']),
            'recommended_courses': courses
        }]
        return request_response
