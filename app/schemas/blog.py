from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ContentSectionSchema(BaseModel):
    """Schema for blog content sections"""
    heading: str = Field(..., max_length=200, description="Section heading")
    description: str = Field(..., description="Section description/content")
    sub_sections: List[str] = Field(default_factory=list, description="List of sub-items or bullet points")

class BlogBaseSchema(BaseModel):
    title: str = Field(..., max_length=200, description="Blog title")
    slug: Optional[str] = Field(None, max_length=250, description="URL-friendly slug")
    excerpt: str = Field(..., max_length=500, description="Blog excerpt/summary")
    content: List[ContentSectionSchema] = Field(..., description="Blog content sections")
    image: Optional[str] = Field(None, max_length=1000000, description="Blog image URL or base64 encoded image")
    author: str = Field(..., max_length=100, description="Author name")
    author_bio: Optional[str] = Field(None, max_length=500, description="Author biography")
    author_image: Optional[str] = Field(None, max_length=1000000, description="Author image URL or base64 encoded image")
    published_at: Optional[datetime] = Field(None, description="Publication date")
    tags: List[str] = Field(default_factory=list, description="Blog tags")
    is_published: str = Field(default="draft", description="Publication status")

class BlogCreateSchema(BlogBaseSchema):
    pass

class BlogUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, max_length=200, description="Blog title")
    slug: Optional[str] = Field(None, max_length=250, description="URL-friendly slug")
    excerpt: Optional[str] = Field(None, max_length=500, description="Blog excerpt/summary")
    content: Optional[List[ContentSectionSchema]] = Field(None, description="Blog content sections")
    image: Optional[str] = Field(None, max_length=1000000, description="Blog image URL or base64 encoded image")
    author: Optional[str] = Field(None, max_length=100, description="Author name")
    author_bio: Optional[str] = Field(None, max_length=500, description="Author biography")
    author_image: Optional[str] = Field(None, max_length=1000000, description="Author image URL or base64 encoded image")
    published_at: Optional[datetime] = Field(None, description="Publication date")
    tags: Optional[List[str]] = Field(None, description="Blog tags")
    is_published: Optional[str] = Field(None, description="Publication status")

class BlogResponseSchema(BaseModel):
    id: str
    title: str
    slug: str
    excerpt: str
    content: List[ContentSectionSchema]
    image: Optional[str]
    author: str
    author_bio: Optional[str]
    author_image: Optional[str]
    published_at: datetime
    tags: List[str]
    is_published: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BlogListResponseSchema(BaseModel):
    blogs: List[BlogResponseSchema]
    total: int
    page: int
    limit: int

class BlogStatusUpdateSchema(BaseModel):
    is_published: str = Field(..., description="Publication status: draft, published, or archived")

class BlogTagUpdateSchema(BaseModel):
    tags: List[str] = Field(..., description="List of tags")

class ContentSectionUpdateSchema(BaseModel):
    """Schema for updating a specific content section"""
    heading: str = Field(..., description="Section heading to update")
    new_heading: Optional[str] = Field(None, description="New heading (if changing)")
    description: Optional[str] = Field(None, description="New description")
    sub_sections: Optional[List[str]] = Field(None, description="New sub-sections")

class ContentSectionAddSchema(BaseModel):
    """Schema for adding a new content section"""
    heading: str = Field(..., description="Section heading")
    description: str = Field(..., description="Section description")
    sub_sections: List[str] = Field(default_factory=list, description="List of sub-items")
