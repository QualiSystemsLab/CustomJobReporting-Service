from email_helper import send_email
import json

with open("debug_mail_config.json") as config:
    data = json.load(config)

try:
    send_email(smtp_user=data["smtp_user"],
               smtp_pass=data["smtp_pass"],
               smtp_address=data["smtp_address"],
               smtp_port=data["smtp_port"],
               message_title=data["message_title"],
               message_body=data["message_body"],
               recipients_list=data["recipients_list"],
               proxy_enabled=data["proxy_enabled"],
               proxy_host=data["proxy_host"],
               proxy_port=data["proxy_port"],
               smtp_auth_enabled=data["smtp_auth_enabled"],
               ssl_enabled=data["ssl_enabled"])
except Exception as e:
    print("=== issue sending email ===")
    raise
else:
    print("mail test passed with no errors :)")

pass
