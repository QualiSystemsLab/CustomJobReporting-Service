from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadDetails, \
    CancellationContext, AutoLoadCommandContext
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext

from data_model import *  # run 'shellfoundry generate' to generate data model classes
from email_helper import send_email

import automation_api_helpers as auto_api_help
from common_helpers import get_list_from_comma_separated_string


class SMTPServerException(Exception):
    pass


class SmtpServerDriver(ResourceDriverInterface):

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

    # <editor-fold desc="Discovery">

    def get_inventory(self, context):
        """
        Discovers the resource structure and attributes.
        :param AutoLoadCommandContext context: the context the command runs on
        :return Attribute and sub-resource information for the Shell resource you can return an AutoLoadDetails object
        :rtype: AutoLoadDetails
        """
        # See below some example code demonstrating how to return the resource structure and attributes
        # In real life, this code will be preceded by SNMP/other calls to the resource details and will not be static
        # run 'shellfoundry generate' in order to create classes that represent your data model
        '''
        resource = SmtpServer.create_from_context(context)
        resource.vendor = 'specify the shell vendor'
        resource.model = 'specify the shell model'

        port1 = ResourcePort('Port 1')
        port1.ipv4_address = '192.168.10.7'
        resource.add_sub_resource('1', port1)

        return resource.create_autoload_details()
        '''
        return AutoLoadDetails([], [])

    # </editor-fold>

    # <editor-fold desc="Orchestration Save and Restore Standard">
    def orchestration_save(self, context, cancellation_context, mode, custom_params):
        """
        Saves the Shell state and returns a description of the saved artifacts and information
        This command is intended for API use only by sandbox orchestration scripts to implement
        a save and restore workflow
        :param ResourceCommandContext context: the context object containing resource and reservation info
        :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
        :param str mode: Snapshot save mode, can be one of two values 'shallow' (default) or 'deep'
        :param str custom_params: Set of custom parameters for the save operation
        :return: SavedResults serialized as JSON
        :rtype: OrchestrationSaveResult
        """

        # See below an example implementation, here we use jsonpickle for serialization,
        # to use this sample, you'll need to add jsonpickle to your requirements.txt file
        # The JSON schema is defined at:
        # https://github.com/QualiSystems/sandbox_orchestration_standard/blob/master/save%20%26%20restore/saved_artifact_info.schema.json
        # You can find more information and examples examples in the spec document at
        # https://github.com/QualiSystems/sandbox_orchestration_standard/blob/master/save%20%26%20restore/save%20%26%20restore%20standard.md
        '''
              # By convention, all dates should be UTC
              created_date = datetime.datetime.utcnow()
  
              # This can be any unique identifier which can later be used to retrieve the artifact
              # such as filepath etc.
  
              # By convention, all dates should be UTC
              created_date = datetime.datetime.utcnow()
  
              # This can be any unique identifier which can later be used to retrieve the artifact
              # such as filepath etc.
              identifier = created_date.strftime('%y_%m_%d %H_%M_%S_%f')
  
              orchestration_saved_artifact = OrchestrationSavedArtifact('REPLACE_WITH_ARTIFACT_TYPE', identifier)
  
              saved_artifacts_info = OrchestrationSavedArtifactInfo(
                  resource_name="some_resource",
                  created_date=created_date,
                  restore_rules=OrchestrationRestoreRules(requires_same_resource=True),
                  saved_artifact=orchestration_saved_artifact)
  
              return OrchestrationSaveResult(saved_artifacts_info)
        '''
        pass

    def orchestration_restore(self, context, cancellation_context, saved_artifact_info, custom_params):
        """
        Restores a saved artifact previously saved by this Shell driver using the orchestration_save function
        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
        :param str saved_artifact_info: A JSON string representing the state to restore including saved artifacts and info
        :param str custom_params: Set of custom parameters for the restore operation
        :return: None
        """
        '''
        # The saved_details JSON will be defined according to the JSON Schema and is the same object returned via the
        # orchestration save function.
        # Example input:
        # {
        #     "saved_artifact": {
        #      "artifact_type": "REPLACE_WITH_ARTIFACT_TYPE",
        #      "identifier": "16_08_09 11_21_35_657000"
        #     },
        #     "resource_name": "some_resource",
        #     "restore_rules": {
        #      "requires_same_resource": true
        #     },
        #     "created_date": "2016-08-09T11:21:35.657000"
        #    }

        # The example code below just parses and prints the saved artifact identifier
        saved_details_object = json.loads(saved_details)
        return saved_details_object[u'saved_artifact'][u'identifier']
        '''
        pass

    # </editor-fold>

    def send_mail(self, context, message_title, message_body, recipients, cc_recipients=""):
        """
        Gets smtp credentials from shell and passes into email helper
        :param ResourceCommandContext context:
        :param str message_title: title of email
        :param str message_body: body of mail. can be html
        :param str recipients: comma separated list of people to send mail to
        :param str cc_recipients: comma separated list of people to put in cc
        :return:
        """
        api = CloudShellSessionContext(context).get_api()
        resource = SmtpServer.create_from_context(context)

        resource_name = context.resource.fullname

        if not recipients:
            raise ValueError("Recipients list must be populated")

        smtp_ip = context.resource.address
        smtp_user, smtp_password = auto_api_help.get_resource_credentials(api, context.resource.name)

        smtp_port = int(resource.smtp_port)
        ssl_enabled = True if resource.ssl_enabled == "True" else False
        proxy_enabled = True if resource.proxy_enabled == "True" else False
        proxy_host = resource.proxy_host
        proxy_port = int(resource.proxy_port)
        is_smtp_auth = True if resource.smtp_auth_enabled == "True" else False

        recipients_list = get_list_from_comma_separated_string(recipients)
        cc_list = get_list_from_comma_separated_string(cc_recipients)

        try:
            send_email(smtp_user=smtp_user,
                       smtp_pass=smtp_password,
                       smtp_address=smtp_ip,
                       smtp_port=smtp_port,
                       message_title=message_title,
                       message_body=message_body,
                       recipients_list=recipients_list,
                       cc_recipients=cc_list,
                       proxy_enabled=proxy_enabled,
                       proxy_host=proxy_host,
                       proxy_port=proxy_port,
                       smtp_auth_enabled=is_smtp_auth,
                       ssl_enabled=ssl_enabled)
        except Exception as e:
            err_msg = f"Issue sending mail. Error: {str(e)}"
            api.SetResourceLiveStatus(resourceFullName=resource_name,
                                      liveStatusName="Error",
                                      additionalInfo=err_msg)
            raise SMTPServerException(err_msg)
        api.SetResourceLiveStatus(resourceFullName=resource_name,
                                  liveStatusName="Online",
                                  additionalInfo="SMTP server online. Last mail sent to '{}'".format(recipients))
        comma_separated_recipients = ",".join(recipients_list)
        return f"mail sent to '{comma_separated_recipients}'"

    def send_test_mail(self, context):
        """
        send test mail to owner of sandbox to check SMTP connectivity
        :param ResourceCommandContext context:
        :return:
        """
        resource = SmtpServer.create_from_context(context)
        resource_name = context.resource.fullname

        smtp_user = resource.user

        msg_body = "<h2>This is a test mail from Cloudshell SMTP Resource '{}'</h2>".format(resource_name)
        self.send_mail(context=context,
                       message_title="Cloudshell Admin Service Test",
                       message_body=msg_body,
                       recipients=smtp_user)

        return "test email sent to {}".format(smtp_user)
