"""
Test module for the contact identification and reconciliation logic.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import the app components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app, get_db
from database import Base
from models import Contact, LinkPrecedence
from schemas import IdentifyRequest, IdentifyResponse

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(setup_database):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def db_session(setup_database):
    """Create database session for direct database access."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


class TestContactIdentification:
    """Test cases for contact identification and reconciliation."""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    def test_new_contact_creation(self, client, db_session):
        """Test creating a completely new contact."""
        request_data = {
            "email": "new@example.com",
            "phoneNumber": "+1234567890"
        }
        
        response = client.post("/identify", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["primaryContactId"] == 1
        assert data["emails"] == ["new@example.com"]
        assert data["phoneNumbers"] == ["+1234567890"]
        assert data["secondaryContactIds"] == []
        
        # Verify database state
        contact = db_session.query(Contact).filter(Contact.id == 1).first()
        assert contact is not None
        assert contact.email == "new@example.com"
        assert contact.phoneNumber == "+1234567890"
        assert contact.linkPrecedence == LinkPrecedence.PRIMARY
        assert contact.linkedId is None
    
    def test_simple_secondary_creation(self, client, db_session):
        """Test creating a secondary contact linked to existing primary."""
        # First, create a primary contact
        primary_data = {
            "email": "primary@example.com",
            "phoneNumber": "+1111111111"
        }
        client.post("/identify", json=primary_data)
        
        # Then create a secondary with same email, different phone
        secondary_data = {
            "email": "primary@example.com",
            "phoneNumber": "+2222222222"
        }
        
        response = client.post("/identify", json=secondary_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["primaryContactId"] == 1
        assert set(data["emails"]) == {"primary@example.com"}
        assert set(data["phoneNumbers"]) == {"+1111111111", "+2222222222"}
        assert data["secondaryContactIds"] == [2]
        
        # Verify database state
        primary = db_session.query(Contact).filter(Contact.id == 1).first()
        secondary = db_session.query(Contact).filter(Contact.id == 2).first()
        
        assert primary.linkPrecedence == LinkPrecedence.PRIMARY
        assert secondary.linkPrecedence == LinkPrecedence.SECONDARY
        assert secondary.linkedId == 1
    
    def test_merging_two_primaries(self, client, db_session):
        """Test merging two separate primary contacts through overlapping secondary."""
        # Create first primary
        primary1_data = {"email": "primary1@example.com"}
        client.post("/identify", json=primary1_data)
        
        # Create second primary  
        primary2_data = {"phoneNumber": "+9999999999"}
        client.post("/identify", json=primary2_data)
        
        # Now create a contact that links both (same email as primary1, same phone as primary2)
        linking_data = {
            "email": "primary1@example.com",
            "phoneNumber": "+9999999999"
        }
        
        response = client.post("/identify", json=linking_data)
        assert response.status_code == 200
        
        data = response.json()
        # Should merge under the earliest primary (ID 1)
        assert data["primaryContactId"] == 1
        assert set(data["emails"]) == {"primary1@example.com"}
        assert set(data["phoneNumbers"]) == {"+9999999999"}
        assert set(data["secondaryContactIds"]) == {2, 3}
        
        # Verify database state - primary2 should be demoted to secondary
        primary1 = db_session.query(Contact).filter(Contact.id == 1).first()
        former_primary2 = db_session.query(Contact).filter(Contact.id == 2).first() 
        linking_contact = db_session.query(Contact).filter(Contact.id == 3).first()
        
        assert primary1.linkPrecedence == LinkPrecedence.PRIMARY
        assert former_primary2.linkPrecedence == LinkPrecedence.SECONDARY
        assert former_primary2.linkedId == 1
        assert linking_contact.linkPrecedence == LinkPrecedence.SECONDARY
        assert linking_contact.linkedId == 1
    
    def test_email_only_identification(self, client):
        """Test identification with email only."""
        # Create contact with email and phone
        full_contact_data = {
            "email": "test@example.com",
            "phoneNumber": "+1234567890"
        }
        client.post("/identify", json=full_contact_data)
        
        # Identify with email only
        email_only_data = {"email": "test@example.com"}
        response = client.post("/identify", json=email_only_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["primaryContactId"] == 1
        assert "test@example.com" in data["emails"]
        assert "+1234567890" in data["phoneNumbers"]
    
    def test_phone_only_identification(self, client):
        """Test identification with phone number only."""
        # Create contact with email and phone
        full_contact_data = {
            "email": "test@example.com", 
            "phoneNumber": "+1234567890"
        }
        client.post("/identify", json=full_contact_data)
        
        # Identify with phone only
        phone_only_data = {"phoneNumber": "+1234567890"}
        response = client.post("/identify", json=phone_only_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["primaryContactId"] == 1
        assert "test@example.com" in data["emails"]
        assert "+1234567890" in data["phoneNumbers"]
    
    def test_invalid_input_no_email_or_phone(self, client):
        """Test error handling for missing both email and phone."""
        response = client.post("/identify", json={})
        assert response.status_code == 400
        assert "At least one of email or phoneNumber must be provided" in response.json()["detail"]
    
    def test_invalid_email_format(self, client):
        """Test error handling for invalid email format."""
        invalid_email_data = {
            "email": "not-an-email",
            "phoneNumber": "+1234567890"
        }
        response = client.post("/identify", json=invalid_email_data)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")
        assert response.status_code == 422  # Pydantic validation error
    
    def test_invalid_phone_format(self, client):
        """Test error handling for invalid phone format."""
        invalid_phone_data = {
            "email": "test@example.com",
            "phoneNumber": "abc"
        }
        response = client.post("/identify", json=invalid_phone_data)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")
        assert response.status_code == 422  # Pydantic validation error
    
    def test_exact_match_no_duplicate_creation(self, client, db_session):
        """Test that exact matches don't create duplicate contacts."""
        contact_data = {
            "email": "duplicate@example.com",
            "phoneNumber": "+1234567890"
        }
        
        # Create contact first time
        response1 = client.post("/identify", json=contact_data)
        assert response1.status_code == 200
        
        # Try to create exact same contact
        response2 = client.post("/identify", json=contact_data)
        assert response2.status_code == 200
        
        # Should return same primary ID and not create duplicate
        data1 = response1.json()
        data2 = response2.json()
        assert data1["primaryContactId"] == data2["primaryContactId"]
        
        # Should only have one contact in database
        contact_count = db_session.query(Contact).count()
        assert contact_count == 1
    
    def test_complex_merging_scenario(self, client, db_session):
        """Test complex scenario with multiple contacts and merging."""
        # Create first primary with email
        client.post("/identify", json={"email": "user1@example.com"})
        
        # Create second primary with phone
        client.post("/identify", json={"phoneNumber": "+1111111111"})
        
        # Create third primary with different email
        client.post("/identify", json={"email": "user2@example.com"})
        
        # Link first and second primaries
        client.post("/identify", json={
            "email": "user1@example.com",
            "phoneNumber": "+1111111111"
        })
        
        # Link the merged group with third primary
        response = client.post("/identify", json={
            "email": "user2@example.com", 
            "phoneNumber": "+1111111111"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # All should be merged under earliest primary (ID 1)
        assert data["primaryContactId"] == 1
        assert set(data["emails"]) == {"user1@example.com", "user2@example.com"}
        assert "+1111111111" in data["phoneNumbers"]
        
        # Verify all former primaries are now secondaries except the winner
        primary = db_session.query(Contact).filter(
            Contact.id == 1,
            Contact.linkPrecedence == LinkPrecedence.PRIMARY
        ).first()
        assert primary is not None
        
        secondaries = db_session.query(Contact).filter(
            Contact.linkPrecedence == LinkPrecedence.SECONDARY,
            Contact.linkedId == 1
        ).all()
        assert len(secondaries) >= 2  # At least the demoted primaries
