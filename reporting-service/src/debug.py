from cloudshell.helpers.scripts.cloudshell_dev_helpers import attach_to_cloudshell_as
import cloudshell.helpers.scripts.cloudshell_scripts_helpers as sh
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, ConnectivityContext, \
    Connector, ReservationContextDetails, ResourceContextDetails
import driver as mydriver
from helper_code.quali_api_wrapper import QualiAPISession

LIVE_SANDBOX_ID = "33b70f5a-ed37-40de-87a0-b2125fa7245b"
SERVICE_NAME = "Reporting Service"

server = "qs-il-lt-nattik"

attach_to_cloudshell_as(
    user='admin',
    password='admin',
    domain='Global',
    server_address=server,
    reservation_id=LIVE_SANDBOX_ID,
    service_name=SERVICE_NAME
)

session = sh.get_api_session()
token = session.token_id
quali_api = QualiAPISession(host="localhost", token_id=token)
jobs = quali_api.get_running_jobs()

reservation_context_details = sh.get_reservation_context_details()
reservation_context = ReservationContextDetails(environment_name=reservation_context_details.environment_name,
                                                environment_path=reservation_context_details.environment_path,
                                                domain=reservation_context_details.domain,
                                                description=reservation_context_details.description,
                                                owner_user=reservation_context_details.owner_user,
                                                owner_email="natti.k@quali.com",
                                                reservation_id=reservation_context_details.id)

connectivity_context_details = sh.get_connectivity_context_details()
cs_api_port = connectivity_context_details.cloudshell_api_port
connectivity_context = ConnectivityContext(server_address=server, cloudshell_api_port=cs_api_port,
                                           quali_api_port="9000",
                                           admin_auth_token=token, cloudshell_version="9.3", cloudshell_api_scheme="")

context = ResourceCommandContext(
    connectivity=connectivity_context,
    resource=sh.get_resource_context_details(),
    reservation=reservation_context,
    connectors=""
)

debug_driver_instance = mydriver.ReportingServiceDriver()
# debug_driver_instance.set_test_data(context, "456", "okay okay")
debug_driver_instance.send_report_mail(context)
pass
