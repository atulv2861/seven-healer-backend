
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from fastapi import HTTPException, UploadFile
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


def validate_file_size(file: UploadFile, max_size_mb: int = 10) -> bool:
    """Validate file size (default 10MB limit)"""
    if not file:
        return True
    
    # Get file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes


def send_simple_email(recipients: str, subject: str, body: str, content_type="plain", attachments: list[UploadFile] | None = None):
    try:
        sender_email = config.SMTP_USERNAME                
        sender_password = config.SMTP_PASSWORD

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipients
        msg["Subject"] = subject
        msg.attach(MIMEText(body, content_type))

        # Add file attachments if provided
        if attachments:
            for attachment in attachments:
                if attachment and attachment.filename:
                    # Validate file size (10MB limit)
                    if not validate_file_size(attachment, 10):
                        raise HTTPException(
                            status_code=400, 
                            detail=f"File {attachment.filename} is too large. Maximum size is 10MB."
                        )
                    
                    # Read file content
                    file_content = attachment.file.read()
                    attachment.file.seek(0)  # Reset file pointer
                    
                    # Create MIME attachment
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file_content)
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment.filename}'
                    )
                    msg.attach(part)

        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as smtp_server:
            smtp_server.starttls()
            smtp_server.login(sender_email, sender_password)
            smtp_server.sendmail(sender_email, recipients, msg.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))