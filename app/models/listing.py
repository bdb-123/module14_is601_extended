# app/models/listing.py
"""
Listing Model Module

This module defines the Listing model for the CarCompare application.
A Listing represents a marketplace posting for a specific car.

The Listing model follows the same patterns as other models in the project:
- UUID primary key for security and uniqueness
- Foreign key relationships to both User and Car
- Timezone-aware timestamps
- Cascade deletion when user or car is deleted
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.database import Base


def utcnow():
    """
    Helper function to get current UTC datetime with timezone information.
    
    Returns:
        datetime: Current UTC time with timezone info
    """
    return datetime.now(timezone.utc)


class Listing(Base):
    """
    Listing model representing a marketplace posting for a car.
    
    A listing belongs to both a user (who created it) and a car (being listed).
    Listings track price, mileage, source platform, and location information.
    
    Attributes:
        id: Unique identifier (UUID)
        user_id: Foreign key to the user who created the listing
        car_id: Foreign key to the car being listed
        price: Listing price (can be float for decimal prices)
        mileage: Current mileage of the car (optional)
        source: Platform/source of the listing (e.g., "Craigslist", "AutoTrader")
        url: URL to the listing (optional)
        location: Geographic location of the listing (optional)
        created_at: Timestamp when the listing was created
        updated_at: Timestamp when the listing was last modified
    """
    
    __tablename__ = "listings"
    
    # Primary key
    id = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True
    )
    
    # Foreign key to user
    user_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True  # Index for faster queries filtering by user
    )
    
    # Foreign key to car
    car_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey('cars.id', ondelete='CASCADE'),
        nullable=False,
        index=True  # Index for faster queries filtering by car
    )
    
    # Listing details
    price = Column(Float, nullable=False)  # Using Float to support decimal prices
    
    mileage = Column(Integer, nullable=True)
    
    source = Column(
        String(100),
        nullable=False,
        index=True  # Index for filtering by source platform
    )
    
    url = Column(String, nullable=True)  # No length limit for URLs
    
    location = Column(String(200), nullable=True)
    
    # Timestamps - All timezone-aware
    created_at = Column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="listings"
    )
    
    car = relationship(
        "Car",
        back_populates="listings"
    )
    
    def __repr__(self):
        """String representation of the listing."""
        return f"<Listing(id={self.id}, car_id={self.car_id}, price=${self.price}, source={self.source})>"
    
    def __str__(self):
        """Human-readable string representation."""
        mileage_info = f" - {self.mileage:,} miles" if self.mileage is not None else ""
        location_info = f" in {self.location}" if self.location is not None else ""
        return f"${self.price:,.2f}{mileage_info} ({self.source}){location_info}"
    
    def update(self, **kwargs):
        """
        Update listing attributes and ensure updated_at is refreshed.
        
        Args:
            **kwargs: Attributes to update
            
        Returns:
            Listing: The updated listing instance
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = utcnow()
        return self
