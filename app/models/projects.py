from mongoengine import Document, StringField, IntField, ListField, DateTimeField, BinaryField, EmbeddedDocumentField, EmbeddedDocument
from datetime import datetime
import uuid
import base64

class Projects(Document):
    class Details(EmbeddedDocument):
        heading = StringField(required=True)
        description = StringField(required=True)
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    title = StringField(required=True, max_length=200)
    location = StringField(required=True, max_length=100)
    beds = StringField(required=True, max_length=50)
    area = StringField(required=True, max_length=100)
    client = StringField(required=True, max_length=100)
    status = StringField(required=True, max_length=50, choices=["Completed", "In Progress", "Planning", "On Hold"])
    description = StringField(required=True)
    features = ListField(StringField(), default=list)
    image = StringField()  # Single base64 encoded image
    image_name = StringField()  # Original image name
    details = ListField(EmbeddedDocumentField(Details), default=[])
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'projects',
        'indexes': ['title', 'client', 'status', 'created_at']
    }
    
    def set_image(self, image_data, image_name):
        """Set a base64 encoded image for the project"""
        # Ensure image_data is base64 encoded
        if isinstance(image_data, bytes):
            image_data = base64.b64encode(image_data).decode('utf-8')
        
        self.image = image_data
        self.image_name = image_name
    
    def get_image(self):
        """Get image data"""
        if self.image:
            return {
                'data': self.image,
                'name': self.image_name or 'project_image'
            }
        return None
    
    def remove_image(self):
        """Remove image"""
        self.image = None
        self.image_name = None
    
    def has_image(self):
        """Check if project has an image"""
        return bool(self.image)
    
    
    def save(self, *args, **kwargs):
        """Override save to update the updated_at field"""
        self.updated_at = datetime.utcnow()
        return super(Projects, self).save(*args, **kwargs)
