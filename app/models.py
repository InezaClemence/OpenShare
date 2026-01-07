from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    institution = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'author', 'reviewer', 'admin'


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="draft")  # 'draft', 'in_review', 'approved'
    license = Column(String, default="CC BY")
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    created_by = relationship("User")

    versions = relationship(
        "ResourceVersion",
        back_populates="resource",
        order_by="ResourceVersion.version_number",
        cascade="all, delete-orphan",
    )

    invites = relationship(
        "CollaborationInvite",
        back_populates="resource",
        order_by="CollaborationInvite.created_at",
        cascade="all, delete-orphan",
    )


class ResourceVersion(Base):
    __tablename__ = "resource_versions"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"))
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    resource = relationship("Resource", back_populates="versions")
    created_by = relationship("User")


class CollaborationInvite(Base):
    __tablename__ = "collaboration_invites"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    collaborator_email = Column(String, nullable=False)
    message = Column(Text, default="")
    status = Column(String, default="pending")  # pending / accepted / declined
    created_at = Column(DateTime, default=datetime.utcnow)

    resource = relationship("Resource", back_populates="invites")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    decision = Column(String)  # 'approved', 'changes_requested'
    comments = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class LtiLink(Base):
    __tablename__ = "lti_links"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), unique=True)
    url = Column(String, nullable=False)
