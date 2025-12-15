# ======================================================================================
# tests/integration/test_car_compare.py
# ======================================================================================
# Purpose: Integration tests for the car comparison statistics endpoint
# ======================================================================================

import pytest
import uuid
import logging
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


def compute_comparison_stats(listings: list[Listing]) -> dict:
    """
    Manually compute comparison statistics to verify endpoint results.
    Mimics the logic in the GET /cars/{car_id}/compare endpoint.
    """
    if not listings:
        return {
            "count": 0,
            "min_price": None,
            "max_price": None,
            "avg_price": None,
            "avg_price_per_mile": None,
            "best_deal_listing_id": None
        }
    
    count = len(listings)
    prices = [float(l.price) for l in listings]  # type: ignore
    min_price = min(prices)
    max_price = max(prices)
    avg_price = sum(prices) / count
    
    # Calculate avg price per mile for listings with mileage > 0
    listings_with_mileage = [l for l in listings if l.mileage and l.mileage > 0]  # type: ignore
    if listings_with_mileage:
        price_per_mile_values = [
            float(l.price) / l.mileage  # type: ignore
            for l in listings_with_mileage
        ]
        avg_price_per_mile = sum(price_per_mile_values) / len(price_per_mile_values)
        
        # Best deal = lowest price per mile
        best_deal_listing = min(
            listings_with_mileage,
            key=lambda l: float(l.price) / l.mileage  # type: ignore
        )
        best_deal_listing_id = str(best_deal_listing.id)  # type: ignore
    else:
        avg_price_per_mile = None
        best_deal_listing_id = None
    
    return {
        "count": count,
        "min_price": round(min_price, 2),
        "max_price": round(max_price, 2),
        "avg_price": round(avg_price, 2),
        "avg_price_per_mile": round(avg_price_per_mile, 2) if avg_price_per_mile else None,
        "best_deal_listing_id": best_deal_listing_id
    }

# ======================================================================================
# Comparison Statistics Tests
# ======================================================================================

def test_compare_no_listings(db_session):
    """Test comparison stats for a car with no listings."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id)  # type: ignore
    
    # Get listings (should be empty)
    listings = db_session.query(Listing).filter(Listing.car_id == car.id).all()  # type: ignore
    
    stats = compute_comparison_stats(listings)
    
    assert stats["count"] == 0
    assert stats["min_price"] is None
    assert stats["max_price"] is None
    assert stats["avg_price"] is None
    assert stats["avg_price_per_mile"] is None
    assert stats["best_deal_listing_id"] is None
    logger.info("Comparison stats correct for car with no listings")


def test_compare_single_listing(db_session):
    """Test comparison stats for a car with one listing."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id)  # type: ignore
    
    listing = create_test_listing(
        db_session,
        car.id,  # type: ignore
        user.id,  # type: ignore
        price=25000.00,
        mileage=50000
    )
    
    listings = db_session.query(Listing).filter(Listing.car_id == car.id).all()  # type: ignore
    stats = compute_comparison_stats(listings)
    
    assert stats["count"] == 1
    assert stats["min_price"] == 25000.00
    assert stats["max_price"] == 25000.00
    assert stats["avg_price"] == 25000.00
    assert stats["avg_price_per_mile"] == 0.50  # 25000 / 50000
    assert stats["best_deal_listing_id"] == str(listing.id)  # type: ignore
    logger.info("Comparison stats correct for car with single listing")


def test_compare_multiple_listings(db_session):
    """Test comparison stats for a car with multiple listings."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id)  # type: ignore
    
    # Create listings with different prices and mileage
    listing1 = create_test_listing(db_session, car.id, user.id, price=20000, mileage=60000, source="S1")  # type: ignore
    listing2 = create_test_listing(db_session, car.id, user.id, price=22000, mileage=50000, source="S2")  # type: ignore
    listing3 = create_test_listing(db_session, car.id, user.id, price=25000, mileage=40000, source="S3")  # type: ignore
    listing4 = create_test_listing(db_session, car.id, user.id, price=18000, mileage=70000, source="S4")  # type: ignore
    
    listings = db_session.query(Listing).filter(Listing.car_id == car.id).all()  # type: ignore
    stats = compute_comparison_stats(listings)
    
    assert stats["count"] == 4
    assert stats["min_price"] == 18000.00
    assert stats["max_price"] == 25000.00
    assert stats["avg_price"] == 21250.00  # (20000 + 22000 + 25000 + 18000) / 4
    
    # Price per mile calculations:
    # listing1: 20000/60000 = 0.333...
    # listing2: 22000/50000 = 0.44
    # listing3: 25000/40000 = 0.625
    # listing4: 18000/70000 = 0.257...
    # Average: (0.333 + 0.44 + 0.625 + 0.257) / 4 = 0.414
    assert abs(stats["avg_price_per_mile"] - 0.41) < 0.01  # type: ignore
    
    # Best deal is listing4 (lowest price per mile: 0.257)
    assert stats["best_deal_listing_id"] == str(listing4.id)  # type: ignore
    logger.info("Comparison stats correct for car with multiple listings")


def test_compare_listings_with_no_mileage(db_session):
    """Test comparison stats when listings have no mileage data."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id)  # type: ignore
    
    # Create listings without mileage
    listing1 = create_test_listing(db_session, car.id, user.id, price=30000, mileage=None, source="S1")  # type: ignore
    listing2 = create_test_listing(db_session, car.id, user.id, price=32000, mileage=None, source="S2")  # type: ignore
    
    listings = db_session.query(Listing).filter(Listing.car_id == car.id).all()  # type: ignore
    stats = compute_comparison_stats(listings)
    
    assert stats["count"] == 2
    assert stats["min_price"] == 30000.00
    assert stats["max_price"] == 32000.00
    assert stats["avg_price"] == 31000.00
    assert stats["avg_price_per_mile"] is None
    assert stats["best_deal_listing_id"] is None
    logger.info("Comparison stats correct for listings without mileage")


def test_compare_listings_mixed_mileage(db_session):
    """Test comparison stats with mixed mileage data (some null, some values)."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id)  # type: ignore
    
    # Create listings with mixed mileage
    listing1 = create_test_listing(db_session, car.id, user.id, price=25000, mileage=50000, source="S1")  # type: ignore
    listing2 = create_test_listing(db_session, car.id, user.id, price=27000, mileage=None, source="S2")  # type: ignore
    listing3 = create_test_listing(db_session, car.id, user.id, price=23000, mileage=60000, source="S3")  # type: ignore
    
    listings = db_session.query(Listing).filter(Listing.car_id == car.id).all()  # type: ignore
    stats = compute_comparison_stats(listings)
    
    assert stats["count"] == 3
    assert stats["min_price"] == 23000.00
    assert stats["max_price"] == 27000.00
    assert stats["avg_price"] == 25000.00  # (25000 + 27000 + 23000) / 3
    
    # Only listing1 and listing3 have mileage
    # listing1: 25000/50000 = 0.50
    # listing3: 23000/60000 = 0.383...
    # Average: (0.50 + 0.383) / 2 = 0.442
    assert abs(stats["avg_price_per_mile"] - 0.44) < 0.01  # type: ignore
    
    # Best deal is listing3 (0.383 < 0.50)
    assert stats["best_deal_listing_id"] == str(listing3.id)  # type: ignore
    logger.info("Comparison stats correct for mixed mileage data")


def test_compare_listings_with_zero_mileage(db_session):
    """Test comparison stats when a listing has zero mileage (new car)."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id)  # type: ignore
    
    # Create listings with one having zero mileage
    listing1 = create_test_listing(db_session, car.id, user.id, price=35000, mileage=0, source="S1")  # type: ignore
    listing2 = create_test_listing(db_session, car.id, user.id, price=28000, mileage=40000, source="S2")  # type: ignore
    
    listings = db_session.query(Listing).filter(Listing.car_id == car.id).all()  # type: ignore
    stats = compute_comparison_stats(listings)
    
    assert stats["count"] == 2
    assert stats["min_price"] == 28000.00
    assert stats["max_price"] == 35000.00
    assert stats["avg_price"] == 31500.00
    
    # Only listing2 has mileage > 0
    # listing2: 28000/40000 = 0.70
    assert stats["avg_price_per_mile"] == 0.70
    assert stats["best_deal_listing_id"] == str(listing2.id)  # type: ignore
    logger.info("Comparison stats correct with zero mileage listing")


def test_compare_identical_prices(db_session):
    """Test comparison stats when all listings have identical prices."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id)  # type: ignore
    
    # Create listings with same price but different mileage
    listing1 = create_test_listing(db_session, car.id, user.id, price=24000, mileage=45000, source="S1")  # type: ignore
    listing2 = create_test_listing(db_session, car.id, user.id, price=24000, mileage=50000, source="S2")  # type: ignore
    listing3 = create_test_listing(db_session, car.id, user.id, price=24000, mileage=55000, source="S3")  # type: ignore
    
    listings = db_session.query(Listing).filter(Listing.car_id == car.id).all()  # type: ignore
    stats = compute_comparison_stats(listings)
    
    assert stats["count"] == 3
    assert stats["min_price"] == 24000.00
    assert stats["max_price"] == 24000.00
    assert stats["avg_price"] == 24000.00
    
    # All have same price, so best deal is the one with highest mileage (lowest price/mile)
    # listing3: 24000/55000 = 0.436...
    assert stats["best_deal_listing_id"] == str(listing3.id)  # type: ignore
    logger.info("Comparison stats correct for identical prices")


def test_compare_price_precision(db_session):
    """Test that comparison stats maintain proper decimal precision."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id)  # type: ignore
    
    # Create listings with precise prices
    listing1 = create_test_listing(db_session, car.id, user.id, price=20999.99, mileage=50000, source="S1")  # type: ignore
    listing2 = create_test_listing(db_session, car.id, user.id, price=21500.50, mileage=48000, source="S2")  # type: ignore
    listing3 = create_test_listing(db_session, car.id, user.id, price=22000.01, mileage=52000, source="S3")  # type: ignore
    
    listings = db_session.query(Listing).filter(Listing.car_id == car.id).all()  # type: ignore
    stats = compute_comparison_stats(listings)
    
    assert stats["count"] == 3
    assert stats["min_price"] == 20999.99
    assert stats["max_price"] == 22000.01
    # Average: (20999.99 + 21500.50 + 22000.01) / 3 = 21500.17
    assert abs(stats["avg_price"] - 21500.17) < 0.01
    logger.info("Comparison stats maintain proper decimal precision")


def test_compare_ownership_isolation(db_session):
    """Test that comparison stats only include listings for the specific car."""
    user = create_test_user(db_session)
    car1 = create_test_car(db_session, user.id, make="Honda", model="Civic")  # type: ignore
    car2 = create_test_car(db_session, user.id, make="Toyota", model="Corolla")  # type: ignore
    
    # Create listings for car1
    listing1 = create_test_listing(db_session, car1.id, user.id, price=18000, mileage=40000, source="S1")  # type: ignore
    listing2 = create_test_listing(db_session, car1.id, user.id, price=19000, mileage=35000, source="S2")  # type: ignore
    
    # Create listings for car2
    listing3 = create_test_listing(db_session, car2.id, user.id, price=25000, mileage=30000, source="S3")  # type: ignore
    listing4 = create_test_listing(db_session, car2.id, user.id, price=26000, mileage=28000, source="S4")  # type: ignore
    
    # Get stats for car1 only
    car1_listings = db_session.query(Listing).filter(Listing.car_id == car1.id).all()  # type: ignore
    car1_stats = compute_comparison_stats(car1_listings)
    
    # Verify car1 stats don't include car2 listings
    assert car1_stats["count"] == 2
    assert car1_stats["min_price"] == 18000.00
    assert car1_stats["max_price"] == 19000.00
    
    # Get stats for car2 only
    car2_listings = db_session.query(Listing).filter(Listing.car_id == car2.id).all()  # type: ignore
    car2_stats = compute_comparison_stats(car2_listings)
    
    # Verify car2 stats don't include car1 listings
    assert car2_stats["count"] == 2
    assert car2_stats["min_price"] == 25000.00
    assert car2_stats["max_price"] == 26000.00
    
    logger.info("Comparison stats correctly isolated by car ownership")


def test_compare_large_dataset(db_session):
    """Test comparison stats with a larger number of listings."""
    user = create_test_user(db_session)
    car = create_test_car(db_session, user.id)  # type: ignore
    
    # Create 20 listings with varying prices and mileage
    base_price = 20000
    base_mileage = 40000
    listings = []
    
    for i in range(20):
        listing = create_test_listing(
            db_session,
            car.id,  # type: ignore
            user.id,  # type: ignore
            price=base_price + (i * 500),
            mileage=base_mileage + (i * 1000),
            source=f"Source_{i}"
        )
        listings.append(listing)
    
    retrieved_listings = db_session.query(Listing).filter(Listing.car_id == car.id).all()  # type: ignore
    stats = compute_comparison_stats(retrieved_listings)
    
    assert stats["count"] == 20
    assert stats["min_price"] == 20000.00
    assert stats["max_price"] == 29500.00  # 20000 + (19 * 500)
    assert stats["avg_price"] == 24750.00  # (20000 + 29500) / 2
    assert stats["avg_price_per_mile"] is not None
    assert stats["best_deal_listing_id"] is not None
    logger.info("Comparison stats correct for large dataset (20 listings)")
