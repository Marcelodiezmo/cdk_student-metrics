#!/usr/bin/env python3

from aws_cdk import core

from student_metrics.student_metrics_stack import StudentMetricsStack


app = core.App()
StudentMetricsStack(app, "student-metrics-test", prod_stage=False)
StudentMetricsStack(app, "student-metrics", prod_stage=True)

app.synth()
