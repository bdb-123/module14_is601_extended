"""
Listing Schemas Module

This module defines the Pydantic schemas for validation and serialization of listing data.
It includes schemas for:
- Base listing data (common fields)
- Creating new listings
- Updating existing listings
- Returning listing responses

The schemas use Pydantic's validation system to ensure data integrity and provide
clear error messages when validation fails.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime


class ListingBase(BaseModel):
    """
    Base schema for listing data.
    
    This schema defines the common fields that all listing operations share:
    - car_id: Foreign key to the car being listed
    - price: Listing price (must be positive)
    - mileage: Current mileage (optional, must be non-negative if provided)
    - source: Platform/source of the listing (e.g., "Craigslist", "AutoTrader")
    - url: URL to the listing (optional)
    - location: Geographic location (optional)
    
    It also implements validation rules to ensure data integrity.
    """
    car_id: UUID = Field(
        ...,  # Required field
        description="UUID of the car being listed",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    price: float = Field(
        ...,  # Required field
        description="Listing price (must be positive)",
        example=25000.00,
        gt=0  # Greater than 0
    )
    mileage: Optional[int] = Field(
        None,  # Optional field
        description="Current mileage of the car",
        example=45000,
        ge=0  # Greater than or equal to 0
    )
    source: str = Field(
        ...,  # Required field
        description="Platform/source of the listing",
        example="Craigslist",
        min_length=1,
        max_length=100
    )
    url: Optional[str] = Field(
        None,  # Optional field
        description="URL to the listing",
        example="https://example.com/listing/12345",
        max_length=2000
    )
    location: Optional[str] = Field(
        None,  # Optional field
        description="Geographic location of the listing",
        example="San Francisco, CA",
        max_length=200
    )

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        """
        Validates that the price is positive and reasonable.
        
        Ensures the price is:
        - Greater than 0
        - Less than a reasonable maximum (e.g., $10 million)
        
        Args:
            v: The price value to validate
            
        Returns:
            float: The validated price
            
        Raises:
            ValueError: If price is invalid
        """
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        if v > 10_000_000:  # $10 million seems like a reasonable upper bound
            raise ValueError("Price cannot exceed $10,000,000")
        return round(v, 2)  # Round to 2 decimal places for currency

    @field_validator("mileage")
    @classmethod
    def validate_mileage(cls, v):
        """
        Validates that the mileage is non-negative if provided.
        
        Ensures the mileage is:
        - Greater than or equal to 0
        - Less than a reasonable maximum (e.g., 1 million miles)
        
        Args:
            v: The mileage value to validate
            
        Returns:
            int: The validated mileage, or None
            
        Raises:
            ValueError: If mileage is invalid
        """
        if v is None:
            return v
        if v < 0:
            raise ValueError("Mileage cannot be negative")
        if v > 1_000_000:  # 1 million miles seems like a reasonable upper bound
            raise ValueError("Mileage cannot exceed 1,000,000 miles")
        return v

    @field_validator("source", "location")
    @classmethod
    def strip_whitespace(cls, v):
        """
        Strip leading/trailing whitespace from string fields.
        
        Args:
            v: The string value to clean
            
        Returns:
            str: The cleaned string, or None if the input was None
        """
        if v is None:
            return v
        return v.strip()

    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        """
        Validates the URL format if provided.
        
        Args:
            v: The URL value to validate
            
        Returns:
            str: The validated URL, or None
            
        Raises:
            ValueError: If URL is invalid
        """
        if v is None:
            return v
        
        # Strip whitespace
        v = v.strip()
        
        # Basic URL validation - should start with http:// or https://
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        
        return v

    model_config = ConfigDict(
        # Allow conversion from SQLAlchemy models to Pydantic models
        from_attributes=True,
        
        # Add examples to the OpenAPI schema for better API documentation
        json_schema_extra={
            "examples": [
                {
                    "car_id": "123e4567-e89b-12d3-a456-426614174000",
                    "price": 25000.00,
                    "mileage": 45000,
                    "source": "Craigslist",
                    "url": "https://sfbay.craigslist.org/sfc/cto/d/listing/12345.html",
                    "location": "San Francisco, CA"
                },
                {
                    "car_id": "987fcdeb-51a2-43f7-8b6a-123456789abc",
                    "price": 18500.00,
                    "mileage": None,
                    "source": "AutoTrader",
                    "url": None,
                    "location": "Los Angeles, CA"
                }
            ]
        }
    )


class ListingCreate(ListingBase):
    """
    Schema for creating a new Listing.
    
    This extends the base schema. In the API, the user_id is automatically
    obtained from the authentication token, so it's not included here.
    The car_id is validated to ensure it belongs to the authenticated user.
    """
    pass


class ListingUpdate(BaseModel):
    """
    Schema for updating an existing Listing.
    
    All fields are optional to allow partial updates. Clients can send
    only the fields they want to update.
    
    Note: car_id cannot be updated after creation (listings are tied to a specific car).
    """
    price: Optional[float] = Field(
        None,
        description="Updated listing price",
        example=24500.00,
        gt=0
    )
    mileage: Optional[int] = Field(
        None,
        description="Updated mileage",
        example=46000,
        ge=0
    )
    source: Optional[str] = Field(
        None,
        description="Updated source platform",
        example="AutoTrader",
        min_length=1,
        max_length=100
    )
    url: Optional[str] = Field(
        None,
        description="Updated URL to the listing",
        example="https://example.com/listing/12345",
        max_length=2000
    )
    location: Optional[str] = Field(
        None,
        description="Updated location",
        example="Oakland, CA",
        max_length=200
    )

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        """Validate price if provided."""
        if v is None:
            return v
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        if v > 10_000_000:
            raise ValueError("Price cannot exceed $10,000,000")
        return round(v, 2)

    @field_validator("mileage")
    @classmethod
    def validate_mileage(cls, v):
        """Validate mileage if provided."""
        if v is None:
            return v
        if v < 0:
            raise ValueError("Mileage cannot be negative")
        if v > 1_000_000:
            raise ValueError("Mileage cannot exceed 1,000,000 miles")
        return v

    @field_validator("source", "location")
    @classmethod
    def strip_whitespace(cls, v):
        """Strip whitespace if provided."""
        if v is None:
            return v
        return v.strip()

    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        """Validate URL if provided."""
        if v is None:
            return v
        v = v.strip()
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "price": 24000.00,
                "mileage": 47000
            }
        }
    )


class ListingResponse(ListingBase):
    """
    Schema for listing response data.
    
    This extends the base schema with additional fields that are populated
    by the database after creation:
    - id: Unique identifier (UUID)
    - user_id: Foreign key to the user who created the listing
    - created_at: Timestamp when the listing was created
    - updated_at: Timestamp when the listing was last updated
    """
    id: UUID = Field(
        ...,
        description="Unique identifier for the listing",
        example="abc12345-6789-def0-1234-56789abcdef0"
    )
    user_id: UUID = Field(
        ...,
        description="UUID of the user who created this listing",
        example="987fcdeb-51a2-43f7-8b6a-123456789abc"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the listing was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the listing was last updated"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "abc12345-6789-def0-1234-56789abcdef0",
                "user_id": "987fcdeb-51a2-43f7-8b6a-123456789abc",
                "car_id": "123e4567-e89b-12d3-a456-426614174000",
                "price": 25000.00,
                "mileage": 45000,
                "source": "Craigslist",
                "url": "https://sfbay.craigslist.org/sfc/cto/d/listing/12345.html",
                "location": "San Francisco, CA",
                "created_at": "2023-01-15T10:30:00Z",
                "updated_at": "2023-01-15T10:30:00Z"
            }
        }
    )
