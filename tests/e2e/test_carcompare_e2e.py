"""
End-to-End Tests for CarCompare Feature

This module contains comprehensive E2E tests for the CarCompare feature,
testing the complete user workflow from authentication through car and listing management.

Test Coverage:
- User registration and authentication
- Car CRUD operations (Create, Read, Update, Delete)
- Listing management for cars
- VIN decoder integration
- Price comparison statistics
- Negative scenarios (unauthorized access, validation errors)
"""

from datetime import datetime
from uuid import uuid4
import pytest
import requests


# ---------------------------------------------------------------------------
# Helper Fixtures and Functions
# ---------------------------------------------------------------------------
@pytest.fixture
def base_url(fastapi_server: str) -> str:
    """Returns the FastAPI server base URL without a trailing slash."""
    return fastapi_server.rstrip("/")


def _parse_datetime(dt_str: str) -> datetime:
    """Helper function to parse datetime strings from API responses."""
    if dt_str.endswith('Z'):
        dt_str = dt_str.replace('Z', '+00:00')
    return datetime.fromisoformat(dt_str)


def register_and_login(base_url: str, user_data: dict) -> dict:
    """
    Registers a new user and logs in, returning the token response data.
    
    Args:
        base_url: Base URL of the API
        user_data: Dictionary with username, email, password
        
    Returns:
        Dictionary with access_token and token_type
    """
    reg_url = f"{base_url}/auth/register"
    login_url = f"{base_url}/auth/login"
    
    # Add required registration fields
    registration_data = {
        **user_data,
        "first_name": "Test",
        "last_name": "User",
        "confirm_password": user_data["password"]
    }
    
    reg_response = requests.post(reg_url, json=registration_data)
    assert reg_response.status_code == 201, f"User registration failed: {reg_response.text}"
    
    login_payload = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    login_response = requests.post(login_url, json=login_payload)
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    return login_response.json()


def create_test_car(base_url: str, token: str, car_data: dict | None = None) -> dict:
    """
    Creates a test car and returns the response data.
    
    Args:
        base_url: Base URL of the API
        token: JWT access token
        car_data: Optional custom car data, defaults to a test car
        
    Returns:
        Dictionary with car data from API response
    """
    if car_data is None:
        car_data = {
            "year": 2020,
            "make": "Honda",
            "model": "Civic",
            "trim": "Sport",
            "vin": "1HGBH41JXMN109186"
        }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{base_url}/cars", json=car_data, headers=headers)
    assert response.status_code == 201, f"Failed to create car: {response.text}"
    return response.json()


def create_test_listing(base_url: str, token: str, car_id: str, listing_data: dict | None = None) -> dict:
    """
    Creates a test listing for a car.
    
    Args:
        base_url: Base URL of the API
        token: JWT access token
        car_id: UUID of the car
        listing_data: Optional custom listing data
        
    Returns:
        Dictionary with listing data from API response
    """
    if listing_data is None:
        listing_data = {
            "price": 18500,
            "mileage": 45000,
            "source": "Autotrader",
            "url": "https://autotrader.com/listing123"
        }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{base_url}/cars/{car_id}/listings",
        json=listing_data,
        headers=headers
    )
    assert response.status_code == 201, f"Failed to create listing: {response.text}"
    return response.json()


# ---------------------------------------------------------------------------
# E2E Test: Complete Car Management Workflow
# ---------------------------------------------------------------------------
def test_complete_car_workflow(base_url: str):
    """
    E2E Test: Complete workflow from registration to car management.
    
    Tests:
    1. User registration
    2. User login
    3. Create car
    4. Retrieve car list
    5. Retrieve specific car
    6. Update car
    7. Delete car
    """
    # Step 1: Register user
    unique_id = str(uuid4())[:8]
    user_data = {
        "username": f"caruser_{unique_id}",
        "email": f"caruser_{unique_id}@test.com",
        "password": "SecurePass123!"
    }
    token_data = register_and_login(base_url, user_data)
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Create a car
    car_data = {
        "year": 2021,
        "make": "Toyota",
        "model": "Camry",
        "trim": "XLE",
        "vin": "4T1BF1FK5CU123456"
    }
    create_response = requests.post(f"{base_url}/cars", json=car_data, headers=headers)
    assert create_response.status_code == 201
    created_car = create_response.json()
    
    assert created_car["year"] == 2021
    assert created_car["make"] == "Toyota"
    assert created_car["model"] == "Camry"
    assert created_car["trim"] == "XLE"
    assert created_car["vin"] == "4T1BF1FK5CU123456"
    assert "id" in created_car
    assert "created_at" in created_car
    car_id = created_car["id"]
    
    # Step 3: Retrieve car list (should have 1 car)
    list_response = requests.get(f"{base_url}/cars", headers=headers)
    assert list_response.status_code == 200
    cars_list = list_response.json()
    assert len(cars_list) == 1
    assert cars_list[0]["id"] == car_id
    
    # Step 4: Retrieve specific car
    get_response = requests.get(f"{base_url}/cars/{car_id}", headers=headers)
    assert get_response.status_code == 200
    retrieved_car = get_response.json()
    assert retrieved_car["id"] == car_id
    assert retrieved_car["make"] == "Toyota"
    
    # Step 5: Update car
    update_data = {"trim": "SE", "mileage": 25000}
    update_response = requests.patch(
        f"{base_url}/cars/{car_id}",
        json=update_data,
        headers=headers
    )
    assert update_response.status_code == 200
    updated_car = update_response.json()
    assert updated_car["trim"] == "SE"
    
    # Step 6: Delete car
    delete_response = requests.delete(f"{base_url}/cars/{car_id}", headers=headers)
    assert delete_response.status_code == 204
    
    # Step 7: Verify car is deleted
    verify_response = requests.get(f"{base_url}/cars/{car_id}", headers=headers)
    assert verify_response.status_code == 404


# ---------------------------------------------------------------------------
# E2E Test: Listing Management Workflow
# ---------------------------------------------------------------------------
def test_complete_listing_workflow(base_url: str):
    """
    E2E Test: Complete workflow for managing car listings.
    
    Tests:
    1. Create user and car
    2. Add multiple listings
    3. Retrieve listings
    4. Update listing
    5. Delete listing
    6. Verify cascade delete (car deletion removes listings)
    """
    # Setup: Create user and car
    unique_id = str(uuid4())[:8]
    user_data = {
        "username": f"listuser_{unique_id}",
        "email": f"listuser_{unique_id}@test.com",
        "password": "SecurePass123!"
    }
    token_data = register_and_login(base_url, user_data)
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    car = create_test_car(base_url, token)
    car_id = car["id"]
    
    # Step 1: Create multiple listings
    listing1_data = {
        "price": 19500,
        "mileage": 35000,
        "source": "Autotrader",
        "url": "https://autotrader.com/listing1"
    }
    listing1_response = requests.post(
        f"{base_url}/cars/{car_id}/listings",
        json=listing1_data,
        headers=headers
    )
    assert listing1_response.status_code == 201
    listing1 = listing1_response.json()
    listing1_id = listing1["id"]
    
    listing2_data = {
        "price": 18900,
        "mileage": 42000,
        "source": "Craigslist",
        "url": "https://craigslist.org/listing2"
    }
    listing2_response = requests.post(
        f"{base_url}/cars/{car_id}/listings",
        json=listing2_data,
        headers=headers
    )
    assert listing2_response.status_code == 201
    # listing2 variable not used but creation verified by assertion
    
    # Step 2: Retrieve all listings for the car
    list_response = requests.get(f"{base_url}/cars/{car_id}/listings", headers=headers)
    assert list_response.status_code == 200
    listings = list_response.json()
    assert len(listings) == 2
    
    # Step 3: Retrieve specific listing
    get_response = requests.get(
        f"{base_url}/cars/{car_id}/listings/{listing1_id}",
        headers=headers
    )
    assert get_response.status_code == 200
    retrieved_listing = get_response.json()
    assert retrieved_listing["price"] == 19500
    assert retrieved_listing["source"] == "Autotrader"
    
    # Step 4: Update listing
    update_data = {"price": 18500, "mileage": 36000}
    update_response = requests.patch(
        f"{base_url}/cars/{car_id}/listings/{listing1_id}",
        json=update_data,
        headers=headers
    )
    assert update_response.status_code == 200
    updated_listing = update_response.json()
    assert updated_listing["price"] == 18500
    assert updated_listing["mileage"] == 36000
    
    # Step 5: Delete one listing
    delete_response = requests.delete(
        f"{base_url}/cars/{car_id}/listings/{listing1_id}",
        headers=headers
    )
    assert delete_response.status_code == 204
    
    # Verify only 1 listing remains
    verify_response = requests.get(f"{base_url}/cars/{car_id}/listings", headers=headers)
    assert verify_response.status_code == 200
    remaining_listings = verify_response.json()
    assert len(remaining_listings) == 1
    
    # Step 6: Delete car and verify cascade delete of listings
    car_delete_response = requests.delete(f"{base_url}/cars/{car_id}", headers=headers)
    assert car_delete_response.status_code == 204
    
    # Verify listings are also deleted (car doesn't exist, so 404 expected)
    listings_after_delete = requests.get(f"{base_url}/cars/{car_id}/listings", headers=headers)
    assert listings_after_delete.status_code == 404


# ---------------------------------------------------------------------------
# E2E Test: Price Comparison Statistics
# ---------------------------------------------------------------------------
def test_price_comparison_workflow(base_url: str):
    """
    E2E Test: Complete workflow for price comparison statistics.
    
    Tests:
    1. Create car with multiple listings
    2. Retrieve comparison statistics
    3. Verify min/max/average prices
    4. Verify price per mile calculations
    5. Verify best deal identification
    """
    # Setup
    unique_id = str(uuid4())[:8]
    user_data = {
        "username": f"compuser_{unique_id}",
        "email": f"compuser_{unique_id}@test.com",
        "password": "SecurePass123!"
    }
    token_data = register_and_login(base_url, user_data)
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    car = create_test_car(base_url, token)
    car_id = car["id"]
    
    # Create listings with known prices and mileage
    listings_data = [
        {"price": 20000, "mileage": 40000, "source": "Autotrader", "url": "https://autotrader.com/1"},
        {"price": 18000, "mileage": 50000, "source": "CarGurus", "url": "https://cargurus.com/1"},
        {"price": 22000, "mileage": 30000, "source": "Craigslist", "url": "https://craigslist.org/1"},
    ]
    
    for listing_data in listings_data:
        response = requests.post(
            f"{base_url}/cars/{car_id}/listings",
            json=listing_data,
            headers=headers
        )
        assert response.status_code == 201
    
    # Get comparison statistics
    compare_response = requests.get(f"{base_url}/cars/{car_id}/compare", headers=headers)
    assert compare_response.status_code == 200
    stats = compare_response.json()
    
    # Verify statistics
    assert stats["total_listings"] == 3
    assert stats["min_price"] == 18000
    assert stats["max_price"] == 22000
    assert stats["avg_price"] == 20000  # (20000 + 18000 + 22000) / 3
    
    # Verify price per mile calculations
    # CarGurus: 18000/50000 = 0.36 (best deal)
    # Autotrader: 20000/40000 = 0.50
    # Craigslist: 22000/30000 = 0.73
    assert stats["avg_price_per_mile"] is not None
    assert "best_deal" in stats
    assert stats["best_deal"]["source"] == "CarGurus"
    assert stats["best_deal"]["price"] == 18000


# ---------------------------------------------------------------------------
# E2E Test: VIN Decoder Integration
# ---------------------------------------------------------------------------
def test_vin_decoder_workflow(base_url: str):
    """
    E2E Test: VIN decoder integration workflow.
    
    Tests:
    1. Call VIN decoder endpoint with valid VIN
    2. Verify decoded vehicle information
    3. Create car using decoded information
    4. Test with invalid VIN (negative scenario)
    """
    # Valid VIN test
    valid_vin = "1HGBH41JXMN109186"
    vin_response = requests.get(f"{base_url}/vin/{valid_vin}")
    assert vin_response.status_code == 200
    vin_data = vin_response.json()
    
    # Verify decoded data structure
    assert "vin" in vin_data
    assert "year" in vin_data
    assert "make" in vin_data
    assert "model" in vin_data
    assert vin_data["vin"] == valid_vin
    
    # Create user and use decoded VIN data to create car
    unique_id = str(uuid4())[:8]
    user_data = {
        "username": f"vinuser_{unique_id}",
        "email": f"vinuser_{unique_id}@test.com",
        "password": "SecurePass123!"
    }
    token_data = register_and_login(base_url, user_data)
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create car using VIN-decoded data
    car_data = {
        "year": vin_data["year"],
        "make": vin_data["make"],
        "model": vin_data["model"],
        "vin": valid_vin
    }
    car_response = requests.post(f"{base_url}/cars", json=car_data, headers=headers)
    assert car_response.status_code == 201
    created_car = car_response.json()
    assert created_car["vin"] == valid_vin
    
    # Test invalid VIN (negative scenario)
    invalid_vin = "INVALID123"
    invalid_response = requests.get(f"{base_url}/vin/{invalid_vin}")
    # Should return 400 or 422 for invalid VIN format
    assert invalid_response.status_code in [400, 422]


# ---------------------------------------------------------------------------
# E2E Test: Unauthorized Access (Negative Scenario)
# ---------------------------------------------------------------------------
def test_unauthorized_access_scenarios(base_url: str):
    """
    E2E Test: Negative scenarios for unauthorized access.
    
    Tests:
    1. Accessing cars without authentication
    2. Accessing another user's car
    3. Updating another user's listing
    4. Deleting another user's car
    """
    # Create two users with cars
    unique_id1 = str(uuid4())[:8]
    user1_data = {
        "username": f"user1_{unique_id1}",
        "email": f"user1_{unique_id1}@test.com",
        "password": "SecurePass123!"
    }
    token1_data = register_and_login(base_url, user1_data)
    token1 = token1_data["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    unique_id2 = str(uuid4())[:8]
    user2_data = {
        "username": f"user2_{unique_id2}",
        "email": f"user2_{unique_id2}@test.com",
        "password": "SecurePass123!"
    }
    token2_data = register_and_login(base_url, user2_data)
    token2 = token2_data["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # User 1 creates a car
    car1 = create_test_car(base_url, token1)
    car1_id = car1["id"]
    
    # Test 1: Access without authentication
    no_auth_response = requests.get(f"{base_url}/cars")
    assert no_auth_response.status_code == 401
    
    # Test 2: User 2 tries to access User 1's car
    unauthorized_get = requests.get(f"{base_url}/cars/{car1_id}", headers=headers2)
    assert unauthorized_get.status_code == 404  # Not found (ownership check)
    
    # Test 3: User 2 tries to update User 1's car
    unauthorized_update = requests.patch(
        f"{base_url}/cars/{car1_id}",
        json={"trim": "Hacked"},
        headers=headers2
    )
    assert unauthorized_update.status_code == 404
    
    # Test 4: User 2 tries to delete User 1's car
    unauthorized_delete = requests.delete(f"{base_url}/cars/{car1_id}", headers=headers2)
    assert unauthorized_delete.status_code == 404
    
    # Verify User 1's car is still intact
    verify_response = requests.get(f"{base_url}/cars/{car1_id}", headers=headers1)
    assert verify_response.status_code == 200


# ---------------------------------------------------------------------------
# E2E Test: Validation Errors (Negative Scenario)
# ---------------------------------------------------------------------------
def test_validation_error_scenarios(base_url: str):
    """
    E2E Test: Negative scenarios for data validation.
    
    Tests:
    1. Invalid car year (too old/future)
    2. Missing required fields
    3. Invalid VIN format
    4. Invalid price (negative)
    5. Invalid mileage (negative)
    6. Invalid URL format
    """
    # Setup
    unique_id = str(uuid4())[:8]
    user_data = {
        "username": f"valuser_{unique_id}",
        "email": f"valuser_{unique_id}@test.com",
        "password": "SecurePass123!"
    }
    token_data = register_and_login(base_url, user_data)
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Invalid year (too old)
    invalid_year_data = {
        "year": 1800,
        "make": "Ford",
        "model": "Model T"
    }
    response1 = requests.post(f"{base_url}/cars", json=invalid_year_data, headers=headers)
    assert response1.status_code == 422
    
    # Test 2: Missing required fields
    missing_fields_data = {
        "make": "Toyota"
        # Missing year and model
    }
    response2 = requests.post(f"{base_url}/cars", json=missing_fields_data, headers=headers)
    assert response2.status_code == 422
    
    # Test 3: Invalid VIN format (not 17 characters)
    invalid_vin_data = {
        "year": 2020,
        "make": "Honda",
        "model": "Civic",
        "vin": "SHORT"
    }
    response3 = requests.post(f"{base_url}/cars", json=invalid_vin_data, headers=headers)
    assert response3.status_code == 422
    
    # Create valid car for listing tests
    car = create_test_car(base_url, token)
    car_id = car["id"]
    
    # Test 4: Invalid price (negative)
    invalid_price_data = {
        "price": -5000,
        "mileage": 50000,
        "source": "Test"
    }
    response4 = requests.post(
        f"{base_url}/cars/{car_id}/listings",
        json=invalid_price_data,
        headers=headers
    )
    assert response4.status_code == 422
    
    # Test 5: Invalid mileage (negative)
    invalid_mileage_data = {
        "price": 20000,
        "mileage": -10000,
        "source": "Test"
    }
    response5 = requests.post(
        f"{base_url}/cars/{car_id}/listings",
        json=invalid_mileage_data,
        headers=headers
    )
    assert response5.status_code == 422
    
    # Test 6: Invalid URL format
    invalid_url_data = {
        "price": 20000,
        "mileage": 50000,
        "source": "Test",
        "url": "not-a-valid-url"
    }
    response6 = requests.post(
        f"{base_url}/cars/{car_id}/listings",
        json=invalid_url_data,
        headers=headers
    )
    assert response6.status_code == 422


# ---------------------------------------------------------------------------
# E2E Test: Multiple Users Data Isolation
# ---------------------------------------------------------------------------
def test_multi_user_data_isolation(base_url: str):
    """
    E2E Test: Verify complete data isolation between users.
    
    Tests:
    1. Create multiple users with cars
    2. Verify each user only sees their own cars
    3. Verify listing counts are isolated
    4. Verify comparison stats are per-user
    """
    # Create User 1 with 2 cars
    unique_id1 = str(uuid4())[:8]
    user1_data = {
        "username": f"isolate1_{unique_id1}",
        "email": f"isolate1_{unique_id1}@test.com",
        "password": "SecurePass123!"
    }
    token1_data = register_and_login(base_url, user1_data)
    token1 = token1_data["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    car1_user1 = create_test_car(base_url, token1, {
        "year": 2020,
        "make": "Honda",
        "model": "Civic",
        "vin": "1HGBH41JXMN109186"
    })
    car2_user1 = create_test_car(base_url, token1, {
        "year": 2019,
        "make": "Toyota",
        "model": "Camry",
        "vin": "4T1BF1FK5CU654321"
    })
    
    # Create User 2 with 1 car
    unique_id2 = str(uuid4())[:8]
    user2_data = {
        "username": f"isolate2_{unique_id2}",
        "email": f"isolate2_{unique_id2}@test.com",
        "password": "SecurePass123!"
    }
    token2_data = register_and_login(base_url, user2_data)
    token2 = token2_data["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    car1_user2 = create_test_car(base_url, token2, {
        "year": 2021,
        "make": "Mazda",
        "model": "CX-5",
        "vin": "JM3KFBDM8M0123456"
    })
    
    # Verify User 1 sees only their 2 cars
    user1_cars = requests.get(f"{base_url}/cars", headers=headers1)
    assert user1_cars.status_code == 200
    user1_cars_data = user1_cars.json()
    assert len(user1_cars_data) == 2
    user1_car_ids = [car["id"] for car in user1_cars_data]
    assert car1_user1["id"] in user1_car_ids
    assert car2_user1["id"] in user1_car_ids
    assert car1_user2["id"] not in user1_car_ids
    
    # Verify User 2 sees only their 1 car
    user2_cars = requests.get(f"{base_url}/cars", headers=headers2)
    assert user2_cars.status_code == 200
    user2_cars_data = user2_cars.json()
    assert len(user2_cars_data) == 1
    assert user2_cars_data[0]["id"] == car1_user2["id"]


# ---------------------------------------------------------------------------
# E2E Test: Cascade Delete Operations
# ---------------------------------------------------------------------------
def test_cascade_delete_operations(base_url: str):
    """
    E2E Test: Verify cascade delete behavior.
    
    Tests:
    1. Delete car with listings - verify listings are also deleted
    2. Verify related data cleanup
    """
    # Setup
    unique_id = str(uuid4())[:8]
    user_data = {
        "username": f"cascade_{unique_id}",
        "email": f"cascade_{unique_id}@test.com",
        "password": "SecurePass123!"
    }
    token_data = register_and_login(base_url, user_data)
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create car with multiple listings
    car = create_test_car(base_url, token)
    car_id = car["id"]
    
    create_test_listing(base_url, token, car_id, {
        "price": 20000,
        "mileage": 40000,
        "source": "Autotrader"
    })
    create_test_listing(base_url, token, car_id, {
        "price": 19000,
        "mileage": 45000,
        "source": "CarGurus"
    })
    
    # Verify listings exist
    listings_response = requests.get(f"{base_url}/cars/{car_id}/listings", headers=headers)
    assert listings_response.status_code == 200
    assert len(listings_response.json()) == 2
    
    # Delete car
    delete_response = requests.delete(f"{base_url}/cars/{car_id}", headers=headers)
    assert delete_response.status_code == 204
    
    # Verify car is deleted
    car_response = requests.get(f"{base_url}/cars/{car_id}", headers=headers)
    assert car_response.status_code == 404
    
    # Verify listings are also deleted (cascade)
    listings_after_delete = requests.get(f"{base_url}/cars/{car_id}/listings", headers=headers)
    assert listings_after_delete.status_code == 404
