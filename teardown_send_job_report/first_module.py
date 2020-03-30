from cloudshell.workflow.orchestration.sandbox import Sandbox
from helper_code.sandbox_print_helpers import *
import helper_code.automation_api_helpers as api_help
from helper_code.quali_api_wrapper import QualiAPISession
import cloudshell.helpers.scripts.cloudshell_scripts_helpers as script_help
import json
import time


REPORTING_SERVICE = "Reporting Service"


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
    warn_print(api, res_id, "starting teardown, sending job report...")

    # send mail report
    try:
        api.ExecuteCommand(reservationId=res_id,
                           targetName=REPORTING_SERVICE,
                           targetType="Service",
                           commandName="send_report_mail")
    except Exception as e:
        msg = "Issue with reporting service: {}".format(str(e))
        err_print(api, res_id, msg)
        raise
    else:
        warn_print(api, res_id, "Email Job Report Sent")


