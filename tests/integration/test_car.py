# ======================================================================================
# tests/integration/test_car.py
# ======================================================================================
# Purpose: Integration tests for Car CRUD operations with ownership enforcement
# ======================================================================================

import pytest
import uuid
import logging
from sqlalchemy.orm import Session

from app.models.car import Car
from app.models.user import User
from tests.conftest import create_fake_user, managed_db_session

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
        "vin": None,
        "user_id": user_id
    }
    car_data.update(kwargs)
    
    car = Car(**car_data)
    db_session.add(car)
    db_session.commit()
    db_session.refresh(car)
    return car

# ======================================================================================
# Car CRUD Tests
# ======================================================================================

def test_create_car(db_session):
    """Test creating a car with valid data."""
    user = create_test_user(db_session)
    
    car = Car(
        year=2022,
        make="Honda",
        model="Accord",
        trim="Sport",
        vin="5HGBH41JXMN100001",  # Unique VIN for this test
        user_id=user.id  # type: ignore
    )
    db_session.add(car)
    db_session.commit()
    db_session.refresh(car)
    
    assert car.id is not None
    assert car.year == 2022  # type: ignore
    assert car.make == "Honda"  # type: ignore
    assert car.model == "Accord"  # type: ignore
    assert car.trim == "Sport"  # type: ignore
    assert car.vin == "5HGBH41JXMN100001"  # type: ignore
    assert car.user_id == user.id  # type: ignore
    assert car.created_at is not None
    assert car.updated_at is not None
    logger.info(f"Successfully created car with ID: {car.id}")


def test_create_car_without_optional_fields(db_session):
    """Test creating a car without optional fields (VIN and trim)."""
    user = create_test_user(db_session)
    
    car = Car(
        year=2019,
        make="Ford",
        model="F-150",
        user_id=user.id
    )
    db_session.add(car)
    db_session.commit()
    db_session.refresh(car)
    
    assert car.id is not None
    assert car.vin is None
    assert car.trim is None
    assert car.make == "Ford"
    logger.info(f"Successfully created car without VIN/trim with ID: {car.id}")


def test_read_car_by_id(db_session):
    """Test reading a car by its ID."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id, make="Tesla", model="Model 3")
    
    # Query the car by ID
    retrieved_car = db_session.query(Car).filter(Car.id == car.id).first()
    
    assert retrieved_car is not None
    assert retrieved_car.id == car.id
    assert retrieved_car.make == "Tesla"
    assert retrieved_car.model == "Model 3"
    logger.info(f"Successfully retrieved car with ID: {retrieved_car.id}")


def test_read_user_cars(db_session):
    """Test reading all cars belonging to a specific user."""
    user1 = create_test_user(db_session)
    user2 = create_test_user(db_session)
    
    # Create cars for user1
    car1 = create_test_car(db_session, user1.id, make="Toyota", model="Corolla")
    car2 = create_test_car(db_session, user1.id, make="Honda", model="Civic")
    
    # Create car for user2
    car3 = create_test_car(db_session, user2.id, make="Ford", model="Mustang")
    
    # Query cars for user1
    user1_cars = db_session.query(Car).filter(Car.user_id == user1.id).all()
    
    assert len(user1_cars) == 2
    assert all(c.user_id == user1.id for c in user1_cars)
    car_models = {c.model for c in user1_cars}
    assert car_models == {"Corolla", "Civic"}
    logger.info(f"User1 has {len(user1_cars)} cars")


def test_update_car(db_session):
    """Test updating a car's fields."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id, make="Nissan", model="Altima", year=2018)
    
    original_updated_at = car.updated_at
    
    # Update car fields
    car.year = 2019
    car.trim = "SV"
    car.vin = "1N4AL3AP8JC123456"
    db_session.commit()
    db_session.refresh(car)
    
    assert car.year == 2019
    assert car.trim == "SV"
    assert car.vin == "1N4AL3AP8JC123456"
    assert car.updated_at > original_updated_at
    logger.info(f"Successfully updated car ID: {car.id}")


def test_delete_car(db_session):
    """Test deleting a car."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id, make="Mazda", model="CX-5")
    car_id = car.id
    
    # Delete the car
    db_session.delete(car)
    db_session.commit()
    
    # Verify deletion
    deleted_car = db_session.query(Car).filter(Car.id == car_id).first()
    assert deleted_car is None
    logger.info(f"Successfully deleted car ID: {car_id}")

# ======================================================================================
# Ownership Enforcement Tests
# ======================================================================================

def test_car_ownership_verification(db_session):
    """Test that cars are correctly associated with their owners."""
    user1 = create_test_user(db_session)
    user2 = create_test_user(db_session)
    
    car1 = create_test_car(db_session, user1.id, make="BMW", model="3 Series")
    car2 = create_test_car(db_session, user2.id, make="Audi", model="A4")
    
    # Verify car1 belongs to user1
    assert car1.user_id == user1.id
    assert car1 not in user2.cars
    
    # Verify car2 belongs to user2
    assert car2.user_id == user2.id
    assert car2 not in user1.cars
    
    logger.info("Car ownership correctly enforced")


def test_user_deletion_cascades_to_cars(db_session):
    """Test that deleting a user also deletes their cars (cascade delete)."""
    user = create_test_user(db_session)
    car1 = create_test_car(db_session, user.id, make="Chevrolet", model="Silverado")
    car2 = create_test_car(db_session, user.id, make="GMC", model="Sierra")
    
    car1_id = car1.id
    car2_id = car2.id
    
    # Delete the user
    db_session.delete(user)
    db_session.commit()
    
    # Verify cars are also deleted
    assert db_session.query(Car).filter(Car.id == car1_id).first() is None
    assert db_session.query(Car).filter(Car.id == car2_id).first() is None
    logger.info("User deletion successfully cascaded to cars")


def test_multiple_users_different_cars(db_session):
    """Test that multiple users can have cars with similar attributes."""
    user1 = create_test_user(db_session)
    user2 = create_test_user(db_session)
    
    # Both users have a 2020 Toyota Camry, but different instances
    car1 = create_test_car(
        db_session, 
        user1.id,  # type: ignore
        year=2020, 
        make="Toyota", 
        model="Camry",
        vin="6HGBH41JXMN100002"  # Unique VIN
    )
    car2 = create_test_car(
        db_session, 
        user2.id,  # type: ignore
        year=2020, 
        make="Toyota", 
        model="Camry",
        vin="7HGBH41JXMN100003"  # Different unique VIN
    )
    
    assert car1.id != car2.id  # type: ignore
    assert car1.user_id != car2.user_id  # type: ignore
    assert car1.vin != car2.vin  # type: ignore
    logger.info("Multiple users can have similar cars with different VINs")

# ======================================================================================
# VIN Tests
# ======================================================================================

def test_unique_vin_constraint(db_session):
    """Test that VIN must be unique across all cars."""
    user1 = create_test_user(db_session)
    user2 = create_test_user(db_session)
    
    vin = "3HGBH41JXMN999999"  # Unique VIN for this test
    
    # Create first car with VIN
    car1 = create_test_car(db_session, user1.id, vin=vin)  # type: ignore
    
    # Attempt to create second car with same VIN (should fail)
    car2 = Car(
        year=2021,
        make="Honda",
        model="Accord",
        vin=vin,
        user_id=user2.id  # type: ignore
    )
    db_session.add(car2)
    
    with pytest.raises(Exception):  # Should raise IntegrityError
        db_session.commit()
    
    db_session.rollback()
    logger.info("VIN uniqueness constraint enforced")


def test_null_vins_allowed(db_session):
    """Test that multiple cars can have NULL VINs."""
    user = create_test_user(db_session)
    
    car1 = create_test_car(db_session, user.id, vin=None, make="Honda", model="Civic")
    car2 = create_test_car(db_session, user.id, vin=None, make="Toyota", model="Corolla")
    
    assert car1.vin is None
    assert car2.vin is None
    assert car1.id != car2.id
    logger.info("Multiple NULL VINs allowed")

# ======================================================================================
# Relationship Tests
# ======================================================================================

def test_car_user_relationship(db_session):
    """Test the bidirectional relationship between Car and User."""
    user = create_test_user(db_session)
    car1 = create_test_car(db_session, user.id, make="Subaru", model="Outback")
    car2 = create_test_car(db_session, user.id, make="Subaru", model="Forester")
    
    # Access cars through user relationship
    db_session.refresh(user)
    assert len(user.cars) == 2
    assert car1 in user.cars
    assert car2 in user.cars
    
    # Access user through car relationship
    assert car1.user == user
    assert car2.user == user
    logger.info("Car-User bidirectional relationship working correctly")


def test_query_cars_with_user_join(db_session):
    """Test querying cars with user information via join."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id, make="Volvo", model="XC90")
    
    # Query with join
    result = db_session.query(Car, User).join(User).filter(Car.id == car.id).first()
    
    assert result is not None
    queried_car, queried_user = result
    assert queried_car.id == car.id
    assert queried_user.id == user.id
    assert queried_user.email == user.email
    logger.info("Car-User join query successful")
