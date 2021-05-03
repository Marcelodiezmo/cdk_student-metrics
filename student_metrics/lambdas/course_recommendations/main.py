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
        query_recommendations = f'SELECT * FROM "analytics-prod"."s3_devbits_recommended" where id_usuario = {self.get_student_id()};'
        query_courses = '''SELECT course_id,
                            fullname,
                            course_summary,
                            cant_modules,
                            course_duration_in_minutes
                FROM "analytics-prod"."s3_devnew_kambits_parquet"
                WHERE course_id in {0};'''

        course_recommendations_df = self.request_athena_table(query_recommendations)

        if not course_recommendations_df.empty:
            course_recommendations_df = course_recommendations_df.to_dict('records')

            student_recommendations_data = {
                'student_id': str(course_recommendations_df[0]["id_usuario"]),
                'recommended_courses': []
            }

            tuple_of_curses = tuple([int(num) for num in course_recommendations_df[0]["recomendaciones"]])

            student_recommendations_data["recommended_courses"].append({
                "course_info": self.request_athena_table(query_courses.format(tuple_of_curses)).astype(str).to_dict(
                    'records')
            })

            return [student_recommendations_data]
        else:
            raise Exception("Dataframe in empty and data cannot be processed. Check your S3 bucket")

    def request_athena_table(self, query):
        # Athena Setup Config
        athena = pallas.setup(
            # AWS region, read from ~/.aws/config if not specified.
            region=None,
            # Athena (AWS Glue) database. Can be overridden in queries.
            database="ml_test_athena",
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
