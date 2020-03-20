import os

from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext
# from data_model import *  # run 'shellfoundry generate' to generate data model classes
from helper_code.quali_api_wrapper import QualiAPISession
import helper_code.shell_api_helpers as shell_api_help
import helper_code.automation_api_helpers as auto_api_help
from helper_code.sandbox_print_helpers import *
import helper_code.time_helpers as time_help
import json
import time
from cloudshell.api.cloudshell_api import AttributeNameValue, InputNameValue, SandboxDataKeyValue
from format_html import format_html_template

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

    def _get_current_job_id(self, context):
        """
        get current job id and save as attribute on shell (not used right now in solution)
        :param ResourceCommandContext context:
        :return:
        """
        api = shell_api_help.get_api_from_context(context)
        res_id = context.reservation.reservation_id

        blueprint_name = context.reservation.environment_name
        sb_print(api, res_id, "blueprint name test - {}".format(blueprint_name))

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

        quali_server = context.connectivity.server_address
        admin_token = context.connectivity.admin_auth_token
        sb_owner_mail = context.reservation.owner_email

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
            self._send_error_report(context, custom_message="No Job Id Set On Reporting Service")
            return
            # raise Exception("Job Id not set to service. Can't get report info from Quali API")

        try:
            quali_api = QualiAPISession(host=quali_server, token_id=admin_token)
        except Exception as e:
            err_print(api, res_id, "=== issue with quali api session ===")
            self._send_error_report(context, "Issue establishing Quali API Session: {}".format(str(e)))
            return
            # raise
        else:
            job_details = quali_api.get_job_details(current_job_id)

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
            InputNameValue("recipients", sb_owner_mail)]
        try:
            mail_response = api.ExecuteCommand(reservationId=res_id,
                                               targetName=smtp_resource,
                                               targetType="Resource",
                                               commandName="send_mail",
                                               commandInputs=mail_inputs)
        except Exception as e:
            err_print(api, res_id, "=== Issue sending mail ===")
            err_print(api, res_id, str(e))
            info = "Issue sending mail. Check '{}' SMTP Resource. Error: {}".format(smtp_resource, str(e))
            api.SetReservationLiveStatus(reservationId=res_id,
                                         liveStatusName="Error",
                                         additionalInfo=info)
            # raise
        else:
            warn_print(api, res_id, mail_response.Output)

    @staticmethod
    def _send_error_report(context, custom_message=""):
        """
        get current job id and save as attribute on shell
        :param ResourceCommandContext context:
        :return:
        """
        api = shell_api_help.get_api_from_context(context)
        res_id = context.reservation.reservation_id
        environment_name = context.reservation.environment_name

        sb_owner_mail = context.reservation.owner_email

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
            InputNameValue("recipients", sb_owner_mail)]
        try:
            mail_response = api.ExecuteCommand(reservationId=res_id,
                                               targetName=smtp_resource,
                                               targetType="Resource",
                                               commandName="send_mail",
                                               commandInputs=mail_inputs)
        except Exception as e:
            err_print(api, res_id, "=== Issue sending mail ===")
            raise
        else:
            warn_print(api, res_id, "Error Report Mail sent to {}".format(sb_owner_mail))

    def set_test_data(self, context, test_id, test_data):
        """
        set custom
        :param ResourceCommandContext context:
        :return:
        """
        api = shell_api_help.get_api_from_context(context)
        res_id = context.reservation.reservation_id

        model = context.resource.model
        attrs = context.resource.attributes

        ms_timestamp = time_help.get_current_millisecond_timestamp()

        # save sandbox data
        sb_data = []
        data_key = "{}_{}".format(test_id, ms_timestamp)
        sb_timestamp_data = SandboxDataKeyValue(data_key, test_data)
        sb_data.append(sb_timestamp_data)
        api.SetSandboxData(res_id, sb_data)
