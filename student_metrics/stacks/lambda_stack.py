from os import path
from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as _iam,
    aws_ec2 as _ec2,
    core
)

class lambdaStack(core.Construct):
    student_lambda: _lambda.Function
    def __init__(self, scope: core.Construct, construct_id: str,
        lambda_name: str,
        stage: str,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        this_dir = path.dirname(__file__)
        code_route = _lambda.Code.from_asset(path.join(this_dir, '../lambdas/' + lambda_name))

        shared_values = self.node.try_get_context('shared_values')
        dev_values = shared_values['dev_values']
        test_values = shared_values['test_values']
        prod_values = shared_values['prod_values']

        if stage == 'prod':
            rds_host = prod_values['rds_host']
            db_user = prod_values['db_user']
            db_pass = prod_values['db_pass']
            db_name = prod_values['db_name']
            db_port = prod_values['db_port']
            secret_name = prod_values['secret_name']
            layer_arn = prod_values['layer_arn']
            role_arn = prod_values['rol_arn']
            security_group_id = prod_values["security_group_id"]
            subnets = prod_values["subnets"]
            vpc_id = prod_values["vcp_id"]
            bucket_name = prod_values["bucket_name"]
        elif stage == 'test':
            lambda_name = lambda_name + '_test'
            rds_host = test_values['rds_host']
            db_user = test_values['db_user']
            db_pass = test_values['db_pass']
            db_name = test_values['db_name']
            db_port = test_values['db_port']
            secret_name = test_values['secret_name']
            layer_arn = test_values['layer_arn']
            role_arn = test_values['rol_arn']
            security_group_id = test_values["security_group_id"]
            subnets = test_values["subnets"]
            vpc_id = test_values["vcp_id"]
            bucket_name = test_values["bucket_name"]
        elif stage == 'dev':
            rds_host = dev_values['rds_host']
            db_user = dev_values['db_user']
            db_pass = dev_values['db_pass']
            db_name = dev_values['db_name']
            db_port = dev_values['db_port']
            secret_name = dev_values['secret_name']
            layer_arn = dev_values['layer_arn']
            role_arn = dev_values['rol_arn']
            security_group_id = dev_values["security_group_id"]
            subnets = dev_values["subnets"]
            vpc_id = dev_values["vcp_id"]
            bucket_name = dev_values["bucket_name"]

        lambda_role = _iam.Role.from_role_arn(self, 'student_role', role_arn=role_arn)
        lambda_layer = _lambda.LayerVersion.from_layer_version_attributes(self, 'student_layer', layer_version_arn=layer_arn)
        security_group = _ec2.SecurityGroup.from_security_group_id(self, "student_suc_group", security_group_id=security_group_id)

        dev_vpc = _ec2.Vpc.from_vpc_attributes(self, 'dev_vpc',
                                               vpc_id=vpc_id,
                                               availability_zones=core.Fn.get_azs(),
                                               private_subnet_ids=subnets
                                               )

        student_lambda = _lambda.Function(
            self,
            'student_metrics_' + lambda_name,
            function_name='student_metrics_' + lambda_name,
            code=code_route,
            # code=_lambda.Code.from_asset(path.join(this_dir,'lambdas/mostpopular.zip')),
            handler='app.handler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            description='Lambda for student metrics project',
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

        student_lambda.grant_invoke(_iam.ServicePrincipal('apigateway.amazonaws.com'))

        self.student_lambda = student_lambda