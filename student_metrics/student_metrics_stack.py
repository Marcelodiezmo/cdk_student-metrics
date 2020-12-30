from aws_cdk import core
from os import path
from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as _agw
)


class StudentMetricsStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        this_dir = path.dirname(__file__)

        # Lambda for mostPopular path
        lambda_mostpopular = _lambda.Function(
            self,
            'lambda_metrics',
            code=_lambda.Code.from_asset(path.join(this_dir,'lambdas')),
            handler='student_metrics_mostpopular.handler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            description='Lambda to get information about user metrics'
        )

        api = _agw.RestApi(
            self,
            'StudentMetrics',
            description='API for users metrics'
        )

        # Integrate API and lambda function
        events_integration = _agw.LambdaIntegration(lambda_mostpopular)

        # Main Resources
        user_resource = api.root.add_resource("Users")
        metrics_resource = user_resource.add_resource("Metrics")

        # Paths resources
        most_popular_resource = metrics_resource.add_resource("mostPopular")
        course_month_resource = metrics_resource.add_resource("courseMonth")
        ranking_company_resource = metrics_resource.add_resource("rankingCompany")

        # Paths Methods
        most_popular_method = most_popular_resource.add_method(
            "GET",
            events_integration
            # auth
        )
