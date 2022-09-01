from os import path
from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as _iam,
    aws_ec2 as _ec2)

import aws_cdk as core
from constructs import Construct


class lambdaStack(Construct):
    student_lambda: _lambda.Function

    def __init__(self, scope: Construct, construct_id: str,
                 lambda_name: str, shared_values: [], has_security: bool, has_mongo: bool,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        this_dir = path.dirname(__file__)
        code_route = _lambda.Code.from_asset(path.join(this_dir, '../lambdas/' + lambda_name))

        #print(shared_values['value'])
        rds_host = shared_values['rds_host']
        db_user = shared_values['db_user']
        db_pass = shared_values['db_pass']
        db_name = shared_values['db_name']
        db_port = shared_values['db_port']
        secret_name = shared_values['secret_name']
        layer_arn = shared_values['layer_arn']
        role_arn = shared_values['rol_arn']
        security_group_id = shared_values["security_group_id"]
        subnets = shared_values["subnets"]
        vpc_id = shared_values["vcp_id"]
        bucket_name = shared_values["bucket_name"]
        vpc_id = shared_values["vcp_id"]
        mongodb_db = shared_values["mongodb_db"]
        mongodb_ip = shared_values["mongodb_ip"]
        mongodb_password = shared_values["mongodb_password"]
        mongodb_user = shared_values["mongodb_user"]
        ElasticMapReduceSlave = shared_values["ElasticMapReduce-slave"]
        ElasticMapReduceDefault = shared_values["ElasticMapReduce-default"]
        ElasticMapReduceMaster = shared_values["ElasticMapReduce-master"]
       # secret_name = shared_values["secret_name"]

        security_group = [_ec2.SecurityGroup.from_security_group_id(self, "student_suc_group",
                                                                   security_group_id=security_group_id)]

        if has_mongo:
            has_security = True    
            subnets = shared_values["subnets_mongo"]
            role_arn = shared_values['role_arn_mongo']
            layer_arn = shared_values['layer_arn_mongo']

            # Security Groups
            ElasticMapReduce_slave = _ec2.SecurityGroup.from_security_group_id(
                    self, "ElasticMapReduce-slave", ElasticMapReduceSlave, mutable=False)
            ElasticMapReduce_default = _ec2.SecurityGroup.from_security_group_id(
                    self, "ElasticMapReduce-default", ElasticMapReduceDefault, mutable=False)
            ElasticMapReduce_master = _ec2.SecurityGroup.from_security_group_id(
                    self, "ElasticMapReduce-master", ElasticMapReduceMaster, mutable=False)
                                                                    
            security_group = [
                ElasticMapReduce_slave, ElasticMapReduce_default, ElasticMapReduce_master]

        if "lambda_name" in shared_values:
            lambda_name = lambda_name + shared_values["lambda_name"]

        lambda_role = _iam.Role.from_role_arn(self, 'student_role', role_arn=role_arn)
        lambda_layer = _lambda.LayerVersion.from_layer_version_attributes(self, 'student_layer',
                                                                          layer_version_arn=layer_arn)
        # security_group = _ec2.SecurityGroup.from_security_group_id(self, "student_suc_group",
        #                                                            security_group_id=security_group_id)

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
            vpc=dev_vpc if has_security else None,
            role=lambda_role,
            security_groups=security_group if has_security else None,
            layers=[lambda_layer],
            environment={
                "rds_host": rds_host,
                "db_user": db_user,
                "db_pass": db_pass,
                "db_name": db_name,
                "db_port": db_port,
                "bucket_name": bucket_name,
                "secret_name": secret_name,
                "mongodb_db": mongodb_db,
                "mongodb_ip": mongodb_ip,
                "mongodb_password": mongodb_password,
                "mongodb_user": mongodb_user
            },
            timeout=core.Duration.seconds(30)
        )

        student_lambda.grant_invoke(_iam.ServicePrincipal('apigateway.amazonaws.com'))

        self.student_lambda = student_lambda

class lambdaStackTEST(Construct):
    student_lambda: _lambda.Function

    def __init__(self, scope: Construct, construct_id: str,
                 lambda_name: str, shared_values: [], has_security: bool, has_mongo: bool,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        this_dir = path.dirname(__file__)
        code_route = _lambda.Code.from_asset(path.join(this_dir, '../lambdas/' + lambda_name))

        #print(shared_values['value'])
        rds_host = shared_values['rds_host']
        db_user = shared_values['db_user']
        db_pass = shared_values['db_pass']
        db_name = shared_values['db_name']
        db_port = shared_values['db_port']
        secret_name = shared_values['secret_name']
        layer_arn = shared_values['layer_arn']
        role_arn = shared_values['rol_arn']
        security_group_id = shared_values["security_group_id"]
        subnets = shared_values["subnets"]
        vpc_id = shared_values["vcp_id"]
        bucket_name = shared_values["bucket_name"]
        vpc_id = shared_values["vcp_id"]
        mongodb_db = shared_values["mongodb_db"]
        mongodb_ip = shared_values["mongodb_ip"]
        mongodb_password = shared_values["mongodb_password"]
        mongodb_user = shared_values["mongodb_user"]
        ElasticMapReduceSlave = shared_values["ElasticMapReduce-slave"]
        ElasticMapReduceDefault = shared_values["ElasticMapReduce-default"]
        ElasticMapReduceMaster = shared_values["ElasticMapReduce-master"]
       # secret_name = shared_values["secret_name"]

        security_group = [_ec2.SecurityGroup.from_security_group_id(self, "student_suc_group",
                                                                   security_group_id=security_group_id)]

        if has_mongo:
            has_security = True    
            subnets = shared_values["subnets_mongo"]
            role_arn = shared_values['role_arn_mongo']
            layer_arn = shared_values['layer_arn_mongo']

            # Security Groups
            ElasticMapReduce_slave = _ec2.SecurityGroup.from_security_group_id(
                    self, "ElasticMapReduce-slave", ElasticMapReduceSlave, mutable=False)
            ElasticMapReduce_default = _ec2.SecurityGroup.from_security_group_id(
                    self, "ElasticMapReduce-default", ElasticMapReduceDefault, mutable=False)
            ElasticMapReduce_master = _ec2.SecurityGroup.from_security_group_id(
                    self, "ElasticMapReduce-master", ElasticMapReduceMaster, mutable=False)
                                                                    
            security_group = [
                ElasticMapReduce_slave, ElasticMapReduce_default, ElasticMapReduce_master]

        if "lambda_name" in shared_values:
            lambda_name = lambda_name + shared_values["lambda_name"]

        lambda_role = _iam.Role.from_role_arn(self, 'student_role', role_arn=role_arn)
        lambda_layer = _lambda.LayerVersion.from_layer_version_attributes(self, 'student_layer',
                                                                          layer_version_arn=layer_arn)
        # security_group = _ec2.SecurityGroup.from_security_group_id(self, "student_suc_group",
        #                                                            security_group_id=security_group_id)

        dev_vpc = _ec2.Vpc.from_vpc_attributes(self, 'dev_vpc',
                                               vpc_id=vpc_id,
                                               availability_zones=core.Fn.get_azs(),
                                               private_subnet_ids=subnets
                                               )

        student_lambda = _lambda.Function(
            self,
            'student_metrics_GOTOPROD' + lambda_name,
            function_name='student_metrics_GOTOPROD' + lambda_name,
            code=code_route,
            # code=_lambda.Code.from_asset(path.join(this_dir,'lambdas/mostpopular.zip')),
            handler='app.handler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            description='Lambda for student metrics project',
            vpc=dev_vpc if has_security else None,
            role=lambda_role,
            security_groups=security_group if has_security else None,
            layers=[lambda_layer],
            environment={
                "rds_host": rds_host,
                "db_user": db_user,
                "db_pass": db_pass,
                "db_name": db_name,
                "db_port": db_port,
                "bucket_name": bucket_name,
                "secret_name": secret_name,
                "mongodb_db": mongodb_db,
                "mongodb_ip": mongodb_ip,
                "mongodb_password": mongodb_password,
                "mongodb_user": mongodb_user
            },
            timeout=core.Duration.seconds(30)
        )

        student_lambda.grant_invoke(_iam.ServicePrincipal('apigateway.amazonaws.com'))

        self.student_lambda = student_lambda