import smtplib
from email.message import EmailMessage


def send_email(smtp_config, subject, body, recipients):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = smtp_config["sender"]
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP(smtp_config["smtp_server"], smtp_config["smtp_port"]) as server:
        server.starttls()
        server.login(smtp_config["smtp_username"], smtp_config["smtp_password"])
        server.send_message(msg)
