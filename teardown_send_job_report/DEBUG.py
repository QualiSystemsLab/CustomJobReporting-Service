from cloudshell.workflow.orchestration.sandbox import Sandbox
from cloudshell.helpers.scripts.cloudshell_dev_helpers import attach_to_cloudshell_as
from credentials import credentials
from send_job_report import send_job_report

LIVE_SANDBOX_ID = "3cc3ad73-5147-4057-9edf-5875747bf786"

attach_to_cloudshell_as(user=credentials["user"],
                        password=credentials["password"],
                        domain=credentials["domain"],
                        reservation_id=LIVE_SANDBOX_ID,
                        server_address=credentials['server'])

sandbox = Sandbox()
send_job_report(sandbox=sandbox, components=None)
