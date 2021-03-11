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

    def __init__(self, scope: core.Construct, construct_id: str, prod_stage=False, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        this_dir = path.dirname(__file__)

        lambda_role = _iam.Role.from_role_arn(self, 'student_role',
                                              'arn:aws:iam::986361039434:role/customerSuccessBoxv1-LambdaExecutionRole-OBI9J5F7YON')
        lambda_layer = _lambda.LayerVersion.from_layer_version_attributes(self, 'student_layer',
                                                                          layer_version_arn='arn:aws:lambda:us-east-1:986361039434:layer:csb-sam-app-dependencies:13')
        security_group = _ec2.SecurityGroup.from_security_group_id(self, "student_suc_group", "sg-f9a5c9b2")

        rds_host = ''
        db_user = ''
        db_pass = ''
        db_name = ''
        db_port = ''
        lambda_mostpopular_name = ''
        lambda_coursemonth_name = ''
        lambda_rankingcompany_name = ''
        lambda_powerbi_dashboard_name = ''
        bucket_name = ''
        api_name = ''

        if prod_stage:
            rds_host = self.node.try_get_context("rds_host_prod")
            db_user = self.node.try_get_context("db_user_prod")
            db_pass = self.node.try_get_context("db_pass_prod")
            db_name = self.node.try_get_context("db_name_prod")
            db_port = self.node.try_get_context("db_port_prod")
            lambda_mostpopular_name = 'student_metrics_mostpopular'
            lambda_coursemonth_name = 'student_metrics_coursemonth'
            lambda_rankingcompany_name = 'student_metrics_rankingcompany'
            lambda_powerbi_dashboard_name = "powerbi_dashboard_client"
            bucket_name = 'student-metrics'
            api_name = 'StudentMetrics'
        else:
            rds_host = self.node.try_get_context("rds_host_test")
            db_user = self.node.try_get_context("db_user_test")
            db_pass = self.node.try_get_context("db_pass_test")
            db_name = self.node.try_get_context("db_name_test")
            db_port = self.node.try_get_context("db_port_test")
            lambda_mostpopular_name = 'student_metrics_mostpopular_test'
            lambda_coursemonth_name = 'student_metrics_coursemonth_test'
            lambda_rankingcompany_name = 'student_metrics_rankingcompany_test'
            lambda_powerbi_dashboard_name = "powerbi_dashboard_client_test"
            bucket_name = 'student-metrics-test'
            api_name = 'StudentMetrics_test'

        # Create the S3 bucket for JSON metrics files
        student_bucket = _s3.Bucket(self, bucket_name, bucket_name=bucket_name)

        dev_vpc = _ec2.Vpc.from_vpc_attributes(self, 'dev_vpc',
                                               vpc_id="vpc-4f3dd135",
                                               availability_zones=core.Fn.get_azs(),
                                               private_subnet_ids=["subnet-0aea8240", "subnet-430ca91f"]
                                               )

        # Lambda for mostPopular path
        lambda_mostpopular = _lambda.Function(
            self,
            lambda_mostpopular_name,
            function_name=lambda_mostpopular_name,
            code=_lambda.Code.from_asset(path.join(this_dir, 'lambdas/most_popular')),
            # code=_lambda.Code.from_asset(path.join(this_dir,'lambdas/mostpopular.zip')),
            handler='student_metrics_mostpopular.handler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            description='Lambda to get information about the most popular course',
            vpc=dev_vpc,
            role=lambda_role,
            security_groups=[security_group],
            layers=[lambda_layer],
            environment={
                "rds_host": rds_host,
                "db_user": db_user,
                "db_pass": db_pass,
                "db_name": db_name,
                "db_port": db_port,
                "bucket_name": bucket_name
            }
        )

        lambda_mostpopular.grant_invoke(_iam.ServicePrincipal('apigateway.amazonaws.com'))

        # Lambda for courseMonth path
        lambda_coursemonth = _lambda.Function(
            self,
            lambda_coursemonth_name,
            function_name=lambda_coursemonth_name,
            code=_lambda.Code.from_asset(path.join(this_dir, 'lambdas/course_month')),
            handler='student_metrics_coursemonth.handler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            description='Lambda to get information about the Course of the Month',
            vpc=dev_vpc,
            role=lambda_role,
            security_groups=[security_group],
            layers=[lambda_layer],
            environment={
                "rds_host": rds_host,
                "db_user": db_user,
                "db_pass": db_pass,
                "db_name": db_name,
                "db_port": db_port,
                "bucket_name": bucket_name
            }
        )

        lambda_coursemonth.grant_invoke(_iam.ServicePrincipal('apigateway.amazonaws.com'))

        # Lambda for Ranking Company

        lambda_rankingcompany = _lambda.Function(
            self,
            lambda_rankingcompany_name,
            function_name=lambda_rankingcompany_name,
            code=_lambda.Code.from_asset(path.join(this_dir, 'lambdas/ranking_company')),
            handler='student_metrics_rankingcompany.handler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            description='Lambda to get information about the students ranking into the company',
            vpc=dev_vpc,
            role=lambda_role,
            security_groups=[security_group],
            layers=[lambda_layer],
            environment={
                "rds_host": rds_host,
                "db_user": db_user,
                "db_pass": db_pass,
                "db_name": db_name,
                "db_port": db_port,
                "bucket_name": bucket_name
            }
        )
        lambda_rankingcompany.grant_invoke(_iam.ServicePrincipal('apigateway.amazonaws.com'))

        lambda_powerbi_dashboard = _lambda.Function(
            self,
            lambda_powerbi_dashboard_name,
            function_name=lambda_powerbi_dashboard_name,
            code=_lambda.Code.from_asset(path.join(this_dir, 'lambdas/dashboard_powerbi')),
            handler='app.handler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            description='Lambda to get URL that contains the analytics dashboard',
            vpc=dev_vpc,
            role=lambda_role,
            security_groups=[security_group]
        )

        lambda_powerbi_dashboard.grant_invoke(_iam.ServicePrincipal('apigateway.amazonaws.com'))

        # Grant the bucket to read access from lambdas
        student_bucket.grant_read(lambda_mostpopular)
        student_bucket.grant_read(lambda_coursemonth)
        student_bucket.grant_read(lambda_rankingcompany)

        api = _agw.RestApi(
            self,
            api_name,
            description='API for users metrics',
            deploy= False
        )

        # Integrate API and mostpopular lambda
        most_popular_integration = _agw.LambdaIntegration(lambda_mostpopular)

        # Integrate API and courseMonth lambda
        course_month_integration = _agw.LambdaIntegration(lambda_coursemonth)

        # Integrate API and rankingcompany lambda
        ranking_company_integration = _agw.LambdaIntegration(lambda_rankingcompany)

        # Integrate API and Power BI Dashboard lambda
        powerbi_dashboard_integration = _agw.LambdaIntegration(lambda_powerbi_dashboard)

        # Main Resources
        user_resource = api.root.add_resource("users")
        metrics_resource = user_resource.add_resource("metrics")
        root_resource = api.root.add_resource("v1")
        students_resource = root_resource.add_resource("students")

        # Paths resources
        most_popular_resource = metrics_resource.add_resource("mostpopular")
        course_month_resource = metrics_resource.add_resource("coursemonth")
        ranking_company_resource = metrics_resource.add_resource("rankingcompany").add_resource("{companyId}")
        powerbi_dashboard_resource = students_resource.add_resource("dashboard").add_resource("{companyId}")

        # Paths Methods
        most_popular_method = most_popular_resource.add_method(
            "GET",
            most_popular_integration
            # api_key_required=True
        )
        # key = api.add_api_key("ApiKey", api_key_name="studentMetricsKey")
        #
        # plan = api.add_usage_plan(
        #     "UsagePlan",
        #     name="Easy",
        #     api_key=key,
        #     throttle={
        #         "rate_limit": 100,
        #         "burst_limit": 50
        #     }
        # )
        #
        # plan.add_api_stage(
        #     stage=api.deployment_stage,
        #     throttle=[{
        #         "method": most_popular_method,
        #         "throttle": {
        #             "rate_limit": 100,
        #             "burst_limit": 50
        #         }
        #     }]
        # )

        course_month_resource.add_method(
            "GET",
            course_month_integration
        )

        ranking_company_resource.add_method(
            "GET",
            ranking_company_integration
        )

        powerbi_dashboard_resource.add_method(
            "GET",
            powerbi_dashboard_integration
        )

        # Deployment
        if prod_stage:
            deployment_prod = _agw.Deployment(self, id='deployment_prod', api=api)
            _agw.Stage(self, id='prod_stage', deployment=deployment_prod, stage_name='services')
        else:
            deployment_test = _agw.Deployment(self, id='deployment_test', api=api)
            _agw.Stage(self, id='test_stage', deployment=deployment_test, stage_name='test')
