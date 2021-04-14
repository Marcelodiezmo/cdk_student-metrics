class StudentProgressPlan:
    def __init__(self, user_id, progress_percent):
        self.user_id = user_id
        self.progress_percent = progress_percent

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)