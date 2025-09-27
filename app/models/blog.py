from mongoengine import Document, StringField, ListField, DateTimeField, EmbeddedDocument, EmbeddedDocumentListField
import uuid
from datetime import datetime

class ContentSection(EmbeddedDocument):
    """Embedded document for blog content sections"""
    heading = StringField(required=True, max_length=200)
    description = StringField(required=True)
    sub_sections = ListField(StringField(), default=list)  # For bullet points or sub-items

class Blog(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    title = StringField(required=True, max_length=200)
    slug = StringField(required=True, unique=True, max_length=250)
    excerpt = StringField(required=True)
    content = EmbeddedDocumentListField(ContentSection, required=True)
    image = StringField(max_length=1000000)  # Image URL or base64 encoded image
    author = StringField(required=True, max_length=100)
    author_bio = StringField(max_length=500)
    author_image = StringField(max_length=1000000)  # Author image URL or base64 encoded image
    published_at = DateTimeField(default=datetime.utcnow)
    tags = ListField(StringField(), default=list)
    is_published = StringField(default="draft", choices=["draft", "published", "archived"])
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'blogs',
        'indexes': [
            'slug',
            'published_at',
            'is_published',
            'author',
            'tags'
        ]
    }
    
    def save(self, *args, **kwargs):
        """Override save to update the updated_at field"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def generate_slug(self, title):
        """Generate a URL-friendly slug from title"""
        import re
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def set_slug_from_title(self):
        """Set slug from title if not provided"""
        if not self.slug:
            self.slug = self.generate_slug(self.title)
    
    def add_tag(self, tag):
        """Add a tag to the blog"""
        if tag and tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag):
        """Remove a tag from the blog"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def publish(self):
        """Publish the blog"""
        self.is_published = "published"
        if not self.published_at:
            self.published_at = datetime.utcnow()
    
    def unpublish(self):
        """Unpublish the blog"""
        self.is_published = "draft"
    
    def archive(self):
        """Archive the blog"""
        self.is_published = "archived"
    
    def add_content_section(self, heading, description, sub_sections=None):
        """Add a new content section to the blog"""
        section = ContentSection(
            heading=heading,
            description=description,
            sub_sections=sub_sections or []
        )
        self.content.append(section)
    
    def get_content_section(self, heading):
        """Get a content section by heading"""
        for section in self.content:
            if section.heading.lower() == heading.lower():
                return section
        return None
    
    def update_content_section(self, heading, new_description=None, new_sub_sections=None):
        """Update a content section"""
        section = self.get_content_section(heading)
        if section:
            if new_description is not None:
                section.description = new_description
            if new_sub_sections is not None:
                section.sub_sections = new_sub_sections
            return True
        return False
    
    def remove_content_section(self, heading):
        """Remove a content section by heading"""
        for i, section in enumerate(self.content):
            if section.heading.lower() == heading.lower():
                del self.content[i]
                return True
        return False
