from mongoengine import Document, StringField, BooleanField, EnumField
from app.enum import UserRoles
import uuid

class Users(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = StringField(required=True, max_length=50)
    last_name = StringField(required=True, max_length=50)
    email = StringField(required=True, unique=True, max_length=100)
    password = StringField(required=True)
    phone = StringField(required=True, max_length=15)
    role = EnumField(UserRoles, default=UserRoles.USER)
    is_active = BooleanField(default=True)
    
    meta = {
        'collection': 'users',
        'indexes': ['email']
    }