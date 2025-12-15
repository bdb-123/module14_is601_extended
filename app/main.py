"""
FastAPI Main Application Module

This module defines the main FastAPI application, including:
- Application initialization and configuration
- API endpoints for user authentication
- API endpoints for calculation management (BREAD operations)
- Web routes for HTML templates
- Database table creation on startup

The application follows a RESTful API design with proper separation of concerns:
- Routes handle HTTP requests and responses
- Models define database structure
- Schemas validate request/response data
- Dependencies handle authentication and database sessions
"""

from contextlib import asynccontextmanager  # Used for startup/shutdown events
from datetime import datetime, timezone, timedelta
from uuid import UUID  # For type validation of UUIDs in path parameters
from typing import List

# FastAPI imports
from fastapi import Body, FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles  # For serving static files (CSS, JS)
from fastapi.templating import Jinja2Templates  # For HTML templates

from sqlalchemy.orm import Session  # SQLAlchemy database session

import uvicorn  # ASGI server for running FastAPI apps

# Application imports
from app.auth.dependencies import get_current_active_user  # Authentication dependency
from app.models.calculation import Calculation  # Database model for calculations
from app.models.user import User  # Database model for users
from app.models.car import Car  # Database model for cars
from app.models.listing import Listing  # Database model for listings
from app.schemas.calculation import CalculationBase, CalculationResponse, CalculationUpdate  # API request/response schemas
from app.schemas.token import TokenResponse  # API token schema
from app.schemas.user import UserCreate, UserResponse, UserLogin  # User schemas
from app.schemas.car import CarCreate, CarUpdate, CarResponse, CarCompareStats, VINDecodeResponse  # Car schemas
from app.schemas.listing import ListingCreate, ListingUpdate, ListingResponse  # Listing schemas
from app.schemas.recommendation import CarRecommendationRequest, CarRecommendationResponse  # Recommendation schemas
from app.schemas.live_listing import LiveListingSearch, LiveListingResponse  # Live listing schemas
from app.database import Base, get_db, engine  # Database connection
from app.services.vin_decoder import VINDecoderService  # VIN decoder service


# ------------------------------------------------------------------------------
# Create tables on startup using the lifespan event
# ------------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI.
    
    This runs when the application starts and creates all database tables
    defined in SQLAlchemy models. It's an alternative to using Alembic
    for simpler applications.
    
    Args:
        app: FastAPI application instance
    """
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    yield  # This is where application runs
    # Cleanup code would go here (after yield), but we don't need any

# Initialize the FastAPI application with metadata and lifespan
app = FastAPI(
    title="Calculations API",
    description="API for managing calculations",
    version="1.0.0",
    lifespan=lifespan  # Pass our lifespan context manager
)

# ------------------------------------------------------------------------------
# Static Files and Templates Configuration
# ------------------------------------------------------------------------------
# Mount the static files directory for serving CSS, JS, and images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates directory for HTML rendering
templates = Jinja2Templates(directory="templates")


# ------------------------------------------------------------------------------
# Web (HTML) Routes
# ------------------------------------------------------------------------------
# Our web routes use HTML responses with Jinja2 templates
# These provide a user-friendly web interface alongside the API

@app.get("/", response_class=HTMLResponse, tags=["web"])
def read_index(request: Request):
    """
    Landing page.
    
    Displays the welcome page with links to register and login.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse, tags=["web"])
def login_page(request: Request):
    """
    Login page.
    
    Displays a form for users to enter credentials and log in.
    """
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse, tags=["web"])
def register_page(request: Request):
    """
    Registration page.
    
    Displays a form for new users to create an account.
    """
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse, tags=["web"])
def dashboard_page(request: Request):
    """
    Dashboard page, listing calculations & new calculation form.
    
    This is the main interface after login, where users can:
    - See all their calculations
    - Create a new calculation
    - Access links to view/edit/delete calculations
    
    JavaScript in this page calls the API endpoints to fetch and display data.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/dashboard/view/{calc_id}", response_class=HTMLResponse, tags=["web"])
def view_calculation_page(request: Request, calc_id: str):
    """
    Page for viewing a single calculation (Read).
    
    Part of the BREAD (Browse, Read, Edit, Add, Delete) pattern:
    - This is the Read page
    
    Args:
        request: The FastAPI request object (required by Jinja2)
        calc_id: UUID of the calculation to view
        
    Returns:
        HTMLResponse: Rendered template with calculation ID passed to frontend
    """
    return templates.TemplateResponse("view_calculation.html", {"request": request, "calc_id": calc_id})

@app.get("/dashboard/edit/{calc_id}", response_class=HTMLResponse, tags=["web"])
def edit_calculation_page(request: Request, calc_id: str):
    """
    Page for editing a calculation (Update).
    
    Part of the BREAD (Browse, Read, Edit, Add, Delete) pattern:
    - This is the Edit page
    
    Args:
        request: The FastAPI request object (required by Jinja2)
        calc_id: UUID of the calculation to edit
        
    Returns:
        HTMLResponse: Rendered template with calculation ID passed to frontend
    """
    return templates.TemplateResponse("edit_calculation.html", {"request": request, "calc_id": calc_id})

@app.get("/cars-ui", response_class=HTMLResponse, tags=["web"])
def cars_page(request: Request):
    """
    Cars list page for CarCompare feature.
    
    This page displays all cars owned by the user and provides:
    - A form to add a new car
    - VIN decoder integration
    - List/grid of user's cars with delete functionality
    - Links to individual car detail pages
    
    JavaScript in this page calls the /cars API endpoints.
    """
    return templates.TemplateResponse("cars.html", {"request": request})

@app.get("/cars-ui/{car_id}", response_class=HTMLResponse, tags=["web"])
def car_detail_page(request: Request, car_id: str):
    """
    Car detail page showing listings and comparison statistics.
    
    This page displays:
    - Car details (year, make, model, trim, VIN)
    - All listings for this car
    - Comparison statistics (min/max/avg prices, best deal)
    - Form to add new listings
    - Delete functionality for car and listings
    
    Args:
        request: The FastAPI request object (required by Jinja2)
        car_id: UUID of the car to view
        
    Returns:
        HTMLResponse: Rendered template with car ID passed to frontend
    """
    return templates.TemplateResponse("car_detail.html", {"request": request, "car_id": car_id})

@app.get("/recommendations-ui", response_class=HTMLResponse, tags=["web"])
def recommendations_page(request: Request):
    """
    AI-powered car recommendations page.
    
    This page allows users to input their preferences and get
    intelligent car recommendations based on:
    - Budget
    - Body style
    - Year range
    - Brands
    - Features
    
    JavaScript in this page calls the /cars/recommendations API endpoint.
    """
    return templates.TemplateResponse("recommendations.html", {"request": request})

@app.get("/live-listings-ui", response_class=HTMLResponse, tags=["web"])
def live_listings_page(request: Request):
    """
    Live car listings search page.
    
    This page allows users to search real-time car listings from
    multiple sources (CarGurus, Autotrader, Cars.com, etc.).
    
    JavaScript in this page calls the /cars/live-listings API endpoint.
    """
    return templates.TemplateResponse("live_listings.html", {"request": request})

@app.get("/gallery-ui", response_class=HTMLResponse, tags=["web"])
def gallery_page(request: Request):
    """
    Car gallery showcase page.
    
    This page displays a visual gallery of popular cars including:
    - Lexus luxury vehicles (IS 350, ES 350, RX 350)
    - Honda Civic variants (Sedan, Coupe, Hatchback)
    
    Features real car images from Imagin Studio API with detailed
    specifications, pricing, and feature highlights.
    """
    return templates.TemplateResponse("gallery.html", {"request": request})


# ------------------------------------------------------------------------------
# Health Endpoint
# ------------------------------------------------------------------------------
@app.get("/health", tags=["health"])
def read_health():
    """Health check."""
    return {"status": "ok"}


# ------------------------------------------------------------------------------
# User Registration Endpoint
# ------------------------------------------------------------------------------
@app.post(
    "/auth/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    tags=["auth"]
)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.
    """
    user_data = user_create.dict(exclude={"confirm_password"})
    try:
        user = User.register(db, user_data)
        db.commit()
        db.refresh(user)
        return user
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ------------------------------------------------------------------------------
# User Login Endpoints
# ------------------------------------------------------------------------------
@app.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login_json(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    Login with JSON payload (username & password).
    Returns an access token, refresh token, and user info.
    """
    auth_result = User.authenticate(db, user_login.username, user_login.password)
    if auth_result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = auth_result["user"]
    db.commit()  # commit the last_login update

    # Ensure expires_at is timezone-aware
    expires_at = auth_result.get("expires_at")
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    else:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    return TokenResponse(
        access_token=auth_result["access_token"],
        refresh_token=auth_result["refresh_token"],
        token_type="bearer",
        expires_at=expires_at,
        user_id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified=user.is_verified
    )

@app.post("/auth/token", tags=["auth"])
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login with form data (Swagger/UI).
    Returns an access token.
    """
    auth_result = User.authenticate(db, form_data.username, form_data.password)
    if auth_result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": auth_result["access_token"],
        "token_type": "bearer"
    }


# ------------------------------------------------------------------------------
# Calculations Endpoints (BREAD)
# ------------------------------------------------------------------------------
# Create (Add) Calculation
@app.post(
    "/calculations",
    response_model=CalculationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["calculations"],
)
def create_calculation(
    calculation_data: CalculationBase,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new calculation for the authenticated user.
    Automatically computes the 'result'.
    """
    try:
        new_calculation = Calculation.create(
            calculation_type=calculation_data.type,
            user_id=current_user.id,
            inputs=calculation_data.inputs,
        )
        new_calculation.result = new_calculation.get_result()

        db.add(new_calculation)
        db.commit()
        db.refresh(new_calculation)
        return new_calculation

    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Browse / List Calculations
@app.get("/calculations", response_model=List[CalculationResponse], tags=["calculations"])
def list_calculations(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all calculations belonging to the current authenticated user.
    """
    calculations = db.query(Calculation).filter(Calculation.user_id == current_user.id).all()
    return calculations


# Read / Retrieve a Specific Calculation by ID
@app.get("/calculations/{calc_id}", response_model=CalculationResponse, tags=["calculations"])
def get_calculation(
    calc_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a single calculation by its UUID, if it belongs to the current user.
    """
    try:
        calc_uuid = UUID(calc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid calculation id format.")

    calculation = db.query(Calculation).filter(
        Calculation.id == calc_uuid,
        Calculation.user_id == current_user.id
    ).first()
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found.")

    return calculation


# Edit / Update a Calculation
@app.put("/calculations/{calc_id}", response_model=CalculationResponse, tags=["calculations"])
def update_calculation(
    calc_id: str,
    calculation_update: CalculationUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update the inputs (and thus the result) of a specific calculation.
    """
    try:
        calc_uuid = UUID(calc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid calculation id format.")

    calculation = db.query(Calculation).filter(
        Calculation.id == calc_uuid,
        Calculation.user_id == current_user.id
    ).first()
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found.")

    if calculation_update.inputs is not None:
        calculation.inputs = calculation_update.inputs
        calculation.result = calculation.get_result()

    calculation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(calculation)
    return calculation


# Delete a Calculation
@app.delete("/calculations/{calc_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["calculations"])
def delete_calculation(
    calc_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a calculation by its UUID, if it belongs to the current user.
    """
    try:
        calc_uuid = UUID(calc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid calculation id format.")

    calculation = db.query(Calculation).filter(
        Calculation.id == calc_uuid,
        Calculation.user_id == current_user.id
    ).first()
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found.")

    db.delete(calculation)
    db.commit()
    return None


# ------------------------------------------------------------------------------
# Car CRUD Endpoints
# ------------------------------------------------------------------------------
@app.post("/cars", response_model=CarResponse, status_code=status.HTTP_201_CREATED, tags=["cars"])
def create_car(
    car: CarCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new car for the authenticated user."""
    new_car = Car(
        user_id=current_user.id,
        year=car.year,
        make=car.make,
        model=car.model,
        trim=car.trim,
        vin=car.vin
    )
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car


@app.get("/cars", response_model=List[CarResponse], tags=["cars"])
def get_user_cars(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all cars for the authenticated user."""
    cars = db.query(Car).filter(Car.user_id == current_user.id).all()
    return cars


@app.post("/cars/recommendations", response_model=CarRecommendationResponse, tags=["cars"])
def get_car_recommendations(
    request: CarRecommendationRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Get AI-powered car recommendations based on preferences.
    
    This endpoint provides intelligent car suggestions based on:
    - Budget range
    - Preferred body styles (sedan, SUV, truck, etc.)
    - Year range
    - Brands/makes
    - Desired features
    - And more...
    
    Returns a list of recommended cars with pros, cons, and confidence scores.
    """
    from app.services.car_recommendations import CarRecommendationService
    
    return CarRecommendationService.generate_recommendations(request)


@app.post("/cars/live-listings", response_model=LiveListingResponse, tags=["cars"])
def search_live_listings(
    search: LiveListingSearch,
    current_user = Depends(get_current_active_user)
):
    """
    Search for real-time car listings from multiple sources.
    
    This endpoint aggregates live listings from popular car shopping sites including:
    - CarGurus
    - Autotrader
    - Cars.com
    - TrueCar
    - eBay Motors
    
    Search by:
    - Make/Model
    - Year range
    - Price range
    - Maximum mileage
    - Location (ZIP code + radius)
    
    Returns actual listings currently for sale with prices, photos, and dealer info.
    """
    from app.services.live_listings import LiveListingService
    
    return LiveListingService.search_listings(search)


@app.get("/cars/{car_id}", response_model=CarResponse, tags=["cars"])
def get_car(
    car_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific car by ID (must be owned by authenticated user)."""
    try:
        car_uuid = UUID(car_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid car ID format")
    
    car = db.query(Car).filter(Car.id == car_uuid, Car.user_id == current_user.id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    return car


@app.patch("/cars/{car_id}", response_model=CarResponse, tags=["cars"])
def update_car(
    car_id: str,
    car_update: CarUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a car (must be owned by authenticated user)."""
    try:
        car_uuid = UUID(car_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid car ID format")
    
    car = db.query(Car).filter(Car.id == car_uuid, Car.user_id == current_user.id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    # Update only provided fields
    update_data = car_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(car, field, value)
    
    db.commit()
    db.refresh(car)
    return car


@app.delete("/cars/{car_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["cars"])
def delete_car(
    car_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a car (must be owned by authenticated user). Cascade deletes all associated listings."""
    try:
        car_uuid = UUID(car_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid car ID format")
    
    car = db.query(Car).filter(Car.id == car_uuid, Car.user_id == current_user.id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    db.delete(car)
    db.commit()
    return None


# ------------------------------------------------------------------------------
# VIN Decode Endpoint
# ------------------------------------------------------------------------------
@app.get("/vin/{vin}", response_model=VINDecodeResponse, tags=["vin"])
def decode_vin(vin: str):
    """
    Decode a VIN using the NHTSA (National Highway Traffic Safety Administration) API.
    
    This endpoint calls the external NHTSA VIN decoder API to retrieve vehicle
    information including year, make, model, and trim.
    
    The NHTSA API is a free public service provided by the U.S. government.
    
    Args:
        vin: Vehicle Identification Number (must be 17 characters)
        
    Returns:
        VINDecodeResponse with year, make, model, trim (all optional)
        
    Raises:
        400: Invalid VIN format (must be 17 characters)
        502: External NHTSA API request failed (timeout, network error, etc.)
        
    Note:
        This endpoint does NOT require authentication - it's a public utility.
    """
    import httpx
    
    # Validate VIN format
    if len(vin) != 17:
        raise HTTPException(
            status_code=400,
            detail="VIN must be exactly 17 characters"
        )
    
    # Call the NHTSA API using our service
    try:
        result = VINDecoderService.decode_vin_sync(vin)
        return VINDecodeResponse(**result)
        
    except httpx.TimeoutException as e:
        raise HTTPException(
            status_code=502,
            detail=f"NHTSA API request timed out. Please try again later. ({str(e)})"
        )
    
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to connect to NHTSA API. Please try again later. ({str(e)})"
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=502,
            detail=f"NHTSA API returned invalid data. ({str(e)})"
        )
    
    except Exception as e:
        # Catch-all for unexpected errors
        raise HTTPException(
            status_code=502,
            detail=f"Unexpected error while decoding VIN. Please try again later. ({str(e)})"
        )


# ------------------------------------------------------------------------------
# Car Comparison Endpoint
# ------------------------------------------------------------------------------
@app.get("/cars/{car_id}/compare", response_model=CarCompareStats, tags=["cars"])
def compare_car_listings(
    car_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Compute comparison statistics from all listings for a specific car.
    
    This endpoint calculates server-side statistics without requiring additional
    database tables:
    - count: Total number of listings
    - min_price: Lowest listing price
    - max_price: Highest listing price
    - avg_price: Average listing price
    - avg_price_per_mile: Average price per mile (only for listings with mileage)
    - best_deal_listing_id: Listing with lowest price (tie-breaker: lowest mileage)
    
    Ownership enforcement:
    - Car must belong to the authenticated user
    
    Args:
        car_id: UUID of the car
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        CarCompareStats with computed statistics
        
    Raises:
        400: Invalid car ID format
        404: Car not found or doesn't belong to user
    """
    try:
        car_uuid = UUID(car_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid car id format.")
    
    # Verify car exists and belongs to current user
    car = db.query(Car).filter(
        Car.id == car_uuid,
        Car.user_id == current_user.id
    ).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found.")
    
    # Get all listings for this car
    listings = db.query(Listing).filter(
        Listing.car_id == car_uuid
    ).all()
    
    # Compute statistics
    count = len(listings)
    
    if count == 0:
        # No listings - return zeros/nulls
        return CarCompareStats(
            count=0,
            min_price=None,
            max_price=None,
            avg_price=None,
            avg_price_per_mile=None,
            best_deal_listing_id=None
        )
    
    # Extract prices
    prices = [float(listing.price) for listing in listings]  # type: ignore
    min_price = min(prices)
    max_price = max(prices)
    avg_price = sum(prices) / count
    
    # Compute average price per mile (only for listings with mileage)
    listings_with_mileage = [
        listing for listing in listings 
        if listing.mileage is not None and listing.mileage > 0  # type: ignore
    ]
    if listings_with_mileage:
        price_per_mile_values = [
            float(listing.price) / listing.mileage  # type: ignore
            for listing in listings_with_mileage
        ]
        avg_price_per_mile = sum(price_per_mile_values) / len(price_per_mile_values)
    else:
        avg_price_per_mile = None
    
    # Find best deal: lowest price, tie-breaker is lowest mileage
    # Sort by price first, then by mileage (treating None as infinity)
    best_deal = sorted(
        listings,
        key=lambda listing: (
            float(listing.price),  # type: ignore
            listing.mileage if listing.mileage is not None else float('inf')
        )
    )[0]
    
    return CarCompareStats(
        count=count,
        min_price=round(min_price, 2),
        max_price=round(max_price, 2),
        avg_price=round(avg_price, 2),
        avg_price_per_mile=round(avg_price_per_mile, 2) if avg_price_per_mile else None,  # type: ignore
        best_deal_listing_id=best_deal.id  # type: ignore
    )


# ------------------------------------------------------------------------------
# Listings Endpoints (nested under /cars/{car_id}/listings)
# ------------------------------------------------------------------------------
# Browse / List Listings for a Specific Car
@app.get("/cars/{car_id}/listings", response_model=List[ListingResponse], tags=["listings"])
def list_listings_for_car(
    car_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all listings for a specific car owned by the current user.
    
    This endpoint enforces ownership: the car must belong to the authenticated user.
    
    Args:
        car_id: UUID of the car
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        List of listings for the specified car
        
    Raises:
        400: Invalid car ID format
        404: Car not found or doesn't belong to user
    """
    try:
        car_uuid = UUID(car_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid car id format.")
    
    # Verify car exists and belongs to current user
    car = db.query(Car).filter(
        Car.id == car_uuid,
        Car.user_id == current_user.id
    ).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found.")
    
    # Get all listings for this car
    listings = db.query(Listing).filter(
        Listing.car_id == car_uuid
    ).all()
    
    return listings


# Create a New Listing for a Car
@app.post(
    "/cars/{car_id}/listings",
    response_model=ListingResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["listings"]
)
def create_listing_for_car(
    car_id: str,
    listing_data: ListingCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new listing for a specific car.
    
    This endpoint enforces ownership:
    - The car must belong to the authenticated user
    - The car_id in the URL must match the car_id in the request body
    
    Args:
        car_id: UUID of the car (from URL path)
        listing_data: Listing data including car_id, price, mileage, etc.
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        The newly created listing
        
    Raises:
        400: Invalid car ID format or car_id mismatch
        404: Car not found or doesn't belong to user
    """
    try:
        car_uuid = UUID(car_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid car id format.")
    
    # Verify car_id in URL matches car_id in body
    if listing_data.car_id != car_uuid:
        raise HTTPException(
            status_code=400, 
            detail="Car ID in URL must match car_id in request body."
        )
    
    # Verify car exists and belongs to current user
    car = db.query(Car).filter(
        Car.id == car_uuid,
        Car.user_id == current_user.id
    ).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found.")
    
    # Create the new listing
    try:
        new_listing = Listing(
            car_id=car_uuid,
            user_id=current_user.id,
            price=listing_data.price,
            mileage=listing_data.mileage,
            source=listing_data.source,
            url=listing_data.url,
            location=listing_data.location
        )
        
        db.add(new_listing)
        db.commit()
        db.refresh(new_listing)
        return new_listing
        
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Read / Retrieve a Specific Listing
@app.get(
    "/cars/{car_id}/listings/{listing_id}",
    response_model=ListingResponse,
    tags=["listings"]
)
def get_listing(
    car_id: str,
    listing_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific listing for a car.
    
    This endpoint enforces ownership:
    - The car must belong to the authenticated user
    - The listing must belong to the specified car
    
    Args:
        car_id: UUID of the car
        listing_id: UUID of the listing
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        The requested listing
        
    Raises:
        400: Invalid car or listing ID format
        404: Car or listing not found, or doesn't belong to user
    """
    try:
        car_uuid = UUID(car_id)
        listing_uuid = UUID(listing_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid car or listing id format.")
    
    # Verify car exists and belongs to current user
    car = db.query(Car).filter(
        Car.id == car_uuid,
        Car.user_id == current_user.id
    ).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found.")
    
    # Get the listing (must belong to this car and this user)
    listing = db.query(Listing).filter(
        Listing.id == listing_uuid,
        Listing.car_id == car_uuid,
        Listing.user_id == current_user.id
    ).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found.")
    
    return listing


# Update a Listing (PATCH for partial updates)
@app.patch(
    "/cars/{car_id}/listings/{listing_id}",
    response_model=ListingResponse,
    tags=["listings"]
)
def update_listing(
    car_id: str,
    listing_id: str,
    listing_update: ListingUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a specific listing (partial update).
    
    This endpoint enforces ownership:
    - The car must belong to the authenticated user
    - The listing must belong to the specified car and user
    
    Only provided fields will be updated. The car_id cannot be changed.
    
    Args:
        car_id: UUID of the car
        listing_id: UUID of the listing
        listing_update: Fields to update (all optional)
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        The updated listing
        
    Raises:
        400: Invalid car or listing ID format
        404: Car or listing not found, or doesn't belong to user
    """
    try:
        car_uuid = UUID(car_id)
        listing_uuid = UUID(listing_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid car or listing id format.")
    
    # Verify car exists and belongs to current user
    car = db.query(Car).filter(
        Car.id == car_uuid,
        Car.user_id == current_user.id
    ).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found.")
    
    # Get the listing (must belong to this car and this user)
    listing = db.query(Listing).filter(
        Listing.id == listing_uuid,
        Listing.car_id == car_uuid,
        Listing.user_id == current_user.id
    ).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found.")
    
    # Update only the fields that were provided
    update_data = listing_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(listing, field, value)
    
    listing.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(listing)
    return listing


# Delete a Listing
@app.delete(
    "/cars/{car_id}/listings/{listing_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["listings"]
)
def delete_listing(
    car_id: str,
    listing_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific listing.
    
    This endpoint enforces ownership:
    - The car must belong to the authenticated user
    - The listing must belong to the specified car and user
    
    Args:
        car_id: UUID of the car
        listing_id: UUID of the listing
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        None (204 No Content)
        
    Raises:
        400: Invalid car or listing ID format
        404: Car or listing not found, or doesn't belong to user
    """
    try:
        car_uuid = UUID(car_id)
        listing_uuid = UUID(listing_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid car or listing id format.")
    
    # Verify car exists and belongs to current user
    car = db.query(Car).filter(
        Car.id == car_uuid,
        Car.user_id == current_user.id
    ).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found.")
    
    # Get the listing (must belong to this car and this user)
    listing = db.query(Listing).filter(
        Listing.id == listing_uuid,
        Listing.car_id == car_uuid,
        Listing.user_id == current_user.id
    ).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found.")
    
    db.delete(listing)
    db.commit()
    return None


# ------------------------------------------------------------------------------
# Main Block to Run the Server
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, log_level="info")
