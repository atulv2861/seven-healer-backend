from mongoengine import Document, StringField, BooleanField, EnumField, DateTimeField
from app.enum import UserRoles
import uuid
from datetime import datetime

class Users(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = StringField(required=True, max_length=50)
    last_name = StringField(required=True, max_length=50)
    email = StringField(required=True, unique=True, max_length=100)
    password = StringField(required=True)
    phone = StringField(required=True, max_length=15)
    role = EnumField(UserRoles, default=UserRoles.USER)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'users',
        'indexes': ['email']
    }
    
    def save(self, *args, **kwargs):
        """Override save to update the updated_at field"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)