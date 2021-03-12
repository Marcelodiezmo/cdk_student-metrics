from aws_cdk import core
from os import path
from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as _agw,
    aws_s3 as _s3,
    aws_s3_deployment as _deploy,
    aws_ec2 as _ec2,
    aws_rds as _rds,
    aws_iam as _iam,
    core
)

from .stacks import (
    bucket_stack,
    lambda_stack
)


class StudentMetricsStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, stage:str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the Bucket
        student_bucket = bucket_stack.bucketStack(self, 'student-metrics-' + stage, 'student-metrics-' + stage)

        # Create Lambdas
        course_month_lambda = lambda_stack.lambdaStack(self, 'course_month', lambda_name='course_month', stage=stage)
        student_bucket.student_bucket.grant_read(course_month_lambda.student_lambda)

        most_popular_lambda = lambda_stack.lambdaStack(self, 'most_popular', lambda_name='most_popular', stage=stage)
        student_bucket.student_bucket.grant_read(most_popular_lambda.student_lambda)

        ranking_company_lambda = lambda_stack.lambdaStack(self, 'ranking_company', lambda_name='ranking_company', stage=stage)
        student_bucket.student_bucket.grant_read(ranking_company_lambda.student_lambda)

        finished_courses_lambda = lambda_stack.lambdaStack(self, 'finished_courses', lambda_name='finished_courses', stage=stage)
        student_bucket.student_bucket.grant_read(finished_courses_lambda.student_lambda)
        
        # Create the Api
        api_name = 'StudentMetrics'
        if stage == 'test':
            api_name = 'StudentMetrics_test'

        api = _agw.RestApi(
            self,
            api_name,
            description='API for users metrics',
            deploy= False
        )

        # Main Resources
        user_resource = api.root.add_resource("users")
        metrics_resource = user_resource.add_resource("metrics")

        # Paths resources
        most_popular_resource = metrics_resource.add_resource("mostpopular")
        course_month_resource = metrics_resource.add_resource("coursemonth")
        ranking_company_resource = metrics_resource.add_resource("rankingcompany").add_resource("{companyId}")
        finished_courses_resource = metrics_resource.add_resource("finishedcourses").add_resource("{studentId}")

        # Integrate API and courseMonth lambda
        course_month_integration = _agw.LambdaIntegration(course_month_lambda.student_lambda)

        # Integrate API and mostpopular lambda
        most_popular_integration = _agw.LambdaIntegration(most_popular_lambda.student_lambda)

        # Integrate API and rankingcompany lambda
        ranking_company_integration = _agw.LambdaIntegration(ranking_company_lambda.student_lambda)

        # Integrate API and finishedcourses lambda
        finished_courses_integration = _agw.LambdaIntegration(finished_courses_lambda.student_lambda)

        course_month_resource.add_method(
            "GET",
            course_month_integration
        )

        ranking_company_resource.add_method(
            "GET",
            ranking_company_integration
        )

        finished_courses_resource.add_method(
            "GET",
            finished_courses_integration
        )

        most_popular_method = most_popular_resource.add_method(
            "GET",
            most_popular_integration
            # api_key_required=True
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
        else:
            deployment_prod = _agw.Deployment(self, id='deployment', api=api)
            _agw.Stage(self, id='prod_stage', deployment=deployment_prod, stage_name='services')
