
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException
from app.core import config

def get_email_template(filename, context):
    try:
        file_path = os.path.join("app/templates", filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Email template file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as file:
            template = file.read()
            
        # Replace template variables
        for key, value in context.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
            
        return template
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def send_simple_email(recipients: str, subject: str, body: str, content_type="plain"):
    try:
        sender_email = config.SMTP_USERNAME                
        sender_password = config.SMTP_PASSWORD

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipients
        msg["Subject"] = subject
        msg.attach(MIMEText(body, content_type))

        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as smtp_server:
            smtp_server.starttls()
            smtp_server.login(sender_email, sender_password)
            smtp_server.sendmail(sender_email, recipients, msg.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))