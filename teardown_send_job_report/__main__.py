from cloudshell.workflow.orchestration.teardown.default_teardown_orchestrator import DefaultTeardownWorkflow
from cloudshell.workflow.orchestration.sandbox import Sandbox
from send_job_report import send_job_report

sandbox = Sandbox()
DefaultTeardownWorkflow().register(sandbox)
sandbox.workflow.add_to_teardown(send_job_report, None)
sandbox.execute_teardown()

