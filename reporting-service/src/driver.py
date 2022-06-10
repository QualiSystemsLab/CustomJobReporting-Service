import os

from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.api.cloudshell_api import InputNameValue, SandboxDataKeyValue
from cloudshell.logging.qs_logger import get_qs_logger
from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.helpers.sandbox_reporter.reporter import SandboxReporter

from data_model import *  # run 'shellfoundry generate' to generate data model classes
from quali_api_wrapper import QualiAPISession
import time_helpers as time_help
from format_html import format_html_template

EMAIL_TEMPLATE = "JobExecutionEnded.htm"


class ReportingServiceException(Exception):
    pass


class ReportingServiceDriver(ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        pass

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        pass

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass

    @staticmethod
    def _get_reporter(context, api):
        """
        :param ResourceCommandContext context:
        :param CloudShellAPISession api:
        :return:
        """
        res_id = context.reservation.reservation_id
        service_name = context.resource.fullname
        service_model = context.resource.model
        logger = get_qs_logger(log_group=res_id, log_category=service_model, log_file_prefix=service_name)
        reporter = SandboxReporter(api, res_id, logger)
        return reporter

    def send_report_mail(self, context):
        """
        get current job id and save as attribute on shell
        :param ResourceCommandContext context:
        :return:
        """
        api = CloudShellSessionContext(context).get_api()
        res_id = context.reservation.reservation_id
        reporter = self._get_reporter(context, api)

        resource = ReportingService.create_from_context(context)
        service_name = resource.name
        additional_recipients = resource.additional_recipients
        cc_recipients = resource.cc_recipients

        quali_server = context.connectivity.server_address
        admin_token = context.connectivity.admin_auth_token
        sb_owner_mail = context.reservation.owner_email

        if not sb_owner_mail and not additional_recipients:
            raise ValueError("No sandbox owner mail or additional recipients configured")

        recipients = ""
        if sb_owner_mail:
            recipients += sb_owner_mail

        if additional_recipients:
            if recipients:
                recipients += f", {additional_recipients}"
            else:
                recipients = additional_recipients

        current_job_id = resource.current_job_id
        cs_https = resource.cs_https
        smtp_resource = resource.smtp_resource
        self._validate_smtp_resource(api, reporter, smtp_resource)

        server_protocol = "https" if cs_https == "True" else "http"

        server_date_string = time_help.get_server_formatted_date(api)
        server_date_string += " (UTC)"

        # validate that job id was added
        if not current_job_id:
            msg = "No Job Id Set On Reporting Service. Can't pull report data from Quali API"
            reporter.error(msg)
            self._send_error_report(context, custom_message=msg)
            raise ReportingServiceException(msg)

        try:
            quali_api = QualiAPISession(host=quali_server, token_id=admin_token)
        except Exception as e:
            err_msg = "Issue establishing Quali API Session: {}".format(str(e))
            reporter.error(err_msg)
            self._send_error_report(context, err_msg)
            raise ReportingServiceException(err_msg)

        try:
            job_details = quali_api.get_job_details(current_job_id)
        except Exception as e:
            err_msg = "Could not get job details: {}".format(str(e))
            reporter.error(err_msg)
            self._send_error_report(context, err_msg)
            raise ReportingServiceException(err_msg)

        current_dir = os.path.abspath(os.path.dirname(__file__))
        template_path = os.path.join(current_dir, EMAIL_TEMPLATE)

        sb_data = api.GetSandboxData(res_id).SandboxDataKeyValues

        email_body = format_html_template(html_path=template_path,
                                          job_details=job_details,
                                          server_address=quali_server,
                                          server_date_time=server_date_string,
                                          protocol=server_protocol,
                                          sb_data=sb_data)
        # sending mail
        test_result = job_details["JobResult"]
        job_name = job_details["Name"]
        mail_inputs = [
            InputNameValue("message_title", "Job Report: '{}', Ended: {} Result: '{}'".format(job_name,
                                                                                              server_date_string,
                                                                                              test_result)),
            InputNameValue("message_body", email_body),
            InputNameValue("recipients", recipients),
            InputNameValue("cc_recipients", cc_recipients)
        ]
        try:
            api.ExecuteCommand(reservationId=res_id,
                               targetName=smtp_resource,
                               targetType="Resource",
                               commandName="send_mail",
                               commandInputs=mail_inputs,
                               printOutput=True)
        except Exception as e:
            err_msg = "Issue sending mail. Check '{}' SMTP Resource. Error: {}".format(smtp_resource, str(e))
            api.SetResourceLiveStatus(resourceFullName=service_name,
                                      liveStatusName="Error",
                                      additionalInfo=err_msg)
            raise ReportingServiceException(err_msg)

        return "Custom Mail Report sent successfully"

    @staticmethod
    def _validate_smtp_resource(api, reporter, smtp_resource):
        try:
            api.GetResourceDetails(resourceFullPath=smtp_resource)
        except Exception as e:
            err_msg = f"Failed to find SMTP Server Resource to send mail: {str(e)}"
            reporter.error(err_msg)
            raise ReportingServiceException(err_msg)

    def _send_error_report(self, context, custom_message=""):
        """
        get current job id and save as attribute on shell
        :param ResourceCommandContext context:
        :return:
        """
        api = CloudShellSessionContext(context).get_api()
        res_id = context.reservation.reservation_id
        reporter = self._get_reporter(context, api)

        environment_name = context.reservation.environment_name

        resource = ReportingService.create_from_context(context)
        additional_recipients = resource.additional_recipients
        cc_recipients = resource.cc_recipients
        error_report_all = True if resource.error_report_all == "True" else False
        sb_owner_mail = context.reservation.owner_email

        if additional_recipients and error_report_all:
            recipients = sb_owner_mail + "," + additional_recipients
        else:
            recipients = sb_owner_mail

        if not error_report_all:
            cc_recipients = ""

        smtp_resource = resource.smtp_resource
        self._validate_smtp_resource(api, reporter, smtp_resource)

        email_body = """
        <h2>Job Reporting Issue</h2>
        <p>Reservation Id used in job: {res_id}</p>
        <p>Environment Name: {env_name}</p>
        <p>{custom_message}</p>
        """.format(res_id=res_id, env_name=environment_name, custom_message=custom_message)
        mail_inputs = [
            InputNameValue("message_title", "Job Report Issue - Environment '{}'".format(environment_name)),
            InputNameValue("message_body", email_body),
            InputNameValue("recipients", recipients),
            InputNameValue("cc_recipients", cc_recipients)
        ]
        try:
            api.ExecuteCommand(reservationId=res_id,
                               targetName=smtp_resource,
                               targetType="Resource",
                               commandName="send_mail",
                               commandInputs=mail_inputs)
        except Exception as e:
            err_msg = "Issue sending error report mail: {}".format(str(e))
            reporter.error(err_msg)
            raise ReportingServiceException(err_msg)
        msg = f"Error Report Mail sent to {recipients}"
        reporter.logger.info(msg)
        return msg

    def set_test_data(self, context, test_id, test_data):
        """
        set custom
        :param ResourceCommandContext context:
        :param str test_id:
        :param str test_data:
        :return:
        """
        api = CloudShellSessionContext(context).get_api()
        res_id = context.reservation.reservation_id
        reporter = self._get_reporter(context, api)

        ms_timestamp = time_help.get_current_millisecond_timestamp()

        # save sandbox data
        sb_data = []
        data_key = "{}_{}".format(test_id, ms_timestamp)
        sb_timestamp_data = SandboxDataKeyValue(data_key, test_data)
        sb_data.append(sb_timestamp_data)
        api.SetSandboxData(res_id, sb_data)

        reporter.info(f"=== Set sandbox data ==="
                      f"\nkey: {data_key}"
                      f"\ndata: {test_data}")
