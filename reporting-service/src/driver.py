import os

from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext
from data_model import *  # run 'shellfoundry generate' to generate data model classes
from helper_code.quali_api_wrapper import QualiAPISession
import helper_code.shell_api_helpers as shell_api_help
import helper_code.automation_api_helpers as auto_api_help
from helper_code.sandbox_print_helpers import *
from helper_code.sandbox_reporter import SandboxReporter
import helper_code.time_helpers as time_help
import json
import time
from cloudshell.api.cloudshell_api import AttributeNameValue, InputNameValue, SandboxDataKeyValue
from format_html import format_html_template
from cloudshell.logging.qs_logger import get_qs_logger
from cloudshell.api.cloudshell_api import CloudShellAPISession


EMAIL_TEMPLATE = "JobExecutionEnded.htm"


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

    def _get_current_job_id(self, context):
        """
        get current job id and save as attribute on shell
        NOT BEING USED NOW (SETTING JOB ID ON SERVICE FROM TEST)
        :param ResourceCommandContext context:
        :return:
        """
        api = shell_api_help.get_api_from_context(context)
        res_id = context.reservation.reservation_id
        reporter = self._get_reporter(context, api)

        blueprint_name = context.reservation.environment_name
        reporter.info_out("blueprint name test - {}".format(blueprint_name))

        service_name = context.resource.name
        model = context.resource.model
        attrs = context.resource.attributes

        time.sleep(60)

        try:
            quali_api = QualiAPISession(host="localhost", username="admin", password="admin", domain="Global")
        except Exception as e:
            err_print(api, res_id, "=== issue with quali api session ===")
            raise

        running_jobs = quali_api.get_running_jobs()
        if not running_jobs:
            warn_print(api, res_id, "running jobs is empty")
            raise Exception("No current running jobs")

        target_job_id = None
        for job in running_jobs:
            details = quali_api.get_job_details(job["JobId"])
            curr_topology_name = details["Topology"]["Name"]
            if curr_topology_name == blueprint_name:
                target_job_id = job["JobId"]
                break

        sb_print(api, res_id, "target job id: {}".format(target_job_id))

        job_id_attr = "{}.Current Job Id".format(model)
        api.SetServiceAttributesValues(reservationId=res_id,
                                       serviceAlias=service_name,
                                       attributeRequests=[
                                           AttributeNameValue(job_id_attr, target_job_id)])

    def send_report_mail(self, context):
        """
        get current job id and save as attribute on shell
        :param ResourceCommandContext context:
        :return:
        """
        api = shell_api_help.get_api_from_context(context)
        res_id = context.reservation.reservation_id
        reporter = self._get_reporter(context, api)

        resource = ReportingService.create_from_context(context)
        service_name = resource.name
        additional_recipients = resource.additional_recipients
        cc_recipients = resource.cc_recipients

        quali_server = context.connectivity.server_address
        admin_token = context.connectivity.admin_auth_token
        sb_owner_mail = context.reservation.owner_email

        if additional_recipients:
            recipients = sb_owner_mail + "," + additional_recipients
        else:
            recipients = sb_owner_mail

        model = context.resource.model
        attrs = context.resource.attributes

        current_job_id = attrs["{}.Current Job Id".format(model)]
        cs_https = attrs["{}.CS Https".format(model)]
        smtp_resource = attrs["{}.SMTP Resource".format(model)]
        server_protocol = "https" if cs_https == "True" else "http"

        server_date_string = time_help.get_server_formatted_date(api)
        server_date_string += " (UTC)"

        # validate that job id was added
        if not current_job_id:
            msg = "No Job Id Set On Reporting Service. Add set_job_id helper to 'finalize' in one test in the job."
            reporter.err_out(msg)
            self._send_error_report(context, custom_message=msg)
            raise Exception("Job Id not set to service. Can't get job report info from Quali API.")

        try:
            quali_api = QualiAPISession(host=quali_server, token_id=admin_token)
        except Exception as e:
            err_msg = "Issue establishing Quali API Session: {}".format(str(e))
            reporter.err_out(err_msg)
            self._send_error_report(context, err_msg)
            raise

        try:
            job_details = quali_api.get_job_details(current_job_id)
        except Exception as e:
            err_msg = "Could not get job details: {}".format(str(e))
            reporter.err_out(err_msg)
            self._send_error_report(context, err_msg)
            raise

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
        job_name = job_details["Name"]
        mail_inputs = [
            InputNameValue("message_title", "Custom Job Report: '{}', Ended: {}".format(job_name,
                                                                                        server_date_string)),
            InputNameValue("message_body", email_body),
            InputNameValue("recipients", recipients),
            InputNameValue("cc_recipients", cc_recipients)
        ]
        try:
            mail_response = api.ExecuteCommand(reservationId=res_id,
                                               targetName=smtp_resource,
                                               targetType="Resource",
                                               commandName="send_mail",
                                               commandInputs=mail_inputs)
        except Exception as e:
            err_msg = "Issue sending mail. Check '{}' SMTP Resource. Error: {}".format(smtp_resource, str(e))
            api.SetResourceLiveStatus(resourceFullName=service_name,
                                         liveStatusName="Error",
                                         additionalInfo=err_msg)
            raise Exception(err_msg)

        reporter.warn_out(mail_response.Output)

    def _send_error_report(self, context, custom_message=""):
        """
        get current job id and save as attribute on shell
        :param ResourceCommandContext context:
        :return:
        """
        api = shell_api_help.get_api_from_context(context)
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

        model = context.resource.model
        attrs = context.resource.attributes

        smtp_resource = attrs["{}.SMTP Resource".format(model)]

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
            reporter.err_out(err_msg)
            raise Exception(err_msg)
        reporter.info_out("Error Report Mail sent to {}".format(recipients))

    def set_test_data(self, context, test_id, test_data):
        """
        set custom
        :param ResourceCommandContext context:
        :return:
        """
        api = shell_api_help.get_api_from_context(context)
        res_id = context.reservation.reservation_id
        reporter = self._get_reporter(context, api)
        model = context.resource.model
        attrs = context.resource.attributes

        ms_timestamp = time_help.get_current_millisecond_timestamp()

        # save sandbox data
        sb_data = []
        data_key = "{}_{}".format(test_id, ms_timestamp)
        sb_timestamp_data = SandboxDataKeyValue(data_key, test_data)
        sb_data.append(sb_timestamp_data)
        try:
            api.SetSandboxData(res_id, sb_data)
        except Exception as e:
            msg = "issue setting test data with key '{}': {}".format(data_key)

        reporter.info_out("Setting sandbox data for key: {}".format(data_key))
        reporter.debug_out("=== Setting sandbox data ===\n{} - {}".format(data_key, test_data))
