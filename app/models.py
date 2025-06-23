"""
SQLAlchemy models for Contact Reconciliation Service.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone
import enum


class LinkPrecedence(str, enum.Enum):
    """Enum for link precedence types."""
    PRIMARY = "primary"
    SECONDARY = "secondary"


class Contact(Base):
    """
    Contact model for storing contact information and relationships.
    
    Attributes:
        id: Primary key identifier
        phoneNumber: Phone number (optional)
        email: Email address (optional)
        linkedId: Foreign key reference to parent contact (for secondary contacts)
        linkPrecedence: Whether this is a primary or secondary contact
        createdAt: Timestamp when the contact was created
        updatedAt: Timestamp when the contact was last updated
        deletedAt: Timestamp when the contact was soft-deleted (optional)
    """
    
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phoneNumber = Column(String, nullable=True, index=True)
    email = Column(String, nullable=True, index=True)
    linkedId = Column(Integer, ForeignKey("contacts.id"), nullable=True, index=True)
    linkPrecedence = Column(Enum(LinkPrecedence), nullable=False, index=True)
    createdAt = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updatedAt = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    deletedAt = Column(DateTime, nullable=True, index=True)

    # Relationship to parent contact (for secondary contacts)
    parent_contact = relationship("Contact", remote_side=[id], backref="linked_contacts")

    def __repr__(self):
        return f"<Contact(id={self.id}, email={self.email}, phone={self.phoneNumber}, precedence={self.linkPrecedence})>"
