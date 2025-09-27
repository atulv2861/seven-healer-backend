
import os
import smtplib
import re
from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi.security import OAuth2PasswordBearer, HTTPBasic, HTTPBasicCredentials
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from fastapi import HTTPException, UploadFile
from app.core.config import config
from app.models.users import Users
from app.enum import UserRoles
from passlib.context import CryptContext



password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
httpBasic = HTTPBasic()
class OTPOAuth2PasswordBearer(OAuth2PasswordBearer):
    pass


class PasswordOAuth2PasswordBearer(OAuth2PasswordBearer):
    pass


password_oauth2_scheme = PasswordOAuth2PasswordBearer(tokenUrl="auth/login")
otp_oauth2_scheme = OTPOAuth2PasswordBearer(tokenUrl="auth/verify-otp")


superUser = {
    "id": config.SUPERUSER_ID,
    "profile": {"firstName": "Super", "lastName": "User", "avatar": "None"},
    "name": "SuperUser",
    "role": UserRoles.ADMIN.value,
    "email": config.SUPERUSER_EMAIL,
}


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def create_access_token(subject: str, expires_delta: int | None = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now(timezone.utc) + expires_delta
    else:
        expires_delta = datetime.now(timezone.utc) + timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET_KEY, config.ALGORITHM)
    return encoded_jwt

def authenticate_user(email: str, password: str):
    """Authenticate user with email and password"""
    # Check superuser first
    if email == config.SUPERUSER_EMAIL and password == config.SUPERUSER_PASSWORD:
        return superUser
    
    # Check regular users
    user = Users.objects(email=email.lower()).first()
    if not user:
        return False
    
    if not user.is_active:
        return False
    
    if verify_password(password, user.password):
        return user
    return False

def get_current_user(token: str):
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        
        # Check if it's superuser
        if email == config.SUPERUSER_EMAIL:
            return superUser
        
        # Get regular user
        user = Users.objects(email=email).first()
        return user
    except jwt.JWTError:
        return None

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