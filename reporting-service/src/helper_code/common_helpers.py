"""
shared helper functions
"""


def get_list_from_comma_separated_string(comma_separated_list):
    """
    get a python list of resource names from comma separated list
    :param str comma_separated_list:
    :return:
    """
    import re
    # remove all extra whitespace after commas and before/after string but NOT in between resource names
    removed_whitespace_str = re.sub(r"(,\s+)", ",", comma_separated_list).strip()
    resource_names = removed_whitespace_str.split(",")
    return resource_names







