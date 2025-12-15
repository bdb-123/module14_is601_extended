"""
Car Schemas Module

This module defines the Pydantic schemas for validation and serialization of car data.
It includes schemas for:
- Base car data (common fields)
- Creating new cars
- Updating existing cars
- Returning car responses
- Car comparison statistics
- VIN decode responses

The schemas use Pydantic's validation system to ensure data integrity and provide
clear error messages when validation fails.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime


class CarBase(BaseModel):
    """
    Base schema for car data.
    
    This schema defines the common fields that all car operations share:
    - year: Manufacturing year of the vehicle
    - make: Manufacturer (e.g., Toyota, Honda, Ford)
    - model: Model name (e.g., Camry, Accord, F-150)
    - trim: Trim level (e.g., LX, EX, Sport) - optional
    - vin: Vehicle Identification Number - optional
    
    It also implements validation rules to ensure data integrity.
    """
    year: int = Field(
        ...,  # Required field
        description="Manufacturing year of the vehicle",
        example=2020,
        ge=1900,  # Greater than or equal to 1900
        le=2030   # Less than or equal to 2030 (accounts for future models)
    )
    make: str = Field(
        ...,  # Required field
        description="Manufacturer of the vehicle",
        example="Toyota",
        min_length=1,
        max_length=100
    )
    model: str = Field(
        ...,  # Required field
        description="Model name of the vehicle",
        example="Camry",
        min_length=1,
        max_length=100
    )
    trim: Optional[str] = Field(
        None,  # Optional field
        description="Trim level of the vehicle (e.g., LX, EX, Sport)",
        example="SE",
        max_length=100
    )
    vin: Optional[str] = Field(
        None,  # Optional field
        description="Vehicle Identification Number (17 characters)",
        example="1HGBH41JXMN109186",
        min_length=17,
        max_length=17
    )

    @field_validator("year")
    @classmethod
    def validate_year(cls, v):
        """
        Validates that the year is reasonable.
        
        Ensures the year is between 1900 and 2030 to prevent:
        - Historical vehicles before cars were mass-produced
        - Far-future model years that are unrealistic
        
        Args:
            v: The year value to validate
            
        Returns:
            int: The validated year
            
        Raises:
            ValueError: If year is outside the reasonable range
        """
        current_year = datetime.now().year
        if v < 1900:
            raise ValueError("Year must be 1900 or later")
        if v > current_year + 2:  # Allow up to 2 years in the future for upcoming models
            raise ValueError(f"Year cannot be more than {current_year + 2}")
        return v

    @field_validator("vin")
    @classmethod
    def validate_vin(cls, v):
        """
        Validates the VIN format if provided.
        
        VINs are standardized at 17 characters and should not contain
        certain letters (I, O, Q) to avoid confusion with numbers.
        
        Args:
            v: The VIN value to validate
            
        Returns:
            str: The validated and uppercase VIN
            
        Raises:
            ValueError: If VIN format is invalid
        """
        if v is None:
            return v
        
        # Convert to uppercase for consistency
        v = v.upper()
        
        # Check length
        if len(v) != 17:
            raise ValueError("VIN must be exactly 17 characters")
        
        # Check for invalid characters (I, O, Q are not used in VINs)
        if any(char in v for char in ['I', 'O', 'Q']):
            raise ValueError("VIN cannot contain letters I, O, or Q")
        
        # Check that it contains only alphanumeric characters
        if not v.isalnum():
            raise ValueError("VIN must contain only letters and numbers")
        
        return v

    @field_validator("make", "model", "trim")
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

    model_config = ConfigDict(
        # Allow conversion from SQLAlchemy models to Pydantic models
        from_attributes=True,
        
        # Add examples to the OpenAPI schema for better API documentation
        json_schema_extra={
            "examples": [
                {
                    "year": 2020,
                    "make": "Toyota",
                    "model": "Camry",
                    "trim": "SE",
                    "vin": "1HGBH41JXMN109186"
                },
                {
                    "year": 2019,
                    "make": "Honda",
                    "model": "Accord",
                    "trim": "EX-L",
                    "vin": None
                }
            ]
        }
    )


class CarCreate(CarBase):
    """
    Schema for creating a new Car.
    
    This extends the base schema. In the API, the user_id is automatically
    obtained from the authentication token, so it's not included here.
    """
    pass


class CarUpdate(BaseModel):
    """
    Schema for updating an existing Car.
    
    All fields are optional to allow partial updates. Clients can send
    only the fields they want to update.
    
    Note: If a field is provided, it must pass the same validation as CarBase.
    """
    year: Optional[int] = Field(
        None,
        description="Manufacturing year of the vehicle",
        example=2020,
        ge=1900,
        le=2030
    )
    make: Optional[str] = Field(
        None,
        description="Manufacturer of the vehicle",
        example="Toyota",
        min_length=1,
        max_length=100
    )
    model: Optional[str] = Field(
        None,
        description="Model name of the vehicle",
        example="Camry",
        min_length=1,
        max_length=100
    )
    trim: Optional[str] = Field(
        None,
        description="Trim level of the vehicle",
        example="SE",
        max_length=100
    )
    vin: Optional[str] = Field(
        None,
        description="Vehicle Identification Number (17 characters)",
        example="1HGBH41JXMN109186",
        min_length=17,
        max_length=17
    )

    @field_validator("year")
    @classmethod
    def validate_year(cls, v):
        """Validate year if provided."""
        if v is None:
            return v
        current_year = datetime.now().year
        if v < 1900:
            raise ValueError("Year must be 1900 or later")
        if v > current_year + 2:
            raise ValueError(f"Year cannot be more than {current_year + 2}")
        return v

    @field_validator("vin")
    @classmethod
    def validate_vin(cls, v):
        """Validate VIN if provided."""
        if v is None:
            return v
        v = v.upper()
        if len(v) != 17:
            raise ValueError("VIN must be exactly 17 characters")
        if any(char in v for char in ['I', 'O', 'Q']):
            raise ValueError("VIN cannot contain letters I, O, or Q")
        if not v.isalnum():
            raise ValueError("VIN must contain only letters and numbers")
        return v

    @field_validator("make", "model", "trim")
    @classmethod
    def strip_whitespace(cls, v):
        """Strip whitespace if provided."""
        if v is None:
            return v
        return v.strip()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "year": 2021,
                "trim": "Limited"
            }
        }
    )


class CarResponse(CarBase):
    """
    Schema for car response data.
    
    This extends the base schema with additional fields that are populated
    by the database after creation:
    - id: Unique identifier (UUID)
    - user_id: Foreign key to the owning user
    - created_at: Timestamp when the car was created
    - updated_at: Timestamp when the car was last updated
    """
    id: UUID = Field(
        ...,
        description="Unique identifier for the car",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    user_id: UUID = Field(
        ...,
        description="UUID of the user who owns this car",
        example="987fcdeb-51a2-43f7-8b6a-123456789abc"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the car was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the car was last updated"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987fcdeb-51a2-43f7-8b6a-123456789abc",
                "year": 2020,
                "make": "Toyota",
                "model": "Camry",
                "trim": "SE",
                "vin": "1HGBH41JXMN109186",
                "created_at": "2023-01-15T10:30:00Z",
                "updated_at": "2023-01-15T10:30:00Z"
            }
        }
    )


class CarCompareStats(BaseModel):
    """
    Schema for car comparison statistics computed from listings.
    
    This schema contains aggregated data calculated server-side from
    all listings associated with a car:
    - count: Total number of listings
    - min_price: Lowest listing price
    - max_price: Highest listing price
    - avg_price: Average listing price
    - avg_price_per_mile: Average price per mile (only if mileage data exists)
    - best_deal_listing_id: ID of the best deal (lowest price, tie-breaker: lowest mileage)
    
    All statistics are computed on-the-fly without requiring additional database tables.
    """
    count: int = Field(
        ...,
        description="Total number of listings for this car",
        example=5,
        ge=0
    )
    min_price: Optional[float] = Field(
        None,
        description="Lowest listing price (None if no listings)",
        example=23000.00
    )
    max_price: Optional[float] = Field(
        None,
        description="Highest listing price (None if no listings)",
        example=27500.00
    )
    avg_price: Optional[float] = Field(
        None,
        description="Average listing price (None if no listings)",
        example=25100.00
    )
    avg_price_per_mile: Optional[float] = Field(
        None,
        description="Average price per mile for listings with mileage data (None if no mileage data)",
        example=0.56
    )
    best_deal_listing_id: Optional[UUID] = Field(
        None,
        description="UUID of the best deal listing (lowest price, tie-breaker: lowest mileage). None if no listings.",
        example="abc12345-6789-def0-1234-56789abcdef0"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "count": 5,
                "min_price": 23000.00,
                "max_price": 27500.00,
                "avg_price": 25100.00,
                "avg_price_per_mile": 0.56,
                "best_deal_listing_id": "abc12345-6789-def0-1234-56789abcdef0"
            }
        }
    )


class VINDecodeResponse(BaseModel):
    """
    Schema for VIN decode API response.
    
    This schema represents the data returned from the NHTSA VIN decoder API.
    All fields are optional since the API may not return complete information
    for all VINs.
    
    The data is sourced from the NHTSA (National Highway Traffic Safety Administration)
    public API and provides basic vehicle identification information.
    """
    year: Optional[str] = Field(
        None,
        description="Model year of the vehicle",
        example="2020"
    )
    make: Optional[str] = Field(
        None,
        description="Manufacturer of the vehicle",
        example="Toyota"
    )
    model: Optional[str] = Field(
        None,
        description="Model name of the vehicle",
        example="Camry"
    )
    trim: Optional[str] = Field(
        None,
        description="Trim level or series of the vehicle",
        example="SE"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "year": "2020",
                "make": "Toyota",
                "model": "Camry",
                "trim": "SE"
            }
        }
    )
