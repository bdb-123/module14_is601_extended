# app/models/car.py
"""
Car Model Module

This module defines the Car model for the CarCompare application.
A Car represents a vehicle owned by a user and can have multiple listings.

The Car model follows the same patterns as the User and Calculation models:
- UUID primary key for security and uniqueness
- Foreign key relationship to User
- Timezone-aware timestamps
- Cascade deletion when user is deleted
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
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


class Car(Base):
    """
    Car model representing a vehicle owned by a user.
    
    A car can have multiple listings across different platforms or time periods.
    Cars are owned by users and will be deleted if the user is deleted (cascade).
    
    Attributes:
        id: Unique identifier (UUID)
        user_id: Foreign key to the owning user
        vin: Vehicle Identification Number (optional)
        year: Manufacturing year
        make: Manufacturer (e.g., Toyota, Honda)
        model: Model name (e.g., Camry, Accord)
        trim: Trim level (e.g., LX, EX, Sport) - optional
        created_at: Timestamp when the car was added
        updated_at: Timestamp when the car was last modified
    """
    
    __tablename__ = "cars"
    
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
    
    # Car identification
    vin = Column(
        String(17),  # VINs are standardized at 17 characters
        nullable=True,
        unique=True,  # VINs should be unique if provided
        index=True
    )
    
    # Car details
    year = Column(Integer, nullable=False)
    make = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=False)
    trim = Column(String(100), nullable=True)
    
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
        back_populates="cars"
    )
    
    listings = relationship(
        "Listing",
        back_populates="car",
        cascade="all, delete-orphan"  # Delete listings when car is deleted
    )
    
    def __repr__(self):
        """String representation of the car."""
        return f"<Car(id={self.id}, year={self.year}, make={self.make}, model={self.model})>"
    
    def __str__(self):
        """Human-readable string representation."""
        trim_info = f" {self.trim}" if self.trim is not None else ""
        return f"{self.year} {self.make} {self.model}{trim_info}"
    
    def update(self, **kwargs):
        """
        Update car attributes and ensure updated_at is refreshed.
        
        Args:
            **kwargs: Attributes to update
            
        Returns:
            Car: The updated car instance
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = utcnow()
        return self
