from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.shell.core.driver_context import ResourceCommandContext


def get_api_from_context(context):
    """
    for commands run directly on the resource
    :param ResourceCommandContext context:
    :return:
    """
    return CloudShellAPISession(host=context.connectivity.server_address,
                                token_id=context.connectivity.admin_auth_token,
                                domain=context.reservation.domain)


def recursive_decrypt_password(api, password):
    """
    At times shell password data types can be doubly encrypted.
    Will throw exception when trying to decrypt non base 64 string and return the real password
    :param CloudShellAPISession api:
    :param str password:
    :return:
    """
    def api_decrypt(api_session, pw_input_str):
        decrypted = api_session.DecryptPassword(pw_input_str).Value
        return decrypted

    i = 0
    while i < 5:
        try:
            password = api_decrypt(api, password)
        except Exception:
            i = 1000
        i = i + 1

    return password
