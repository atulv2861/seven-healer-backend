from fastapi import APIRouter, HTTPException
from app.schemas.contact import EmailRequestSchema
from app.utils import get_email_template, send_simple_email

router = APIRouter()

@router.post("/send/email")
async def send_email(request: EmailRequestSchema):
    try:
        email_content = get_email_template(
                "email_temp.html",
                {
                    "name": request.name,
                    "phone": request.contact,
                    "address": request.address,
                    "message": request.message,                    
                },
            )
        # Send email to company
        send_simple_email(
            recipients=request.email,
            subject=request.subject,
            body=email_content,
            content_type="html",
        ) 
        confirmation_content = get_email_template(
            "comfirmation_temp.html",
            {
                "name": request.name,
                "subject": request.subject,
                "message": request.message,
            },
        )
        # Send email to client
        send_simple_email(
            recipients=request.email,
            subject=request.subject,
            body=confirmation_content,
            content_type="html",
        )
        return {
            "status": "success",
            "message": "Email sent successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))