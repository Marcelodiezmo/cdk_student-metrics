from aws_cdk import core
from os import path
from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as _agw,
    aws_s3 as _s3,
    aws_ec2 as _ec2,
    aws_rds as _rds
)


class StudentMetricsStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        this_dir = path.dirname(__file__)

        # Create the S3 bucket for JSON metrics files
        student_bucket = _s3.Bucket(self, "student-metrics", bucket_name="student-metrics")

        # Lambda for mostPopular path
        lambda_mostpopular = _lambda.Function(
            self,
            'student_metrics_mostpopular',
            function_name='student_metrics_mostpopular',
            # code=_lambda.Code.from_asset(path.join(this_dir,'lambdas')),
            code=_lambda.Code.from_asset(path.join(this_dir,'lambdas/mostpopular.zip')),
            handler='student_metrics_mostpopular.handler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            description='Lambda to get information about the most popular course'
        )

        # Lambda for courseMonth path
        lambda_coursemonth = _lambda.Function(
            self,
            'student_metrics_coursemonth',
            function_name='student_metrics_coursemonth',
            code=_lambda.Code.from_asset(path.join(this_dir,'lambdas')),
            handler='student_metrics_coursemonth.handler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            description='Lambda to get information about the Course of the Month'
        )

        # Lambda for Ranking Company
        lambda_rankingcompany = _lambda.Function(
            self,
            'student_metrics_rankingcompany',
            function_name='student_metrics_rankingcompany',
            code=_lambda.Code.from_asset(path.join(this_dir,'lambdas')),
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

        # RDS configuration

        # RDS needs to be setup in a VPC
        # vpc = _ec2.Vpc(self, 'vpc-students', max_azs=2)

        # vpc_id = "vpc-4f3dd135"
        # vpc = _ec2.Vpc.from_lookup(self, "VPC", vpc_id=vpc_id)

        # security group
        # sg = _ec2.SecurityGroup(self,'scg',vpc = vpc)

        rds = _rds.DatabaseInstance.from_database_instance_attributes(
            self,
            id = 'db_instance',
            instance_identifier = 'moodle-dev-rds-aurora',
            instance_endpoint_address = 'moodle-dev-rds-aurora-instance-1.c9maghmfm0zw.us-east-1.rds.amazonaws.com',
            port = 3036,
            security_groups = [],
            # .DatabaseInstanceEngine..mysql(version = _rds.AuroraMysqlEngineVersion.VER_5_7_12)
            engine = _rds.AuroraMysqlEngineVersion.VER_5_7_12
        )

        rds.grant_connect(lambda_mostpopular)