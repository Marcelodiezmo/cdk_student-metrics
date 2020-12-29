#!/usr/bin/env python3

from aws_cdk import core

from student_metrics.student_metrics_stack import StudentMetricsStack


app = core.App()
StudentMetricsStack(app, "student-metrics")

app.synth()
