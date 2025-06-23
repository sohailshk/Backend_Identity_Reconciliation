"""
FastAPI application for Contact Reconciliation Service.

This service provides endpoints for managing contacts and their relationships,
including the ability to identify and link related contacts based on shared
email addresses or phone numbers.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List

# Import local modules
from database import create_tables, get_db
from fastapi import Depends, FastAPI, HTTPException, status
from models import Contact, LinkPrecedence
from schemas import (
    ContactCreate,
    ContactResponse,
    ContactUpdate,
    ErrorResponse,
    HealthResponse,
    IdentifyRequest,
    IdentifyResponse,
)
from sqlalchemy import or_
from sqlalchemy.orm import Session


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    create_tables()
    yield
    # Shutdown (cleanup if needed)


# Create FastAPI application instance
app = FastAPI(
    title="Contact Reconciliation Service",
    description="A service for managing contacts and identifying relationships between them",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify service is running.

    Returns:
        dict: Status message indicating service health
    """
    return {"status": "ok"}


@app.get("/")
async def root():
    """
    Root endpoint with basic service information.

    Returns:
        dict: Welcome message and service description
    """
    return {
        "message": "Contact Reconciliation Service",
        "description": "API for managing contacts and their relationships",
        "version": "1.0.0",
    }


@app.post(
    "/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED
)
async def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    """
    Create a new contact.

    Args:
        contact: Contact data to create
        db: Database session

    Returns:
        ContactResponse: Created contact information

    Raises:
        HTTPException: If contact creation fails
    """
    # Validate that at least one contact method is provided
    if not contact.email and not contact.phoneNumber:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of email or phoneNumber must be provided",
        )

    # For now, create as primary contact - reconciliation logic would go here
    db_contact = Contact(
        email=contact.email,
        phoneNumber=contact.phoneNumber,
        linkPrecedence=LinkPrecedence.PRIMARY,
    )

    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)

    return db_contact


@app.get("/contacts", response_model=List[ContactResponse])
async def get_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of contacts.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List[ContactResponse]: List of contacts
    """
    contacts = (
        db.query(Contact)
        .filter(Contact.deletedAt.is_(None))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return contacts


@app.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific contact by ID.

    Args:
        contact_id: ID of the contact to retrieve
        db: Database session

    Returns:
        ContactResponse: Contact information

    Raises:
        HTTPException: If contact is not found
    """
    contact = (
        db.query(Contact)
        .filter(Contact.id == contact_id, Contact.deletedAt.is_(None))
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )

    return contact


@app.put("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int, contact_update: ContactUpdate, db: Session = Depends(get_db)
):
    """
    Update an existing contact.

    Args:
        contact_id: ID of the contact to update
        contact_update: Updated contact data
        db: Database session

    Returns:
        ContactResponse: Updated contact information

    Raises:
        HTTPException: If contact is not found
    """
    contact = (
        db.query(Contact)
        .filter(Contact.id == contact_id, Contact.deletedAt.is_(None))
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )

    # Update fields if provided
    update_data = contact_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)

    return contact


@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """
    Soft delete a contact (sets deletedAt timestamp).

    Args:
        contact_id: ID of the contact to delete
        db: Database session

    Raises:
        HTTPException: If contact is not found
    """
    contact = (
        db.query(Contact)
        .filter(Contact.id == contact_id, Contact.deletedAt.is_(None))
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )

    contact.deletedAt = datetime.now(timezone.utc)
    db.commit()


def _find_matching_contacts(
    email: str = None, phoneNumber: str = None, db: Session = None
) -> list[Contact]:
    """
    Find all contacts that match the given email or phone number.

    Args:
        email: Email address to search for
        phoneNumber: Phone number to search for
        db: Database session

    Returns:
        List of matching Contact objects
    """
    if email and phoneNumber:
        return (
            db.query(Contact)
            .filter(
                Contact.deletedAt.is_(None),
                or_(Contact.email == email, Contact.phoneNumber == phoneNumber),
            )
            .all()
        )
    elif email:
        return (
            db.query(Contact)
            .filter(Contact.deletedAt.is_(None), Contact.email == email)
            .all()
        )
    elif phoneNumber:
        return (
            db.query(Contact)
            .filter(Contact.deletedAt.is_(None), Contact.phoneNumber == phoneNumber)
            .all()
        )
    return []


def _get_all_related_contacts(
    matching_contacts: list[Contact], db: Session
) -> set[Contact]:
    """
    Get all contacts related to the matching contacts, including primaries and their secondaries.

    Args:
        matching_contacts: List of initially matching contacts
        db: Database session

    Returns:
        Set of all related contacts
    """
    all_related_contacts = set(matching_contacts)

    # Include contacts linked to any of the matching contacts
    for contact in matching_contacts:
        if contact.linkPrecedence == LinkPrecedence.SECONDARY and contact.linkedId:
            # Get the primary contact this secondary is linked to
            primary = (
                db.query(Contact)
                .filter(Contact.id == contact.linkedId, Contact.deletedAt.is_(None))
                .first()
            )
            if primary:
                all_related_contacts.add(primary)
                # Get all other secondaries linked to this primary
                other_secondaries = (
                    db.query(Contact)
                    .filter(Contact.linkedId == primary.id, Contact.deletedAt.is_(None))
                    .all()
                )
                all_related_contacts.update(other_secondaries)

        # Get all contacts linked to this contact (if it's primary)
        if contact.linkPrecedence == LinkPrecedence.PRIMARY:
            linked_contacts = (
                db.query(Contact)
                .filter(Contact.linkedId == contact.id, Contact.deletedAt.is_(None))
                .all()
            )
            all_related_contacts.update(linked_contacts)

    return all_related_contacts


def _find_primary_contacts(all_contacts: set[Contact]) -> list[Contact]:
    """
    Find all primary contacts in the given set.

    Args:
        all_contacts: Set of contacts to search through

    Returns:
        List of primary contacts
    """
    return [c for c in all_contacts if c.linkPrecedence == LinkPrecedence.PRIMARY]


def _merge_contact_groups(primary_contacts: list[Contact], db: Session) -> Contact:
    """
    Merge multiple primary contact groups under the earliest created primary.

    Args:
        primary_contacts: List of primary contacts to merge
        db: Database session

    Returns:
        The winning primary contact
    """
    if len(primary_contacts) <= 1:
        return primary_contacts[0] if primary_contacts else None

    # Find the earliest created contact to be the winning primary
    winning_primary = min(primary_contacts, key=lambda c: c.createdAt)
    losing_primaries = [p for p in primary_contacts if p.id != winning_primary.id]

    # Merge all losing primaries under the winning primary
    for losing_primary in losing_primaries:
        # Find all secondaries linked to the losing primary
        losing_secondaries = (
            db.query(Contact)
            .filter(Contact.linkedId == losing_primary.id, Contact.deletedAt.is_(None))
            .all()
        )
        # Relink all secondaries to the winning primary
        for secondary in losing_secondaries:
            secondary.linkedId = winning_primary.id
            secondary.updatedAt = datetime.now(timezone.utc)

        # Demote the losing primary to secondary
        losing_primary.linkPrecedence = LinkPrecedence.SECONDARY
        losing_primary.linkedId = winning_primary.id
        losing_primary.updatedAt = datetime.now(timezone.utc)

    return winning_primary


def _create_secondary_contact(
    email: str, phoneNumber: str, primary_contact: Contact, db: Session
) -> Contact:
    """
    Create a new secondary contact linked to the given primary.

    Args:
        email: Email for the new contact
        phoneNumber: Phone number for the new contact
        primary_contact: Primary contact to link to
        db: Database session

    Returns:
        The created secondary contact
    """
    new_secondary = Contact(
        email=email,
        phoneNumber=phoneNumber,
        linkPrecedence=LinkPrecedence.SECONDARY,
        linkedId=primary_contact.id,
    )
    db.add(new_secondary)
    return new_secondary


def _collect_consolidated_info(
    all_contacts: set[Contact], primary_contact: Contact
) -> tuple[list[str], list[str], list[int]]:
    """
    Collect all emails, phone numbers, and secondary contact IDs from the contact group.

    Args:
        all_contacts: Set of all related contacts
        primary_contact: The primary contact

    Returns:
        Tuple of (emails, phone_numbers, secondary_contact_ids)
    """
    all_emails = set()
    all_phone_numbers = set()
    secondary_contact_ids = []

    for contact in all_contacts:
        if contact.email:
            all_emails.add(contact.email)
        if contact.phoneNumber:
            all_phone_numbers.add(contact.phoneNumber)
        if contact.id != primary_contact.id:
            secondary_contact_ids.append(contact.id)

    return (
        sorted(list(all_emails)),
        sorted(list(all_phone_numbers)),
        sorted(secondary_contact_ids),
    )


def identify_contact(
    email: str = None, phoneNumber: str = None, db: Session = None
) -> IdentifyResponse:
    """
    Core logic for contact identification and reconciliation with enhanced merging.

    This function handles complex contact reconciliation including:
    - Finding matching contacts
    - Merging overlapping contact groups
    - Creating new contacts when needed
    - Ensuring proper primary/secondary relationships

    Args:
        email: Email address to search for
        phoneNumber: Phone number to search for
        db: Database session

    Returns:
        IdentifyResponse: Consolidated contact information
    """
    try:
        # Step 1: Find all existing contacts that match the email or phone number
        matching_contacts = _find_matching_contacts(email, phoneNumber, db)

        # Step 2: If no matches found, create new primary contact
        if not matching_contacts:
            new_contact = Contact(
                email=email,
                phoneNumber=phoneNumber,
                linkPrecedence=LinkPrecedence.PRIMARY,
                linkedId=None,
            )
            db.add(new_contact)
            db.commit()
            db.refresh(new_contact)

            return IdentifyResponse(
                primaryContactId=new_contact.id,
                emails=[email] if email else [],
                phoneNumbers=[phoneNumber] if phoneNumber else [],
                secondaryContactIds=[],
            )

        # Step 3: Get all related contacts (including linked primaries and secondaries)
        all_related_contacts = _get_all_related_contacts(matching_contacts, db)

        # Step 4: Find all primary contacts in the related set
        primary_contacts = _find_primary_contacts(all_related_contacts)

        # Step 5: Merge overlapping contact groups if multiple primaries exist
        winning_primary = _merge_contact_groups(primary_contacts, db)

        # Step 6: Check if we need to create a new secondary contact
        exact_match_exists = any(
            c.email == email and c.phoneNumber == phoneNumber
            for c in all_related_contacts
        )

        if not exact_match_exists:
            new_secondary = _create_secondary_contact(
                email, phoneNumber, winning_primary, db
            )
            all_related_contacts.add(new_secondary)
        # Step 7: Ensure all non-primary contacts are properly linked
        for contact in all_related_contacts:
            if contact.id != winning_primary.id:
                if (
                    contact.linkPrecedence != LinkPrecedence.SECONDARY
                    or contact.linkedId != winning_primary.id
                ):
                    contact.linkPrecedence = LinkPrecedence.SECONDARY
                    contact.linkedId = winning_primary.id
                    contact.updatedAt = datetime.now(timezone.utc)

        # Ensure winning primary is properly marked
        if winning_primary.linkPrecedence != LinkPrecedence.PRIMARY:
            winning_primary.linkPrecedence = LinkPrecedence.PRIMARY
            winning_primary.linkedId = None
            winning_primary.updatedAt = datetime.now(timezone.utc)

        # Commit all changes atomically
        db.commit()

        # Step 8: Collect consolidated information
        emails, phone_numbers, secondary_contact_ids = _collect_consolidated_info(
            all_related_contacts, winning_primary
        )

        return IdentifyResponse(
            primaryContactId=winning_primary.id,
            emails=emails,
            phoneNumbers=phone_numbers,
            secondaryContactIds=secondary_contact_ids,
        )

    except Exception as e:
        db.rollback()
        raise e


@app.post("/identify", response_model=IdentifyResponse)
async def identify_endpoint(request: IdentifyRequest, db: Session = Depends(get_db)):
    """
    Identify and reconcile contacts based on email and/or phone number.

    This endpoint implements advanced contact reconciliation logic including:
    1. Searches for existing contacts with matching email or phone
    2. If no matches, creates a new primary contact
    3. If matches exist, determines the primary contact and links others as secondary
    4. Merges overlapping contact groups under the earliest primary
    5. Returns consolidated contact information

    Args:
        request: IdentifyRequest containing email and/or phoneNumber
        db: Database session

    Returns:
        IdentifyResponse: Consolidated contact information

    Raises:
        HTTPException: If validation fails or server error occurs
    """
    # Validate that at least one contact method is provided
    if not request.email and not request.phoneNumber:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of email or phoneNumber must be provided",
        )

    try:
        # Call the core identification logic
        result = identify_contact(
            email=request.email, phoneNumber=request.phoneNumber, db=db
        )
        return result

    except ValueError as e:
        # Handle validation errors (from Pydantic validators)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        # Hide implementation details for security
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service temporarily overloaded",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
