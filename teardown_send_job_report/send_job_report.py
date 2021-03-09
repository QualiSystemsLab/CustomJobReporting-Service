from cloudshell.workflow.orchestration.sandbox import Sandbox
from helper_code.sandbox_print_helpers import *
from helper_code.sandbox_reporter import SandboxReporter

REPORTING_SERVICE = "Reporting Service"


# ========== Primary Function ==========
def send_job_report(sandbox, components=None):
    """
    Functions passed into orchestration flow MUST have (sandbox, components) signature
    :param Sandbox sandbox:
    :param components
    :return:
    """
    api = sandbox.automation_api
    res_id = sandbox.id
    logger = sandbox.logger
    reporter = SandboxReporter(api, res_id, logger)
    reporter.warn_out("starting teardown, sending job report...")


    # send mail report
    try:
        api.ExecuteCommand(reservationId=res_id,
                           targetName=REPORTING_SERVICE,
                           targetType="Service",
                           commandName="send_report_mail")
    except Exception as e:
        msg = "Issue with reporting service: {}".format(str(e))
        err_print(api, res_id, msg)
        reporter.err_out(msg)
        api.SetReservationLiveStatus(reservationId=res_id,
                                     liveStatusName="Error",
                                     additionalInfo=msg)
        raise Exception(msg)

    reporter.warn_out("Email Job Report Sent")


