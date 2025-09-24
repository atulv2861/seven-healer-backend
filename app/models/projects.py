from mongoengine import Document, StringField, IntField, ListField, DateTimeField
from datetime import datetime
import uuid

class Projects(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    title = StringField(required=True, max_length=200)
    location = StringField(required=True, max_length=100)
    beds = StringField(required=True, max_length=50)
    area = StringField(required=True, max_length=100)
    client = StringField(required=True, max_length=100)
    status = StringField(required=True, max_length=50, choices=["Completed", "In Progress", "Planning", "On Hold"])
    description = StringField(required=True, max_length=1000)
    features = ListField(StringField(), default=list)
    images = StringField(max_length=500)  # URL or path to image
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'projects',
        'indexes': ['title', 'client', 'status', 'created_at']
    }
    
    def save(self, *args, **kwargs):
        """Override save to update the updated_at field"""
        self.updated_at = datetime.utcnow()
        return super(Projects, self).save(*args, **kwargs)
