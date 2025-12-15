# ======================================================================================
# tests/integration/test_listing.py
# ======================================================================================
# Purpose: Integration tests for Listing CRUD operations with ownership enforcement
# ======================================================================================

import pytest
import uuid
import logging
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.car import Car
from app.models.listing import Listing
from app.models.user import User
from tests.conftest import create_fake_user

logger = logging.getLogger(__name__)

# ======================================================================================
# Helper Functions
# ======================================================================================

def create_test_user(db_session: Session) -> User:
    """Create and return a test user in the database."""
    user_data = create_fake_user()
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_test_car(db_session: Session, user_id: uuid.UUID, **kwargs) -> Car:
    """Create and return a test car in the database."""
    car_data = {
        "year": 2020,
        "make": "Toyota",
        "model": "Camry",
        "trim": "SE",
        "user_id": user_id
    }
    car_data.update(kwargs)
    
    car = Car(**car_data)
    db_session.add(car)
    db_session.commit()
    db_session.refresh(car)
    return car


def create_test_listing(db_session: Session, car_id: uuid.UUID, user_id: uuid.UUID, **kwargs) -> Listing:
    """Create and return a test listing in the database."""
    listing_data = {
        "car_id": car_id,
        "user_id": user_id,
        "price": 25000.00,
        "mileage": 50000,
        "source": "Autotrader",
        "url": None,
        "location": None
    }
    listing_data.update(kwargs)
    
    listing = Listing(**listing_data)
    db_session.add(listing)
    db_session.commit()
    db_session.refresh(listing)
    return listing

# ======================================================================================
# Listing CRUD Tests
# ======================================================================================

def test_create_listing(db_session):
    """Test creating a listing with valid data."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id)  # type: ignore
    
    listing = Listing(
        car_id=car.id,  # type: ignore
        user_id=user.id,  # type: ignore
        price=28500.50,
        mileage=32000,
        source="Craigslist",
        url="https://example.com/listing",
        location="San Francisco, CA"
    )
    db_session.add(listing)
    db_session.commit()
    db_session.refresh(listing)
    
    assert listing.id is not None
    assert listing.car_id == car.id  # type: ignore
    assert listing.user_id == user.id  # type: ignore
    assert listing.price == 28500.50  # type: ignore
    assert listing.mileage == 32000  # type: ignore
    assert listing.source == "Craigslist"  # type: ignore
    assert listing.url == "https://example.com/listing"  # type: ignore
    assert listing.location == "San Francisco, CA"  # type: ignore
    assert listing.created_at is not None
    assert listing.updated_at is not None
    logger.info(f"Successfully created listing with ID: {listing.id}")


def test_create_listing_without_optional_fields(db_session):
    """Test creating a listing without optional fields (mileage, url, location)."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id)  # type: ignore
    
    listing = Listing(
        car_id=car.id,  # type: ignore
        user_id=user.id,  # type: ignore
        price=30000.00,
        source="Facebook Marketplace"
    )
    db_session.add(listing)
    db_session.commit()
    db_session.refresh(listing)
    
    assert listing.id is not None
    assert listing.mileage is None
    assert listing.url is None
    assert listing.location is None
    assert listing.price == 30000.00  # type: ignore
    logger.info(f"Successfully created listing without optional fields with ID: {listing.id}")


def test_read_listing_by_id(db_session):
    """Test reading a listing by its ID."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id)  # type: ignore
    listing = create_test_listing(db_session, car.id, user.id, price=22000, source="eBay Motors")  # type: ignore
    
    # Query the listing by ID
    retrieved_listing = db_session.query(Listing).filter(Listing.id == listing.id).first()
    
    assert retrieved_listing is not None
    assert retrieved_listing.id == listing.id  # type: ignore
    assert retrieved_listing.price == 22000  # type: ignore
    assert retrieved_listing.source == "eBay Motors"  # type: ignore
    logger.info(f"Successfully retrieved listing with ID: {retrieved_listing.id}")


def test_read_car_listings(db_session):
    """Test reading all listings for a specific car."""
    user = create_test_user(db_session)
    car1 = create_test_car(db_session, user.id, make="Honda", model="Civic")  # type: ignore
    car2 = create_test_car(db_session, user.id, make="Toyota", model="Corolla")  # type: ignore
    
    # Create listings for car1
    listing1 = create_test_listing(db_session, car1.id, user.id, price=20000, source="Source1")  # type: ignore
    listing2 = create_test_listing(db_session, car1.id, user.id, price=21000, source="Source2")  # type: ignore
    
    # Create listing for car2
    listing3 = create_test_listing(db_session, car2.id, user.id, price=19000, source="Source3")  # type: ignore
    
    # Query listings for car1
    car1_listings = db_session.query(Listing).filter(Listing.car_id == car1.id).all()  # type: ignore
    
    assert len(car1_listings) == 2
    assert all(l.car_id == car1.id for l in car1_listings)  # type: ignore
    prices = {float(l.price) for l in car1_listings}  # type: ignore
    assert prices == {20000.0, 21000.0}
    logger.info(f"Car1 has {len(car1_listings)} listings")


def test_update_listing(db_session):
    """Test updating a listing's fields."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id)  # type: ignore
    listing = create_test_listing(db_session, car.id, user.id, price=25000, mileage=50000)  # type: ignore
    
    original_updated_at = listing.updated_at
    
    # Update listing fields
    listing.price = 23500.00  # type: ignore
    listing.mileage = 48000  # type: ignore
    listing.location = "Los Angeles, CA"  # type: ignore
    db_session.commit()
    db_session.refresh(listing)
    
    assert listing.price == 23500.00  # type: ignore
    assert listing.mileage == 48000  # type: ignore
    assert listing.location == "Los Angeles, CA"  # type: ignore
    assert listing.updated_at > original_updated_at  # type: ignore
    logger.info(f"Successfully updated listing ID: {listing.id}")


def test_delete_listing(db_session):
    """Test deleting a listing."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id)  # type: ignore
    listing = create_test_listing(db_session, car.id, user.id)  # type: ignore
    listing_id = listing.id
    
    # Delete the listing
    db_session.delete(listing)
    db_session.commit()
    
    # Verify deletion
    deleted_listing = db_session.query(Listing).filter(Listing.id == listing_id).first()
    assert deleted_listing is None
    logger.info(f"Successfully deleted listing ID: {listing_id}")

# ======================================================================================
# Ownership Enforcement Tests
# ======================================================================================

def test_listing_ownership_verification(db_session):
    """Test that listings are correctly associated with their owners and cars."""
    user1 = create_test_user(db_session)
    user2 = create_test_user(db_session)
    
    car1 = create_test_car(db_session, user1.id, make="BMW")  # type: ignore
    car2 = create_test_car(db_session, user2.id, make="Audi")  # type: ignore
    
    listing1 = create_test_listing(db_session, car1.id, user1.id, price=35000)  # type: ignore
    listing2 = create_test_listing(db_session, car2.id, user2.id, price=40000)  # type: ignore
    
    # Verify listing1 belongs to user1 and car1
    assert listing1.user_id == user1.id  # type: ignore
    assert listing1.car_id == car1.id  # type: ignore
    assert listing1 not in user2.listings  # type: ignore
    
    # Verify listing2 belongs to user2 and car2
    assert listing2.user_id == user2.id  # type: ignore
    assert listing2.car_id == car2.id  # type: ignore
    assert listing2 not in user1.listings  # type: ignore
    
    logger.info("Listing ownership correctly enforced")


def test_user_deletion_cascades_to_listings(db_session):
    """Test that deleting a user also deletes their listings (cascade delete)."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id)  # type: ignore
    listing1 = create_test_listing(db_session, car.id, user.id, price=20000)  # type: ignore
    listing2 = create_test_listing(db_session, car.id, user.id, price=21000)  # type: ignore
    
    listing1_id = listing1.id
    listing2_id = listing2.id
    
    # Delete the user
    db_session.delete(user)
    db_session.commit()
    
    # Verify listings are also deleted
    assert db_session.query(Listing).filter(Listing.id == listing1_id).first() is None
    assert db_session.query(Listing).filter(Listing.id == listing2_id).first() is None
    logger.info("User deletion successfully cascaded to listings")


def test_car_deletion_cascades_to_listings(db_session):
    """Test that deleting a car also deletes its listings (cascade delete)."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id)  # type: ignore
    listing1 = create_test_listing(db_session, car.id, user.id, price=20000)  # type: ignore
    listing2 = create_test_listing(db_session, car.id, user.id, price=21000)  # type: ignore
    
    listing1_id = listing1.id
    listing2_id = listing2.id
    
    # Delete the car
    db_session.delete(car)
    db_session.commit()
    
    # Verify listings are also deleted
    assert db_session.query(Listing).filter(Listing.id == listing1_id).first() is None
    assert db_session.query(Listing).filter(Listing.id == listing2_id).first() is None
    logger.info("Car deletion successfully cascaded to listings")


def test_different_users_same_car_model_different_listings(db_session):
    """Test that different users can have listings for similar cars."""
    user1 = create_test_user(db_session)
    user2 = create_test_user(db_session)
    
    # Both users have a 2020 Honda Civic
    car1 = create_test_car(db_session, user1.id, year=2020, make="Honda", model="Civic")  # type: ignore
    car2 = create_test_car(db_session, user2.id, year=2020, make="Honda", model="Civic")  # type: ignore
    
    # Create listings for each car
    listing1 = create_test_listing(db_session, car1.id, user1.id, price=18000, source="User1 Source")  # type: ignore
    listing2 = create_test_listing(db_session, car2.id, user2.id, price=19000, source="User2 Source")  # type: ignore
    
    assert listing1.id != listing2.id  # type: ignore
    assert listing1.user_id != listing2.user_id  # type: ignore
    assert listing1.car_id != listing2.car_id  # type: ignore
    assert listing1.price != listing2.price  # type: ignore
    logger.info("Different users can have listings for similar cars")

# ======================================================================================
# Relationship Tests
# ======================================================================================

def test_listing_car_relationship(db_session):
    """Test the relationship between Listing and Car."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id, make="Mazda", model="CX-5")  # type: ignore
    listing1 = create_test_listing(db_session, car.id, user.id, price=27000)  # type: ignore
    listing2 = create_test_listing(db_session, car.id, user.id, price=28000)  # type: ignore
    
    # Access listings through car relationship
    db_session.refresh(car)
    assert len(car.listings) == 2  # type: ignore
    assert listing1 in car.listings  # type: ignore
    assert listing2 in car.listings  # type: ignore
    
    # Access car through listing relationship
    assert listing1.car == car  # type: ignore
    assert listing2.car == car  # type: ignore
    logger.info("Listing-Car bidirectional relationship working correctly")


def test_listing_user_relationship(db_session):
    """Test the relationship between Listing and User."""
    user = create_test_user(db_session)
    car1 = create_test_car(db_session, user.id, make="Ford", model="Explorer")  # type: ignore
    car2 = create_test_car(db_session, user.id, make="Chevrolet", model="Tahoe")  # type: ignore
    
    listing1 = create_test_listing(db_session, car1.id, user.id, price=35000)  # type: ignore
    listing2 = create_test_listing(db_session, car2.id, user.id, price=38000)  # type: ignore
    
    # Access listings through user relationship
    db_session.refresh(user)
    assert len(user.listings) >= 2  # type: ignore
    assert listing1 in user.listings  # type: ignore
    assert listing2 in user.listings  # type: ignore
    
    # Access user through listing relationship
    assert listing1.user == user  # type: ignore
    assert listing2.user == user  # type: ignore
    logger.info("Listing-User bidirectional relationship working correctly")


def test_query_listings_with_joins(db_session):
    """Test querying listings with car and user information via joins."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id, make="Tesla", model="Model 3")  # type: ignore
    listing = create_test_listing(db_session, car.id, user.id, price=45000)  # type: ignore
    
    # Query with explicit joins
    result = (
        db_session.query(Listing, Car, User)
        .select_from(Listing)
        .join(Car, Listing.car_id == Car.id)  # type: ignore
        .join(User, Listing.user_id == User.id)  # type: ignore
        .filter(Listing.id == listing.id)  # type: ignore
        .first()
    )
    
    assert result is not None
    queried_listing, queried_car, queried_user = result
    assert queried_listing.id == listing.id  # type: ignore
    assert queried_car.id == car.id  # type: ignore
    assert queried_user.id == user.id  # type: ignore
    logger.info("Listing-Car-User join query successful")

# ======================================================================================
# Price and Mileage Tests
# ======================================================================================

def test_listing_price_precision(db_session):
    """Test that listing prices maintain proper decimal precision."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id)  # type: ignore
    
    listing = create_test_listing(
        db_session, 
        car.id,  # type: ignore
        user.id,  # type: ignore
        price=24999.99
    )
    
    assert listing.price == 24999.99  # type: ignore
    logger.info("Price precision maintained correctly")


def test_listing_with_zero_mileage(db_session):
    """Test creating a listing with zero mileage (new car)."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id)  # type: ignore
    
    listing = create_test_listing(
        db_session, 
        car.id,  # type: ignore
        user.id,  # type: ignore
        mileage=0,
        price=35000
    )
    
    assert listing.mileage == 0  # type: ignore
    logger.info("Zero mileage listing created successfully")


def test_multiple_listings_price_range(db_session):
    """Test creating multiple listings with various prices."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id)  # type: ignore
    
    prices = [18000, 19500, 20000, 22500, 25000]
    listings = []
    
    for price in prices:
        listing = create_test_listing(
            db_session, 
            car.id,  # type: ignore
            user.id,  # type: ignore
            price=price,
            source=f"Source_{price}"
        )
        listings.append(listing)
    
    assert len(listings) == 5
    retrieved_prices = [float(l.price) for l in listings]  # type: ignore
    assert sorted(retrieved_prices) == sorted(prices)
    logger.info(f"Created {len(listings)} listings with various prices")
