from cloudshell.workflow.orchestration.sandbox import Sandbox
from cloudshell.helpers.sandbox_reporter.reporter import SandboxReporter

REPORTING_SERVICE_MODEL = "Reporting Service"


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

    res_details = api.GetReservationDetails(res_id, True).ReservationDescription
    services = res_details.Services
    reporting_service_search = [x for x in services if x.ServiceName == REPORTING_SERVICE_MODEL]
    if not reporting_service_search:
        raise ValueError("No reporting service found on canvas")

    reporting_service = reporting_service_search[0]
    reporter.warning("starting teardown, sending job report...")

    try:
        api.ExecuteCommand(reservationId=res_id,
                           targetName=reporting_service.Alias,
                           targetType="Service",
                           commandName="send_report_mail")
    except Exception as e:
        msg = "Issue with reporting service: {}".format(str(e))
        reporter.error(msg)
        api.SetReservationLiveStatus(reservationId=res_id,
                                     liveStatusName="Error",
                                     additionalInfo=msg)
        raise Exception(msg)
    reporter.success("Email Job Report Sent")
