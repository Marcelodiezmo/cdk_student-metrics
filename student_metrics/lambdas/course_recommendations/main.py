import pallas


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
        query_recommendations = f'SELECT * FROM "analytics-prod"."s3_devbits_recommended" where id_usuario = {user_id};'

        course_recommendations_df = self.request_athena_table(query_recommendations)

        print("La info de Athena es ")
        print(course_recommendations_df.to_dict('records'))

        if not course_recommendations_df.empty:
            course_recommendations_df = course_recommendations_df.to_dict('records')

            response_course = []
            for course in course_recommendations_df[0]["recomendaciones"]:
                query_course = f'''SELECT course_id,
                            fullname,
                            course_summary,
                            cant_modules,
                            course_duration_in_minutes
                FROM "analytics-prod"."s3_devnew_kambits_parquet"
                WHERE course_id = {course};'''

                response_course.append(self.request_athena_table(query_course).astype(str).to_dict('records'))


            finalResults = []
            for i in range(0,len(response_course)): finalResults.append(response_course[i][0])

            student_recommendations_data = {
                'student_id': str(course_recommendations_df[0]["id_usuario"]),
                'recommended_courses': [
                    {"course_info": finalResults}
                ]
            }

            return [student_recommendations_data]
        else:
            raise Exception("Dataframe in empty and data cannot be processed. Check your S3 bucket")

    def request_athena_table(self, query):
        # Athena Setup Config
        athena = pallas.setup(
            # AWS region, read from ~/.aws/config if not specified.
            region=None,
            # Athena (AWS Glue) database. Can be overridden in queries.
            database="analytics-prod",
            # Athena workgroup. Will use default workgroup if omitted.
            workgroup=None,
            # Athena output location, will use workgroup default location if omitted.
            output_location="s3://analytics-athena-results-query-test/analytics/",
            # Optional query execution cache.
            cache_remote="s3://analytics-athena-results-query-test/cache/",
            # Optional query result cache.
            # Normalize white whitespace for better caching. Enabled by default.
            normalize=True,
            # Kill queries on KeybordInterrupt. Enabled by default.
            kill_on_interrupt=True
        )
        return athena.execute(query).to_df()
