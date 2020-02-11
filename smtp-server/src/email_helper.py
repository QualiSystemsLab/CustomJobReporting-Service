import smtplib
import socks  # pip install PySocks
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(smtp_user, smtp_pass, smtp_address, smtp_port, message_title, message_body, recipients_list,
               smtp_auth_enabled=True, ssl_enabled=True, proxy_enabled=False, proxy_host="", proxy_port="", ):
    """
    send email to list of users. First member is primary, the rest in CC
    :param str smtp_user:
    :param str smtp_pass:
    :param str smtp_address:
    :param int smtp_port:
    :param str message_title:
    :param str message_body:
    :param list recipients_list:
    :param bool smtp_auth_enabled:
    :param bool ssl_enabled:
    :param bool proxy_enabled:
    :param str proxy_host:
    :param int proxy_port:
    :return:
    """

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = message_title
    msg['From'] = smtp_user
    msg['To'] = recipients_list[0]
    if len(recipients_list) > 1:
        msg['Cc'] = ', '.join(recipients_list[1:])

    # Create the body of the message (a plain-text and an HTML version).

    text = message_body
    html = message_body

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    if proxy_enabled:
        socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, proxy_host, proxy_port)
        socks.wrapmodule(smtplib)

    # Send the message via local SMTP server.
    try:
        smtp_session = smtplib.SMTP(smtp_address, smtp_port)
    except Exception:
        raise
    else:
        # smtp_session.connect(smtp_address, smtp_port)

        if ssl_enabled:
            smtp_session.ehlo()
            smtp_session.starttls()
            smtp_session.ehlo()

        if smtp_auth_enabled:
            smtp_session.login(smtp_user, smtp_pass)

        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        smtp_session.sendmail(smtp_user, recipients_list, msg.as_string())
        # end smtp session
        smtp_session.quit()
    finally:
        if proxy_enabled:
            # reset proxy settings so as not to interfere with automation api
            socks.set_default_proxy()
