from cloudshell.workflow.orchestration.sandbox import Sandbox
from helper_code.sandbox_print_helpers import *
import helper_code.automation_api_helpers as api_help
import cloudshell.helpers.scripts.cloudshell_scripts_helpers as script_help
from helper_code.quali_api_wrapper import QualiAPISession
import json


# ========== Primary Function ==========
def first_module_flow(sandbox, components=None):
    """
    Functions passed into orchestration flow MUST have (sandbox, components) signature
    :param Sandbox sandbox:
    :param components
    :return:
    """
    api = sandbox.automation_api

    res_id = sandbox.id
    warn_print(api, sandbox.id, "=== Hello from sandbox setup! ===")

    try:
        quali_api = QualiAPISession(host="localhost", username="admin", password="admin", domain="Global")
    except Exception as e:
        sb_print(api, res_id, "issue with quali api session")
    else:
        running_jobs = quali_api.get_running_jobs()
        if running_jobs:
            jobs_json = json.dumps(running_jobs)
            sb_print(api, res_id, jobs_json)
        else:
            sb_print(api, res_id, "running jobs is empty")

    api.EnqueueCommand(reservationId=res_id,
                       targetName="Reporting Service",
                       targetType="Service",
                       commandName="get_current_job_id")

