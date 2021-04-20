class StudentFinishedCourses:
    def __init__(self, user_id, finished_date, free_courses_count, mandatory_courses_count, company_id):
        self.user_id = user_id
        self.finished_date = finished_date
        self.free_courses_count = free_courses_count
        self.mandatory_courses_count = mandatory_courses_count
        self.company_id = company_id

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)