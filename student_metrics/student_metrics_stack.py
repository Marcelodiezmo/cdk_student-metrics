from os import path
from aws_cdk import (
    aws_apigateway as _agw,
    aws_lambda as _lambda,
    aws_iam as _iam,
    core
)

from .stacks import (
    bucket_stack,
    lambda_stack
)


class StudentMetricsStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, stage: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get variables by stage
        shared_values = self.get_variables(self, stage)

        powerBI_values = self.get_power_bi_variables(self, stage)

        # Create the Bucket
        bucket_name = "student-metrics"

        if stage != "prod" and stage != "main":
            student_bucket = bucket_stack.bucketStack(self, f"{bucket_name}-{stage}", f"{bucket_name}-{stage}",
                                                      stage=stage)
        else:
            student_bucket = bucket_stack.bucketStack(self, bucket_name, bucket_name, stage=stage)

        # Create Lambdas
        course_month_lambda = lambda_stack.lambdaStack(self, 'course_month', lambda_name='course_month',
                                                       shared_values=shared_values, has_security=True)
        student_bucket.student_bucket.grant_read(course_month_lambda.student_lambda)

        most_popular_lambda = lambda_stack.lambdaStack(self, 'most_popular', lambda_name='most_popular',
                                                       shared_values=shared_values, has_security=True)
        student_bucket.student_bucket.grant_read(most_popular_lambda.student_lambda)

        ranking_company_lambda = lambda_stack.lambdaStack(self, 'ranking_company', lambda_name='ranking_company',
                                                          shared_values=shared_values, has_security=True)
        student_bucket.student_bucket.grant_read(ranking_company_lambda.student_lambda)

        finished_courses_lambda = lambda_stack.lambdaStack(self, 'finished_courses', lambda_name='finished_courses',
                                                           shared_values=shared_values, has_security=True)
        student_bucket.student_bucket.grant_read(finished_courses_lambda.student_lambda)

        progress_plan_lambda = lambda_stack.lambdaStack(self, 'progress_plan', lambda_name='progress_plan',
                                                        shared_values=shared_values, has_security=True)
        student_bucket.student_bucket.grant_read(progress_plan_lambda.student_lambda)

        company_lambda = lambda_stack.lambdaStack(self, 'company', lambda_name='company', shared_values=shared_values,
                                                  has_security=True)

        # dashboard_powerbi_lambda = lambda_stack.lambdaStack(self, 'dashboard_powerbi', lambda_name='dashboard_powerbi',
        #                                                     shared_values=shared_values, has_security=False)

        student_course_recommendations_lambda = lambda_stack.lambdaStack(self, 'student_course_recommendations',
                                                                         lambda_name='course_recommendations',
                                                                         shared_values=shared_values,
                                                                         has_security=False)
        put_student_course_recommendations_lambda = lambda_stack.lambdaStack(self, 'put_student_course_recommendations',
                                                                             lambda_name='put_course_recommendations',
                                                                             shared_values=shared_values,
                                                                             has_security=False)

        lambda_role = _iam.Role.from_role_arn(self, 'student_role', role_arn=shared_values['rol_arn'])
        lambda_layer = _lambda.LayerVersion.from_layer_version_attributes(self, 'student_layer',
                                                                          layer_version_arn=shared_values['layer_arn'])
        this_dir = path.dirname(__file__)
        
        dashboard_powerbi_lambda = _lambda.Function(
            self,
            'student_metrics_dashboard_powerbi',
            function_name='student_metrics_dashboard_powerbi',
            code=_lambda.Code.from_asset(path.join(this_dir, 'lambdas/dashboard_powerbi')),
            handler='app.handler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            description='Lambda for student metrics project',
            role=lambda_role,
            layers=[lambda_layer],
            environment={
                "WORKSPACE_ID": powerBI_values['WORKSPACE_ID'],
                "REPORT_ID": powerBI_values['REPORT_ID'],
                "TENANT_ID": powerBI_values['TENANT_ID'],
                "CLIENT_ID": powerBI_values['CLIENT_ID'],
                "CLIENT_SECRET": powerBI_values['CLIENT_SECRET'],
                "POWER_BI_USER": powerBI_values['POWER_BI_USER'],
                "POWER_BI_PASS": powerBI_values['POWER_BI_PASS']
            },
            timeout=core.Duration.seconds(16)
        )

        dashboard_powerbi_lambda.grant_invoke(_iam.ServicePrincipal('apigateway.amazonaws.com'))

        # Create the Api
        api_name = 'StudentMetrics'
        if stage == 'test':
            api_name = 'StudentMetrics_test'
        elif stage == 'main':
            api_name = 'StudentMetrics_main'

        api = _agw.RestApi(
            self,
            api_name,
            description='API for users metrics',
            deploy=False
        )

        # Main Resources
        user_resource = api.root.add_resource("users")
        metrics_resource = user_resource.add_resource("metrics")

        student_resource = api.root.add_resource("students")
        student_resource_by_id = student_resource.add_resource("{studentId}")
        students_metrics_resource_by_id = student_resource_by_id.add_resource("metrics")

        # Paths resources
        most_popular_resource = metrics_resource.add_resource("mostpopular")
        course_month_resource = metrics_resource.add_resource("coursemonth")
        ranking_company_resource = metrics_resource.add_resource("rankingcompany").add_resource("{companyId}")
        finished_courses_by_student_id_resource = students_metrics_resource_by_id.add_resource("finishedcourses")
        progress_plan_by_student_id_resource = students_metrics_resource_by_id.add_resource("progressplan")
        company_resource = student_resource.add_resource("companies")
        dashboard_powerbi_resource = student_resource.add_resource("dashboard")
        student_course_recommendations_resource = students_metrics_resource_by_id.add_resource("courses").add_resource(
            "recommendations")

        # Integrate API and courseMonth lambda
        course_month_integration = _agw.LambdaIntegration(course_month_lambda.student_lambda)

        # Integrate API and mostpopular lambda
        most_popular_integration = _agw.LambdaIntegration(most_popular_lambda.student_lambda)

        # Integrate API and rankingcompany lambda
        ranking_company_integration = _agw.LambdaIntegration(ranking_company_lambda.student_lambda)

        # Integrate API and finishedcourses lambda
        finished_courses_integration = _agw.LambdaIntegration(finished_courses_lambda.student_lambda)

        # Integrate API and progressplan lambda
        progress_plan_integration = _agw.LambdaIntegration(progress_plan_lambda.student_lambda)

        # Integrate API and company lambda
        company_integration = _agw.LambdaIntegration(
            company_lambda.student_lambda,
            request_parameters={
                "integration.request.querystring.studentid": "method.request.querystring.studentid",
                "integration.request.querystring.companyid": "method.request.querystring.companyid"
            }
        )

        # Integrate API and dashboard_powerbi lambda
        dashboard_powerbi_integration = _agw.LambdaIntegration(
            dashboard_powerbi_lambda,
            request_parameters={
                "integration.request.querystring.newtoken": "method.request.querystring.newtoken"
            }
        )

        # Integrate API and student_course_recommendations_lambda
        student_course_recommendations_integration = _agw.LambdaIntegration(
            student_course_recommendations_lambda.student_lambda,
        )

        # Integrate API and put_course_recommendations_lambda
        put_student_course_recommendations_integration = _agw.LambdaIntegration(
            put_student_course_recommendations_lambda.student_lambda,
        )

        course_month_resource.add_method(
            "GET",
            course_month_integration
        )

        ranking_company_resource.add_method(
            "GET",
            ranking_company_integration
        )

        finished_courses_by_student_id_resource.add_method(
            "GET",
            finished_courses_integration
        )

        progress_plan_by_student_id_resource.add_method(
            "GET",
            progress_plan_integration
        )

        most_popular_method = most_popular_resource.add_method(
            "GET",
            most_popular_integration
            # api_key_required=True
        )

        company_resource.add_method(
            "GET",
            company_integration,
            request_parameters={"method.request.querystring.studentid": False,
                                "method.request.querystring.companyid": False}
        )

        dashboard_powerbi_resource.add_method(
            "GET",
            dashboard_powerbi_integration,
            request_parameters={"method.request.querystring.newtoken": False}
            # api_key_required=True
        )

        student_course_recommendations_resource.add_method(
            "GET",
            student_course_recommendations_integration,
        )

        student_course_recommendations_resource.add_method(
            "POST",
            put_student_course_recommendations_integration,
        )

        # # key = api.add_api_key("ApiKey", api_key_name="studentMetricsKey")
        # #
        # # plan = api.add_usage_plan(
        # #     "UsagePlan",
        # #     name="Easy",
        # #     api_key=key,
        # #     throttle={
        # #         "rate_limit": 100,
        # #         "burst_limit": 50
        # #     }
        # # )
        # #
        # # plan.add_api_stage(
        # #     stage=api.deployment_stage,
        # #     throttle=[{
        # #         "method": most_popular_method,
        # #         "throttle": {
        # #             "rate_limit": 100,
        # #             "burst_limit": 50
        # #         }
        # #     }]
        # # )

        # Deployment
        if stage == 'test':
            deployment_test = _agw.Deployment(self, id='deployment_test', api=api)
            _agw.Stage(self, id='test_stage', deployment=deployment_test, stage_name='test')
        elif stage == 'dev':
            deployment_dev = _agw.Deployment(self, id='deployment_dev', api=api)
            _agw.Stage(self, id='dev_stage', deployment=deployment_dev, stage_name='dev')
        if stage == 'main':
            deployment_main = _agw.Deployment(self, id='deployment_main', api=api)
            _agw.Stage(self, id='main_stage', deployment=deployment_main, stage_name='main')
        else:
            deployment_prod = _agw.Deployment(self, id='deployment', api=api)
            _agw.Stage(self, id='prod_stage', deployment=deployment_prod, stage_name='v1')

    @staticmethod
    def get_variables(self, stage):
        shared_values = self.node.try_get_context('shared_values')

        if stage == 'test':
            return shared_values['test_values']
        elif stage == 'dev':
            return shared_values['dev_values']
        elif stage == 'prod':
            return shared_values['prod_values']
        elif stage == 'main':
            return shared_values['main_values']

    @staticmethod
    def get_power_bi_variables(self, stage):
        powerBI_values = self.node.try_get_context('powerBI_values')

        if stage == 'test':
            return powerBI_values['test_values']
        elif stage == 'dev':
            return powerBI_values['dev_values']
        elif stage == 'prod':
            return powerBI_values['prod_values']
        elif stage == 'main':
            return powerBI_values['main_values']
