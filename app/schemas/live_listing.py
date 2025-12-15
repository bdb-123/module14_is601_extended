"""
Pydantic schemas for live car listings from external sources.
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class LiveListingSearch(BaseModel):
    """Schema for searching live car listings."""
    
    make: Optional[str] = Field(None, description="Car make/brand (e.g., Honda, Toyota)")
    model: Optional[str] = Field(None, description="Car model (e.g., Civic, Camry)")
    year_min: Optional[int] = Field(None, description="Minimum year", ge=1990, le=2030)
    year_max: Optional[int] = Field(None, description="Maximum year", ge=1990, le=2030)
    price_min: Optional[float] = Field(None, description="Minimum price", ge=0)
    price_max: Optional[float] = Field(None, description="Maximum price", ge=0)
    mileage_max: Optional[int] = Field(None, description="Maximum mileage", ge=0)
    zip_code: Optional[str] = Field(None, description="ZIP code for location-based search")
    radius: Optional[int] = Field(50, description="Search radius in miles", ge=0, le=500)


class LiveListing(BaseModel):
    """Schema for a single live car listing from external source."""
    
    title: str = Field(..., description="Listing title")
    year: int = Field(..., description="Car year")
    make: str = Field(..., description="Car make/brand")
    model: str = Field(..., description="Car model")
    trim: Optional[str] = Field(None, description="Trim level")
    price: float = Field(..., description="Listed price")
    mileage: Optional[int] = Field(None, description="Odometer reading")
    location: Optional[str] = Field(None, description="Seller location")
    dealer_name: Optional[str] = Field(None, description="Dealer or seller name")
    url: str = Field(..., description="Link to full listing")
    image_url: Optional[str] = Field(None, description="Primary car image URL")
    source: str = Field(..., description="Source website (CarGurus, Autotrader, etc.)")
    vin: Optional[str] = Field(None, description="VIN if available")
    exterior_color: Optional[str] = Field(None, description="Exterior color")
    interior_color: Optional[str] = Field(None, description="Interior color")
    transmission: Optional[str] = Field(None, description="Transmission type")
    fuel_type: Optional[str] = Field(None, description="Fuel type")
    drivetrain: Optional[str] = Field(None, description="Drivetrain (FWD, AWD, etc.)")
    features: List[str] = Field(default_factory=list, description="Key features")
    days_listed: Optional[int] = Field(None, description="Days on market")
    price_drop: Optional[float] = Field(None, description="Recent price drop amount")
    is_certified: bool = Field(False, description="Certified pre-owned status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "2020 Honda Civic EX Sedan",
                "year": 2020,
                "make": "Honda",
                "model": "Civic",
                "trim": "EX",
                "price": 18995,
                "mileage": 45000,
                "location": "New York, NY",
                "dealer_name": "ABC Motors",
                "url": "https://example.com/listing/123",
                "image_url": "https://example.com/car.jpg",
                "source": "CarGurus",
                "exterior_color": "Silver",
                "transmission": "CVT",
                "features": ["Sunroof", "Backup Camera", "Bluetooth"]
            }
        }


class LiveListingResponse(BaseModel):
    """Schema for live listing search results."""
    
    listings: List[LiveListing] = Field(..., description="List of found listings")
    total_count: int = Field(..., description="Total number of listings found")
    search_summary: str = Field(..., description="Summary of search criteria")
    last_updated: datetime = Field(..., description="When results were fetched")
    sources: List[str] = Field(..., description="Sources that were searched")
