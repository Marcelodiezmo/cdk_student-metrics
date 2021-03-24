from os import path
from aws_cdk import (
    aws_s3 as _s3,
    aws_s3_deployment as _deploy,
    core
)

class bucketStack(core.Construct):
    student_bucket: _s3.Bucket
    def __init__(self, scope: core.Construct, construct_id: str,
        bucket_name:str,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        this_dir = path.dirname(__file__)
        student_bucket = _s3.Bucket(self, bucket_name, bucket_name=bucket_name)

        _deploy.BucketDeployment(
            self, "DeployFolderLastLogin", 
            sources=[_deploy.Source.asset(path.join(this_dir,"../files"))],
            destination_bucket=student_bucket,
            destination_key_prefix="students/last_login"
        )

        _deploy.BucketDeployment(
            self, "DeployFolderProgressTrainingPlan", 
            sources=[_deploy.Source.asset(path.join(this_dir,"../files"))],
            destination_bucket=student_bucket,
            destination_key_prefix="students/progress_training_plan"
        )

        _deploy.BucketDeployment(
            self, "DeployFolderFinishedCourses", 
            sources=[_deploy.Source.asset(path.join(this_dir,"../files"))],
            destination_bucket=student_bucket,
            destination_key_prefix="students/finished_courses"
        )

        self.student_bucket = student_bucket