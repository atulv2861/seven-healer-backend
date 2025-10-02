from fastapi import APIRouter, HTTPException, Form, File, UploadFile, Request
from typing import List, Optional, Union
from app.schemas.contact import EmailRequestSchema
from app.utils import get_email_template, send_simple_email, validate_file_size

router = APIRouter()

@router.post("/send/email")
async def send_email(
    request: Request,
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    name: str = Form(...),
    contact: str = Form(...),
    address: str = Form(...),
    files: List[UploadFile] = File(None)
):
    try:
        # Check if request is JSON or form data
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            # Handle JSON request
            json_data = await request.json()
            email = json_data.get("email")
            subject = json_data.get("subject")
            message = json_data.get("message")
            name = json_data.get("name")
            contact = json_data.get("contact")
            address = json_data.get("address")
            files = None  # No files in JSON request
        else:
            # Handle form data request
            # Form data is already extracted by FastAPI parameters
            pass
        
        # Validate required fields (form fields are already mandatory, but check JSON fields)
        if "application/json" in content_type:
            if not all([email, subject, message, name, contact, address]):
                raise HTTPException(
                    status_code=400,
                    detail="Missing required fields: email, subject, message, name, contact, address"
                )
        
        # Validate file sizes if files are provided
        if files:
            for file in files:
                if file and file.filename:
                    if not validate_file_size(file, 10):  # 10MB limit
                        raise HTTPException(
                            status_code=400,
                            detail=f"File {file.filename} is too large. Maximum size is 10MB."
                        )
        
        # Prepare email content for company notification
        email_content = get_email_template(
                "email_temp.html",
                {
                    "name": name,
                    "phone": contact,
                    "address": address,
                    "message": message,                    
                },
            )       
        
        # Send email to company with attachments
        send_simple_email(
            recipients=email,
            subject=subject,
            body=email_content,
            content_type="html",
            attachments=files
        )
        
        # Prepare confirmation email for client
        confirmation_content = get_email_template(
            "comfirmation_temp.html",
            {
                "name": name,
                "subject": subject,
                "message": message,
            },
        )
        
        # Send confirmation email to client (without attachments)
        send_simple_email(
            recipients=email,
            subject=f"Confirmation: {subject}",
            body=confirmation_content,
            content_type="html",
        )
        return {
            "status": "success",
            "message": "Email sent successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send/cv")
async def send_email(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    files: List[UploadFile] = File(None)
):
    try:
        # Check if request is JSON or form data
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            # Handle JSON request
            json_data = await request.json()
            email = json_data.get("email")
            full_name = json_data.get("full_name")
            phone = json_data.get("phone")
            files = None  # No files in JSON request
        else:
            # Handle form data request
            # Form data is already extracted by FastAPI parameters
            pass
        
        # Validate required fields (form fields are already mandatory, but check JSON fields)
        if "application/json" in content_type:
            if not all([email, full_name, phone]):
                raise HTTPException(
                    status_code=400,
                    detail="Missing required fields: email, full_name, phone"
                )
        
        # Validate file sizes if files are provided
        if files:
            for file in files:
                if file and file.filename:
                    if not validate_file_size(file, 10):  # 10MB limit
                        raise HTTPException(
                            status_code=400,
                            detail=f"File {file.filename} is too large. Maximum size is 10MB."
                        )
        
        # Prepare email content for company notification
        email_content = get_email_template(
                "cv_email_temp.html",
                {
                    "name": full_name,
                    "phone": phone,                    
                },
            )       
        
        # Send email to company with attachments
        send_simple_email(
            recipients=email,
            subject=f"CV: {full_name}",
            body=email_content,
            content_type="html",
            attachments=files
        )
        
        # Prepare confirmation email for client
        confirmation_content = get_email_template(
            "cv_comfirmation_temp.html",
            {
                "name": full_name,
                "subject": f"CV: {full_name}"
            },
        )
        
        # Send confirmation email to client (without attachments)
        send_simple_email(
            recipients=email,
            subject=f"Confirmation CV: {full_name}",
            body=confirmation_content,
            content_type="html",
        )
        return {
            "status": "success",
            "message": "Email sent successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))