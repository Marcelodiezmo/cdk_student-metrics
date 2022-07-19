#!/usr/bin/env python3

from os import device_encoding
from aws_cdk import core

from student_metrics.student_metrics_stack import StudentMetricsStack
from student_metrics.student_metrics_stack import StudentMetricsStackTEST

prod = core.Environment(account='986361039434', region='us-east-1')
dev = core.Environment(account='824404647578', region='us-east-1')

app = core.App()
StudentMetricsStack(app, "student-metrics-test", env=core.Environment(
    account='986361039434',
    region='us-east-1'), stage='test')

StudentMetricsStack(app, "student-metrics", env=core.Environment(
    account='986361039434',
    region='us-east-1'), stage='prod')

StudentMetricsStack(app, "student-metrics-dev", env=core.Environment(
    account='824404647578',
    region='us-east-1'), stage='dev')

# StudentMetricsStack(app, "student-metrics-main", stage='main')

StudentMetricsStackTEST(app, "student-metrics-test-GOTOPROD", env=core.Environment(
    account='986361039434',
    region='us-east-1'), stage='test')

StudentMetricsStackTEST(app, "student-metrics-GOTOPROD", env=core.Environment(
    account='986361039434',
    region='us-east-1'), stage='prod')

StudentMetricsStackTEST(app, "student-metrics-dev-GOTOPROD", env=core.Environment(
    account='824404647578',
    region='us-east-1'), stage='dev')

app.synth()
