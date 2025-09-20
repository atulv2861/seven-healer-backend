from pydantic import BaseModel


class EmailRequestSchema(BaseModel):
    email: str
    subject: str
    message: str
    name: str
    contact: str
    address: str
    