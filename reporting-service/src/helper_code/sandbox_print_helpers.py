"""
Module for storing convenience functions to print to sandbox console
"""
from cloudshell.api.cloudshell_api import CloudShellAPISession


# For returning output from shells, an api session is not needed
def _html_wrap(content, color, elm):
    return "<{elm} style='color: {color}'>{content}</{elm}>".format(content=content,
                                                                    elm=elm,
                                                                    color=color)


def err_wrap(content):
    return _html_wrap(content, "red", "span")


def success_wrap(content):
    return _html_wrap(content, "#4BB543", "span")


def warn_wrap(content):
    return _html_wrap(content, "yellow", "span")


# for printing to the output with an api session
def sb_print(api, reservation_id, message):
    """
    convenience printing method for printing to reservation output
    :param CloudShellAPISession api:
    :param str reservation_id:
    :param str message:
    :return:
    """
    api.WriteMessageToReservationOutput(reservation_id, message)


def sb_html_print(api, reservation_id, message, txt_color="white", html_elm="span"):
    """
    for wrapping message in custom html color and sizing
    :param CloudShellAPISession api:
    :param str reservation_id:
    :param str message:
    :param str txt_color: choose general color name or hex string
    :param str html_elm: select html element
    :return:
    """
    wrapped_message = _html_wrap(message, txt_color, html_elm)
    sb_print(api, reservation_id, wrapped_message)


def err_print(api, reservation_id, message):
    """
    print red message for errors
    :param CloudShellAPISession api:
    :param str reservation_id:
    :param str message:
    :return:
    """
    wrapped_message = err_wrap(message)
    sb_print(api, reservation_id, wrapped_message)


def success_print(api, reservation_id, message):
    """
    print green message for success statements
    :param CloudShellAPISession api:
    :param str reservation_id:
    :param str message:
    :return:
    """
    wrapped_message = success_wrap(message)
    sb_print(api, reservation_id, wrapped_message)


def warn_print(api, reservation_id, message):
    """
    print yellow message for alerting actions
    :param CloudShellAPISession api:
    :param str reservation_id:
    :param str message:
    :return:
    """
    wrapped_message = warn_wrap(message)
    sb_print(api, reservation_id, wrapped_message)


def sb_link_print(api, reservation_id, url, text):
    """
    for wrapping text in html anchor tag; opens link in new tab by default
    :param CloudShellAPISession api:
    :param str reservation_id:
    :param str url:
    :param str text: the link text to be displayed
    :return:
    """
    def html_link_wrap(target_url, link_text):
        return """<a href={url} 
               style="text-decoration: underline"
               target = "_blank"
               rel = "noopener noreferrer"
               >{link_text}</a>""".format(url=target_url, link_text=link_text)

    wrapped_link = html_link_wrap(url, text)
    sb_print(api, reservation_id, wrapped_link)


