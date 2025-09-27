from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from datetime import datetime
import re

from app.models.blog import Blog
from app.schemas.blog import (
    BlogCreateSchema,
    BlogUpdateSchema,
    BlogResponseSchema,
    BlogListResponseSchema,
    BlogStatusUpdateSchema,
    BlogTagUpdateSchema,
    ContentSectionUpdateSchema,
    ContentSectionAddSchema,
    ContentSectionSchema
)
from app.services.auth import get_current_user_dependency

router = APIRouter()

def generate_slug(title: str) -> str:
    """Generate a URL-friendly slug from title"""
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def ensure_unique_slug(slug: str, exclude_id: str = None) -> str:
    """Ensure slug is unique by appending number if needed"""
    original_slug = slug
    counter = 1
    
    while True:
        query = Blog.objects(slug=slug)
        if exclude_id:
            query = query.filter(id__ne=exclude_id)
        
        if not query.first():
            return slug
        
        slug = f"{original_slug}-{counter}"
        counter += 1

def convert_blog_to_response(blog: Blog) -> BlogResponseSchema:
    """Convert blog model to response schema"""
    # Convert content sections to response format
    content_response = []
    for section in blog.content:
        content_response.append(ContentSectionSchema(
            heading=section.heading,
            description=section.description,
            sub_sections=section.sub_sections
        ))
    
    return BlogResponseSchema(
        id=str(blog.id),
        title=blog.title,
        slug=blog.slug,
        excerpt=blog.excerpt,
        content=content_response,
        image=blog.image,
        author=blog.author,
        author_bio=blog.author_bio,
        author_image=blog.author_image,
        published_at=blog.published_at,
        tags=blog.tags,
        is_published=blog.is_published,
        created_at=blog.created_at,
        updated_at=blog.updated_at
    )

@router.post("/", response_model=BlogResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_blog(
    blog_data: BlogCreateSchema,
    current_user = Depends(get_current_user_dependency)
):
    """
    Create a new blog post (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not (isinstance(current_user, dict) or 
                (hasattr(current_user, 'role') and current_user.role.value == 'admin')):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can create blog posts"
            )
        
        # Generate slug if not provided
        slug = blog_data.slug or generate_slug(blog_data.title)
        slug = ensure_unique_slug(slug)
        
        # Convert content sections to embedded documents
        content_sections = []
        for section_data in blog_data.content:
            from app.models.blog import ContentSection
            section = ContentSection(
                heading=section_data.heading,
                description=section_data.description,
                sub_sections=section_data.sub_sections or []
            )
            content_sections.append(section)
        
        # Create new blog
        new_blog = Blog(
            title=blog_data.title,
            slug=slug,
            excerpt=blog_data.excerpt,
            content=content_sections,
            image=blog_data.image,
            author=blog_data.author,
            author_bio=blog_data.author_bio,
            author_image=blog_data.author_image,
            published_at=blog_data.published_at or datetime.utcnow(),
            tags=blog_data.tags or [],
            is_published=blog_data.is_published
        )
        
        new_blog.save()
        
        return convert_blog_to_response(new_blog)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating blog: {str(e)}"
        )

@router.get("/", response_model=BlogListResponseSchema)
async def get_blogs(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    """
    Get all published blog posts with pagination (Public access)
    """
    try:
        # Build query filters
        query_filters = {}
        
        # For public access, only show published blogs
        query_filters['is_published'] = 'published'
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Get blogs with filters
        blogs_query = Blog.objects(**query_filters)
        total_blogs = blogs_query.count()
        
        blogs = blogs_query.skip(skip).limit(limit).order_by('-published_at', '-created_at')
        
        # Convert to response format
        blog_list = []
        for blog in blogs:
            blog_list.append(convert_blog_to_response(blog))
        
        return BlogListResponseSchema(
            blogs=blog_list,
            total=total_blogs,
            page=page,
            limit=limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving blogs: {str(e)}"
        )

@router.get("/admin", response_model=BlogListResponseSchema)
async def get_all_blogs_admin(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    is_published: Optional[str] = Query(None, description="Filter by publication status"),
    author: Optional[str] = Query(None, description="Filter by author"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    current_user = Depends(get_current_user_dependency)
):
    """
    Get all blog posts with pagination and filtering (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not (isinstance(current_user, dict) or 
                (hasattr(current_user, 'role') and current_user.role.value == 'admin')):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can access all blogs"
            )
        
        # Build query filters
        query_filters = {}
        
        # Admin can see all blogs regardless of status
        if is_published:
            query_filters['is_published'] = is_published
        
        if author:
            query_filters['author__icontains'] = author
        
        if tag:
            query_filters['tags__in'] = [tag]
        
        if search:
            query_filters['$or'] = [
                {'title__icontains': search},
                {'excerpt__icontains': search},
                {'content.heading__icontains': search},
                {'content.description__icontains': search}
            ]
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Get blogs with filters
        blogs_query = Blog.objects(**query_filters)
        total_blogs = blogs_query.count()
        
        blogs = blogs_query.skip(skip).limit(limit).order_by('-published_at', '-created_at')
        
        # Convert to response format
        blog_list = []
        for blog in blogs:
            blog_list.append(convert_blog_to_response(blog))
        
        return BlogListResponseSchema(
            blogs=blog_list,
            total=total_blogs,
            page=page,
            limit=limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving blogs: {str(e)}"
        )

@router.get("/{blog_id}", response_model=BlogResponseSchema)
async def get_blog(
    blog_id: str,
    current_user = Depends(get_current_user_dependency)
):
    """
    Get a specific blog post by ID
    """
    try:
        # Find the blog
        blog = Blog.objects(id=blog_id).first()
        
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )
        
        # If not admin and blog is not published, return 404
        if not (isinstance(current_user, dict) or 
                (hasattr(current_user, 'role') and current_user.role.value == 'admin')):
            if blog.is_published != 'published':
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Blog not found"
                )
        
        return convert_blog_to_response(blog)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving blog: {str(e)}"
        )

@router.get("/slug/{slug}", response_model=BlogResponseSchema)
async def get_blog_by_slug(slug: str):
    """
    Get a specific blog post by slug (Public access)
    """
    try:
        # Find the blog by slug
        blog = Blog.objects(slug=slug).first()
        
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )
        
        # For public access, only show published blogs
        if blog.is_published != 'published':
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )
        
        return convert_blog_to_response(blog)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving blog: {str(e)}"
        )

@router.put("/{blog_id}", response_model=BlogResponseSchema)
async def update_blog(
    blog_id: str,
    blog_data: BlogUpdateSchema,
    current_user = Depends(get_current_user_dependency)
):
    """
    Update a blog post (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not (isinstance(current_user, dict) or 
                (hasattr(current_user, 'role') and current_user.role.value == 'admin')):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update blog posts"
            )
        
        # Find the blog
        blog = Blog.objects(id=blog_id).first()
        
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )
        
        # Update fields
        update_data = blog_data.dict(exclude_unset=True)
        
        # Handle slug generation if title is updated
        if 'title' in update_data and not update_data.get('slug'):
            new_slug = generate_slug(update_data['title'])
            update_data['slug'] = ensure_unique_slug(new_slug, blog_id)
        elif 'slug' in update_data:
            update_data['slug'] = ensure_unique_slug(update_data['slug'], blog_id)
        
        # Handle content sections if provided
        if 'content' in update_data:
            from app.models.blog import ContentSection
            content_sections = []
            for section_data in update_data['content']:
                # Handle both Pydantic model objects and dictionaries
                if hasattr(section_data, 'heading'):
                    # Pydantic model object
                    heading = section_data.heading
                    description = section_data.description
                    sub_sections = section_data.sub_sections or []
                else:
                    # Dictionary object
                    heading = section_data['heading']
                    description = section_data['description']
                    sub_sections = section_data.get('sub_sections', [])
                
                section = ContentSection(
                    heading=heading,
                    description=description,
                    sub_sections=sub_sections
                )
                content_sections.append(section)
            update_data['content'] = content_sections
        
        for field, value in update_data.items():
            setattr(blog, field, value)
        
        blog.save()
        
        return convert_blog_to_response(blog)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating blog: {str(e)}"
        )

@router.patch("/{blog_id}/status", response_model=BlogResponseSchema)
async def update_blog_status(
    blog_id: str,
    status_data: BlogStatusUpdateSchema,
    current_user = Depends(get_current_user_dependency)
):
    """
    Update blog publication status (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not (isinstance(current_user, dict) or 
                (hasattr(current_user, 'role') and current_user.role.value == 'admin')):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update blog status"
            )
        
        # Find the blog
        blog = Blog.objects(id=blog_id).first()
        
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )
        
        # Update status
        blog.is_published = status_data.is_published
        
        # Set published_at if publishing for the first time
        if status_data.is_published == 'published' and not blog.published_at:
            blog.published_at = datetime.utcnow()
        
        blog.save()
        
        return convert_blog_to_response(blog)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating blog status: {str(e)}"
        )

@router.patch("/{blog_id}/tags", response_model=BlogResponseSchema)
async def update_blog_tags(
    blog_id: str,
    tags_data: BlogTagUpdateSchema,
    current_user = Depends(get_current_user_dependency)
):
    """
    Update blog tags (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not (isinstance(current_user, dict) or 
                (hasattr(current_user, 'role') and current_user.role.value == 'admin')):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update blog tags"
            )
        
        # Find the blog
        blog = Blog.objects(id=blog_id).first()
        
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )
        
        # Update tags
        blog.tags = tags_data.tags
        blog.save()
        
        return convert_blog_to_response(blog)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating blog tags: {str(e)}"
        )

@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog(
    blog_id: str,
    current_user = Depends(get_current_user_dependency)
):
    """
    Delete a blog post (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not (isinstance(current_user, dict) or 
                (hasattr(current_user, 'role') and current_user.role.value == 'admin')):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can delete blog posts"
            )
        
        # Find the blog
        blog = Blog.objects(id=blog_id).first()
        
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )
        
        # Delete the blog
        blog.delete()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting blog: {str(e)}"
        )

@router.post("/{blog_id}/content", response_model=BlogResponseSchema)
async def add_content_section(
    blog_id: str,
    section_data: ContentSectionAddSchema,
    current_user = Depends(get_current_user_dependency)
):
    """
    Add a new content section to a blog post (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not (isinstance(current_user, dict) or 
                (hasattr(current_user, 'role') and current_user.role.value == 'admin')):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can add content sections"
            )
        
        # Find the blog
        blog = Blog.objects(id=blog_id).first()
        
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )
        
        # Add new content section
        blog.add_content_section(
            heading=section_data.heading,
            description=section_data.description,
            sub_sections=section_data.sub_sections
        )
        blog.save()
        
        return convert_blog_to_response(blog)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding content section: {str(e)}"
        )

@router.put("/{blog_id}/content", response_model=BlogResponseSchema)
async def update_content_section(
    blog_id: str,
    section_data: ContentSectionUpdateSchema,
    current_user = Depends(get_current_user_dependency)
):
    """
    Update a content section in a blog post (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not (isinstance(current_user, dict) or 
                (hasattr(current_user, 'role') and current_user.role.value == 'admin')):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update content sections"
            )
        
        # Find the blog
        blog = Blog.objects(id=blog_id).first()
        
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )
        
        # Update content section
        success = blog.update_content_section(
            heading=section_data.heading,
            new_description=section_data.description,
            new_sub_sections=section_data.sub_sections
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content section not found"
            )
        
        # Update heading if provided
        if section_data.new_heading:
            section = blog.get_content_section(section_data.heading)
            if section:
                section.heading = section_data.new_heading
        
        blog.save()
        
        return convert_blog_to_response(blog)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating content section: {str(e)}"
        )

@router.delete("/{blog_id}/content/{heading}", response_model=BlogResponseSchema)
async def delete_content_section(
    blog_id: str,
    heading: str,
    current_user = Depends(get_current_user_dependency)
):
    """
    Delete a content section from a blog post (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not (isinstance(current_user, dict) or 
                (hasattr(current_user, 'role') and current_user.role.value == 'admin')):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can delete content sections"
            )
        
        # Find the blog
        blog = Blog.objects(id=blog_id).first()
        
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )
        
        # Delete content section
        success = blog.remove_content_section(heading)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content section not found"
            )
        
        blog.save()
        
        return convert_blog_to_response(blog)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting content section: {str(e)}"
        )
