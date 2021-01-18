from aws_cdk import core
from os import path
from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as _agw,
    aws_s3 as _s3,
    aws_ec2 as _ec2,
    aws_rds as _rds,
    aws_iam as _iam,
    core
)


class StudentMetricsStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        this_dir = path.dirname(__file__)

        # Create the S3 bucket for JSON metrics files
        student_bucket = _s3.Bucket(self, "student-metrics", bucket_name="student-metrics")

        dev_vpc = _ec2.Vpc.from_vpc_attributes(self, 'dev_vpc',
            vpc_id = "vpc-4f3dd135",
            availability_zones = core.Fn.get_azs(),
            private_subnet_ids = ["subnet-0aea8240", "subnet-430ca91f"]
        )

        lambda_role = _iam.Role.from_role_arn(self, 'student_role', 'arn:aws:iam::986361039434:role/customerSuccessBoxv1-LambdaExecutionRole-OBI9J5F7YON')

        lambda_layer = _lambda.LayerVersion.from_layer_version_attributes(self,'student_layer',layer_version_arn='arn:aws:lambda:us-east-1:986361039434:layer:csb-sam-app-dependencies:13')

        security_group = _ec2.SecurityGroup.from_security_group_id(self, "student_suc_group", "sg-f9a5c9b2")

        # Lambda for mostPopular path
        lambda_mostpopular = _lambda.Function(
            self,
            'student_metrics_mostpopular',
            function_name='student_metrics_mostpopular',
            code=_lambda.Code.from_asset(path.join(this_dir,'lambdas/most_popular')),
            # code=_lambda.Code.from_asset(path.join(this_dir,'lambdas/mostpopular.zip')),
            handler='student_metrics_mostpopular.handler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            description='Lambda to get information about the most popular course',
            vpc = dev_vpc,
            role = lambda_role,
            security_groups=[security_group],
            layers=[lambda_layer]
            # environment={
            #     "ASTEROIDS_TABLE": ddb_asteroids_table.table_name,
            #     "S3_BUCKET": s3_bucket.bucket_name,
            #     "SCHEMA": self.node.try_get_context("SCHEMA"),
            #     "REGION": self.node.try_get_context("REGION"),
            #     "DB_SECRETS": self.node.try_get_context("DB_SECRETS_REF"),
            #     "TOPIC_ARN": self.node.try_get_context("TOPIC_ARN")
            # }
        )

        # Lambda for courseMonth path
        lambda_coursemonth = _lambda.Function(
            self,
            'student_metrics_coursemonth',
            function_name='student_metrics_coursemonth',
            code=_lambda.Code.from_asset(path.join(this_dir,'lambdas/course_month')),
            handler='student_metrics_coursemonth.handler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            description='Lambda to get information about the Course of the Month'
        )

        # Lambda for Ranking Company
        lambda_rankingcompany = _lambda.Function(
            self,
            'student_metrics_rankingcompany',
            function_name='student_metrics_rankingcompany',
            code=_lambda.Code.from_asset(path.join(this_dir,'lambdas/ranking_company')),
            handler='student_metrics_rankingcompany.handler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            description='Lambda to get information about the students ranking into the company'
        )

        # Grant the bucket to read access from lambdas
        student_bucket.grant_read(lambda_mostpopular)
        student_bucket.grant_read(lambda_coursemonth)
        student_bucket.grant_read(lambda_rankingcompany)

        api = _agw.RestApi(
            self,
            'StudentMetrics',
            description='API for users metrics'
        )

        # Integrate API and mostpopular lambda
        most_popular_integration = _agw.LambdaIntegration(lambda_mostpopular)

        # Integrate API and courseMonth lambda
        course_month_integration = _agw.LambdaIntegration(lambda_coursemonth)

        # Integrate API and rankingcompany lambda
        ranking_company_integration = _agw.LambdaIntegration(lambda_rankingcompany)

        # Main Resources
        user_resource = api.root.add_resource("Users")
        metrics_resource = user_resource.add_resource("Metrics")

        # Paths resources
        # book = books.add_resource("{book_id}") ---- event["queryStringParameters"]['queryparam1']
        most_popular_resource = metrics_resource.add_resource("mostPopular")
        course_month_resource = metrics_resource.add_resource("courseMonth")
        ranking_company_resource = metrics_resource.add_resource("rankingCompany")

        # Paths Methods
        most_popular_resource.add_method(
            "GET",
            most_popular_integration
            # auth
        )

        course_month_resource.add_method(
            "GET",
            course_month_integration
        )

        ranking_company_resource.add_method(
            "GET",
            ranking_company_integration
        )