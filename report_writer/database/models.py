"""
Database models for Interactive Analytics Report Writer

This module defines the PostgreSQL database schema for multi-tenant document management,
real-time collaboration, and AI-powered report generation.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, JSON, 
    ForeignKey, UniqueConstraint, Index, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class UserRole(str, Enum):
    """User roles within an organization"""
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class DocumentPermission(str, Enum):
    """Document-level permissions"""
    OWNER = "owner"
    EDITOR = "editor"
    COMMENTER = "commenter" 
    VIEWER = "viewer"


class ReportTemplateCategory(str, Enum):
    """Categories for business report templates"""
    FINANCIAL = "financial"
    MARKETING = "marketing"
    OPERATIONAL = "operational"
    SALES = "sales"
    STRATEGIC = "strategic"
    COMPLIANCE = "compliance"


class SectionType(str, Enum):
    """Types of sections in business reports"""
    TITLE = "title"
    EXECUTIVE_SUMMARY = "executive_summary"
    DATA_ANALYSIS = "data_analysis"
    CHART = "chart"
    INSIGHTS = "insights"
    RECOMMENDATIONS = "recommendations"
    CONCLUSION = "conclusion"
    APPENDIX = "appendix"


# Users and Organizations (Multi-tenant Architecture)

class User(Base):
    """User accounts with Google OAuth integration"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    google_id = Column(String(100), unique=True, index=True)
    name = Column(String(255), nullable=False)
    avatar_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Preferences and settings
    preferences = Column(JSON, default=dict)  # AI settings, UI preferences, etc.
    
    # Relationships
    memberships = relationship("UserMembership", back_populates="user", cascade="all, delete-orphan")
    created_documents = relationship("Document", back_populates="creator")
    ai_generations = relationship("AIGeneration", back_populates="user")


class Organization(Base):
    """Organizations for multi-tenant architecture"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)  # URL-friendly name
    plan_type = Column(String(50), default="free")  # free, pro, enterprise
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Organization settings
    settings = Column(JSON, default=dict)  # BigQuery connections, branding, etc.
    
    # Relationships
    members = relationship("UserMembership", back_populates="organization", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="organization")
    custom_templates = relationship("ReportTemplate", back_populates="organization")


class UserMembership(Base):
    """User memberships in organizations with roles"""
    __tablename__ = "user_memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.VIEWER)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Additional permissions
    permissions = Column(JSON, default=dict)  # Custom permissions beyond role
    
    # Relationships
    user = relationship("User", back_populates="memberships")
    organization = relationship("Organization", back_populates="members")
    
    # Ensure unique user-organization pairs
    __table_args__ = (UniqueConstraint('user_id', 'organization_id'),)


# Document Management

class Document(Base):
    """Business reports and documents"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("report_templates.id"))
    
    # Document metadata
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Document content (stored as structured JSON)
    content = Column(JSON, nullable=False, default=dict)  # Document structure and content
    
    # Ownership and permissions
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Status and metadata
    is_archived = Column(Boolean, default=False)
    version_number = Column(Integer, default=1)
    
    # Relationships
    organization = relationship("Organization", back_populates="documents")
    template = relationship("ReportTemplate", back_populates="documents")
    creator = relationship("User", back_populates="created_documents")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    collaborators = relationship("DocumentCollaborator", back_populates="document", cascade="all, delete-orphan")
    ai_generations = relationship("AIGeneration", back_populates="document")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_org_updated', 'organization_id', 'updated_at'),
        Index('idx_creator_created', 'created_by', 'created_at'),
    )


class DocumentVersion(Base):
    """Version history for documents"""
    __tablename__ = "document_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    
    # Version content
    content = Column(JSON, nullable=False)  # Full document content at this version
    title = Column(String(500), nullable=False)
    
    # Version metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    change_summary = Column(Text)  # Description of changes made
    
    # Relationships
    document = relationship("Document", back_populates="versions")
    created_by_user = relationship("User")
    
    # Ensure unique version numbers per document
    __table_args__ = (UniqueConstraint('document_id', 'version_number'),)


class DocumentCollaborator(Base):
    """Document collaborators and their permissions"""
    __tablename__ = "document_collaborators"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission = Column(SQLEnum(DocumentPermission), nullable=False)
    
    # Collaboration metadata
    added_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed = Column(DateTime(timezone=True))
    
    # Relationships
    document = relationship("Document", back_populates="collaborators")
    user = relationship("User", foreign_keys=[user_id])
    added_by_user = relationship("User", foreign_keys=[added_by])
    
    # Ensure unique user-document pairs
    __table_args__ = (UniqueConstraint('document_id', 'user_id'),)


# Report Templates

class ReportTemplate(Base):
    """Business report templates"""
    __tablename__ = "report_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))  # NULL for global templates
    
    # Template metadata
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(SQLEnum(ReportTemplateCategory), nullable=False)
    
    # Template structure
    structure = Column(JSON, nullable=False)  # Template sections and layout
    
    # Template settings
    is_public = Column(Boolean, default=False)  # Available to all organizations
    is_featured = Column(Boolean, default=False)  # Featured in template marketplace
    
    # Ownership and timestamps
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    
    # Relationships
    organization = relationship("Organization", back_populates="custom_templates")
    creator = relationship("User")
    documents = relationship("Document", back_populates="template")
    sections = relationship("TemplateSection", back_populates="template", cascade="all, delete-orphan")


class TemplateSection(Base):
    """Sections within report templates"""
    __tablename__ = "template_sections"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("report_templates.id"), nullable=False)
    
    # Section properties
    section_type = Column(SQLEnum(SectionType), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    order = Column(Integer, nullable=False)  # Position in template
    
    # Section configuration
    config = Column(JSON, default=dict)  # Section-specific settings
    is_required = Column(Boolean, default=False)
    is_ai_generated = Column(Boolean, default=True)  # Can be auto-generated by AI
    
    # Relationships
    template = relationship("ReportTemplate", back_populates="sections")
    
    # Ensure unique ordering within template
    __table_args__ = (UniqueConstraint('template_id', 'order'),)


# AI Generation History

class AIGeneration(Base):
    """History of AI-generated content"""
    __tablename__ = "ai_generations"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Generation details
    section_id = Column(String(100))  # Which section was generated
    prompt = Column(Text, nullable=False)  # User's input prompt
    response = Column(Text, nullable=False)  # AI's generated content
    
    # AI model information
    model_used = Column(String(100), nullable=False)  # e.g., "gemini-2.0-flash-001"
    agent_used = Column(String(100))  # Which agent generated this content
    
    # Generation metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    generation_time_ms = Column(Integer)  # How long generation took
    was_accepted = Column(Boolean, default=True)  # Did user accept the generation
    
    # Quality and feedback
    user_rating = Column(Integer)  # 1-5 star rating from user
    user_feedback = Column(Text)  # User's feedback on the generation
    
    # Relationships
    document = relationship("Document", back_populates="ai_generations")
    user = relationship("User", back_populates="ai_generations")
    
    # Indexes for analytics
    __table_args__ = (
        Index('idx_document_created', 'document_id', 'created_at'),
        Index('idx_model_performance', 'model_used', 'generation_time_ms'),
    ) 