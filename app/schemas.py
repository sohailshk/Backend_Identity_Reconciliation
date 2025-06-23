"""
Pydantic schemas for request/response validation in Contact Reconciliation Service.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from models import LinkPrecedence
import re


class ContactBase(BaseModel):
    """Base schema for Contact with common fields."""
    phoneNumber: Optional[str] = Field(None, description="Phone number of the contact")
    email: Optional[str] = Field(None, description="Email address of the contact")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format."""
        if v is not None and v.strip():
            # Basic email regex validation
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v.strip()):
                raise ValueError('Invalid email format')
        return v.strip() if v else None

    @field_validator('phoneNumber')
    @classmethod
    def validate_phone_number(cls, v):
        """Validate phone number format."""
        if v is not None and v.strip():
            # Basic phone validation - allows digits, spaces, +, -, (), .
            phone_pattern = r'^[\+]?[1-9][\d\s\-\(\)\.]{6,20}$'
            clean_phone = re.sub(r'[\s\-\(\)\.]+', '', v.strip())
            if not re.match(phone_pattern, v.strip()) or len(clean_phone) < 7:
                raise ValueError('Invalid phone number format')
        return v.strip() if v else None


class ContactCreate(ContactBase):
    """Schema for creating a new contact."""
    pass


class ContactUpdate(ContactBase):
    """Schema for updating an existing contact."""
    linkPrecedence: Optional[LinkPrecedence] = Field(None, description="Link precedence type")


class ContactResponse(ContactBase):
    """Schema for contact response with all fields."""
    id: int
    linkedId: Optional[int] = None
    linkPrecedence: LinkPrecedence
    createdAt: datetime
    updatedAt: datetime
    deletedAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str = Field(default="ok", description="Health status of the service")


class IdentifyRequest(ContactBase):
    """Schema for contact identification request."""
    pass


class IdentifyResponse(BaseModel):
    """Schema for contact identification response."""
    primaryContactId: int
    emails: list[str]
    phoneNumbers: list[str]
    secondaryContactIds: list[int]


class ContactReconciliationResponse(BaseModel):
    """Schema for contact reconciliation response."""
    primaryContactId: int
    emails: list[str]
    phoneNumbers: list[str]
    secondaryContactIds: list[int]


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str = Field(description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")


class ValidationErrorResponse(BaseModel):
    """Schema for validation error responses."""
    error: str = Field(description="Validation error message")
    field: Optional[str] = Field(None, description="Field that caused the error")
