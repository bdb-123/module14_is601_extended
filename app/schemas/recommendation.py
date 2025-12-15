"""
Pydantic schemas for car recommendation requests and responses.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class CarRecommendationRequest(BaseModel):
    """Schema for car recommendation request."""
    
    budget_min: Optional[float] = Field(None, description="Minimum budget", ge=0)
    budget_max: Optional[float] = Field(None, description="Maximum budget", ge=0)
    body_styles: Optional[List[str]] = Field(None, description="Preferred body styles (e.g., sedan, suv, truck)")
    year_min: Optional[int] = Field(None, description="Minimum year", ge=1900)
    year_max: Optional[int] = Field(None, description="Maximum year", le=2030)
    brands: Optional[List[str]] = Field(None, description="Preferred brands/makes")
    mileage_max: Optional[int] = Field(None, description="Maximum acceptable mileage", ge=0)
    features: Optional[List[str]] = Field(None, description="Desired features (e.g., AWD, sunroof, leather)")
    fuel_type: Optional[str] = Field(None, description="Fuel type preference (gas, electric, hybrid)")
    transmission: Optional[str] = Field(None, description="Transmission preference (automatic, manual)")
    additional_notes: Optional[str] = Field(None, description="Any additional preferences or requirements")
    
    @field_validator('budget_max')
    @classmethod
    def validate_budget_range(cls, v, info):
        """Ensure budget_max >= budget_min if both provided."""
        if v is not None and info.data.get('budget_min') is not None:
            if v < info.data['budget_min']:
                raise ValueError("budget_max must be greater than or equal to budget_min")
        return v
    
    @field_validator('year_max')
    @classmethod
    def validate_year_range(cls, v, info):
        """Ensure year_max >= year_min if both provided."""
        if v is not None and info.data.get('year_min') is not None:
            if v < info.data['year_min']:
                raise ValueError("year_max must be greater than or equal to year_min")
        return v


class CarRecommendation(BaseModel):
    """Schema for a single car recommendation."""
    
    year: int = Field(..., description="Year of the car")
    make: str = Field(..., description="Make/brand of the car")
    model: str = Field(..., description="Model name")
    trim: Optional[str] = Field(None, description="Trim level")
    estimated_price: Optional[float] = Field(None, description="Estimated market price")
    image_url: Optional[str] = Field(None, description="URL to car image")
    reason: str = Field(..., description="Why this car is recommended")
    pros: List[str] = Field(default_factory=list, description="Pros of this car")
    cons: List[str] = Field(default_factory=list, description="Cons of this car")
    confidence_score: float = Field(..., description="Confidence score 0-1", ge=0, le=1)


class CarRecommendationResponse(BaseModel):
    """Schema for car recommendation response."""
    
    recommendations: List[CarRecommendation] = Field(..., description="List of recommended cars")
    total_count: int = Field(..., description="Total number of recommendations")
    search_summary: str = Field(..., description="Summary of the search criteria")
