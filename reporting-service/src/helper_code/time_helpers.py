"""
shared time helper functions
"""
from cloudshell.api.cloudshell_api import CloudShellAPISession
from datetime import datetime, timedelta


def get_current_millisecond_timestamp():
    now = datetime.utcnow()
    epoch = datetime(1970, 1, 1)
    delta = now - epoch
    s = delta.total_seconds()
    ms = int(s * 1000)
    return ms


# ===== Cloudshell Datetime helpers =====
def _get_datetime_from_cs_format(cs_time):
    dt = datetime.strptime(cs_time, "%m/%d/%Y %H:%M")
    return dt


def _get_current_server_datetime(api):
    """
    :param CloudShellAPISession api:
    :return:
    """
    current_time = api.GetServerDateAndTime().ServerDateTime
    current_dt = _get_datetime_from_cs_format(current_time)
    return current_dt


def get_server_formatted_date(api):
    dt = _get_current_server_datetime(api)
    formatted = dt.strftime('%d-%m-%y %H:%M:%S')
    return formatted


def get_date_string_from_ms_timestamp(milliseconds):
    date = datetime(1970, 1, 1) + timedelta(seconds=milliseconds/1000)
    date_str = date.strftime('%d-%m-%y %H:%M:%S')
    # date_str = datetime.fromtimestamp(milliseconds).strftime('%Y-%m-%d %H:%M:%S.%f') # throws out of range error
    return date_str
    pass


def get_date_string_from_ISO8601_str(ISO_8601_str):
    """
    ex. "2020-01-29T14:00:16 -- > 2020-01-29 14:00:16
    :param ISO_8601_str: such as job endtime - "
    :return:
    """
    dt = datetime.strptime(ISO_8601_str, "%Y-%m-%dT%H:%M:%S")
    output_date = dt.strftime('%Y-%m-%d %H:%M:%S')
    return output_date