"""
Live Car Listings Service - Aggregates real-time car listings from multiple sources.

In production, this would integrate with:
- CarGurus API
- Autotrader API
- Cars.com API
- eBay Motors API
- Craigslist (via unofficial scraping)

For demo purposes, this generates realistic listings with actual market pricing.
"""
from typing import List
from datetime import datetime, timedelta
import random
from app.schemas.live_listing import LiveListingSearch, LiveListing, LiveListingResponse


class LiveListingService:
    """Service for fetching live car listings from external sources."""
    
    # Realistic listing data generator
    SOURCES = ["CarGurus", "Autotrader", "Cars.com", "TrueCar", "eBay Motors"]
    COLORS = ["White", "Black", "Silver", "Gray", "Blue", "Red", "Green", "Brown", "Beige"]
    TRANSMISSIONS = ["Automatic", "CVT", "Manual", "8-Speed Automatic", "6-Speed Automatic"]
    FUEL_TYPES = ["Gasoline", "Diesel", "Hybrid", "Electric", "Plug-in Hybrid"]
    DRIVETRAINS = ["FWD", "RWD", "AWD", "4WD"]
    
    DEALER_NAMES = [
        "Premium Auto Sales", "Elite Motors", "City Car Center", "AutoNation",
        "CarMax", "Carvana", "Vroom", "Highway Motors", "Best Buy Auto",
        "Metro Car Group", "Luxury Auto Gallery", "Quality Cars Inc",
        "Family Motors", "DriveTime", "Hertz Car Sales"
    ]
    
    LOCATIONS = [
        "New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX",
        "Phoenix, AZ", "Philadelphia, PA", "San Antonio, TX", "San Diego, CA",
        "Dallas, TX", "Austin, TX", "Jacksonville, FL", "Fort Worth, TX",
        "San Jose, CA", "Columbus, OH", "Charlotte, NC", "Indianapolis, IN",
        "Seattle, WA", "Denver, CO", "Boston, MA", "Portland, OR"
    ]
    
    COMMON_FEATURES = [
        "Backup Camera", "Bluetooth", "Cruise Control", "Keyless Entry",
        "Sunroof", "Leather Seats", "Heated Seats", "Navigation System",
        "Apple CarPlay", "Android Auto", "Blind Spot Monitor", "Lane Departure Warning",
        "Adaptive Cruise Control", "Power Liftgate", "Remote Start", "USB Ports",
        "Alloy Wheels", "LED Headlights", "Third Row Seating", "Parking Sensors"
    ]
    
    @staticmethod
    def search_listings(search: LiveListingSearch) -> LiveListingResponse:
        """
        Search for live car listings based on criteria.
        
        In production, this would call actual APIs and aggregate results.
        For demo, generates realistic listings with market-accurate pricing.
        """
        listings = []
        
        # Generate 10-20 realistic listings
        num_listings = random.randint(10, 20)
        
        for i in range(num_listings):
            listing = LiveListingService._generate_listing(search, i)
            if listing:
                listings.append(listing)
        
        # Sort by price (ascending)
        listings.sort(key=lambda x: x.price)
        
        # Generate search summary
        summary_parts = []
        if search.make:
            summary_parts.append(search.make)
        if search.model:
            summary_parts.append(search.model)
        if search.year_min or search.year_max:
            if search.year_min and search.year_max:
                summary_parts.append(f"{search.year_min}-{search.year_max}")
            elif search.year_min:
                summary_parts.append(f"{search.year_min}+")
            else:
                summary_parts.append(f"up to {search.year_max}")
        if search.price_max:
            summary_parts.append(f"under ${search.price_max:,.0f}")
        
        summary = " | ".join(summary_parts) if summary_parts else "All listings"
        
        return LiveListingResponse(
            listings=listings[:15],  # Return top 15
            total_count=len(listings),
            search_summary=f"Found {len(listings)} listings: {summary}",
            last_updated=datetime.utcnow(),
            sources=random.sample(LiveListingService.SOURCES, k=random.randint(3, 5))
        )
    
    @staticmethod
    def _generate_listing(search: LiveListingSearch, index: int) -> LiveListing:
        """Generate a realistic listing that matches search criteria."""
        
        # Determine make/model
        if search.make:
            make = search.make
        else:
            make = random.choice(["Honda", "Toyota", "Ford", "Chevrolet", "Nissan", "Mazda", "Subaru", "Hyundai", "Kia", "Lexus"])
        
        # Model based on make
        model_map = {
            "Honda": ["Civic", "Accord", "CR-V", "Pilot", "HR-V", "Odyssey"],
            "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Tacoma", "4Runner"],
            "Ford": ["F-150", "Escape", "Explorer", "Mustang", "Edge", "Bronco"],
            "Chevrolet": ["Silverado", "Equinox", "Malibu", "Traverse", "Tahoe", "Camaro"],
            "Nissan": ["Altima", "Rogue", "Sentra", "Pathfinder", "Murano", "Frontier"],
            "Mazda": ["Mazda3", "CX-5", "CX-30", "CX-9", "Mazda6", "MX-5 Miata"],
            "Subaru": ["Outback", "Forester", "Crosstrek", "Impreza", "Ascent", "Legacy"],
            "Hyundai": ["Elantra", "Sonata", "Tucson", "Santa Fe", "Palisade", "Kona"],
            "Kia": ["Forte", "Optima", "Sportage", "Sorento", "Telluride", "Soul"],
            "Lexus": ["ES", "IS", "RX", "NX", "GX", "UX"]
        }
        
        if search.model:
            model = search.model
        else:
            model = random.choice(model_map.get(make, ["Sedan", "SUV"]))
        
        # Year
        if search.year_min and search.year_max:
            year = random.randint(search.year_min, search.year_max)
        elif search.year_min:
            year = random.randint(search.year_min, 2024)
        elif search.year_max:
            year = random.randint(2015, search.year_max)
        else:
            year = random.randint(2016, 2024)
        
        # Base price calculation (realistic market values)
        base_prices = {
            "Civic": 15000, "Accord": 18000, "CR-V": 22000, "Pilot": 28000,
            "Camry": 18000, "Corolla": 15000, "RAV4": 23000, "Highlander": 30000,
            "F-150": 28000, "Escape": 20000, "Explorer": 28000, "Mustang": 25000,
            "Silverado": 30000, "Equinox": 20000, "Malibu": 17000,
            "ES": 28000, "IS": 26000, "RX": 35000, "NX": 32000
        }
        
        base_price = base_prices.get(model, 20000)
        
        # Adjust price by year (newer = more expensive)
        year_multiplier = 1 + ((year - 2015) * 0.08)
        price = base_price * year_multiplier
        
        # Add random variance (-10% to +15%)
        price = price * random.uniform(0.90, 1.15)
        
        # Mileage (realistic for year)
        years_old = 2024 - year
        avg_miles_per_year = random.randint(10000, 15000)
        mileage = years_old * avg_miles_per_year + random.randint(-5000, 5000)
        mileage = max(100, mileage)  # At least 100 miles
        
        # Apply mileage discount
        if mileage > 100000:
            price *= 0.85
        elif mileage > 75000:
            price *= 0.90
        elif mileage > 50000:
            price *= 0.95
        
        # Check against search price constraints
        if search.price_min and price < search.price_min:
            price = random.uniform(search.price_min, search.price_min * 1.2)
        if search.price_max and price > search.price_max:
            price = random.uniform(search.price_max * 0.8, search.price_max)
        
        # Round to nearest $100
        price = round(price / 100) * 100
        
        # Check mileage constraint
        if search.mileage_max and mileage > search.mileage_max:
            return None  # Skip this listing
        
        # Trim levels
        trim_options = ["Base", "LX", "EX", "EX-L", "Touring", "Sport", "Limited", "Premium", "SE", "XLE", "LE"]
        trim = random.choice(trim_options)
        
        # Generate features (3-8 features)
        num_features = random.randint(3, 8)
        features = random.sample(LiveListingService.COMMON_FEATURES, k=num_features)
        
        # Certified pre-owned (20% chance for newer cars)
        is_certified = year >= 2020 and random.random() < 0.20
        
        # Price drop (30% chance)
        price_drop = None
        if random.random() < 0.30:
            price_drop = random.randint(500, 2000)
        
        # Days listed
        days_listed = random.randint(1, 90)
        
        # Source
        source = random.choice(LiveListingService.SOURCES)
        
        # Location
        location = random.choice(LiveListingService.LOCATIONS)
        
        # Dealer
        dealer_name = random.choice(LiveListingService.DEALER_NAMES)
        
        # Colors
        exterior_color = random.choice(LiveListingService.COLORS)
        interior_color = random.choice(["Black", "Gray", "Beige", "Brown"])
        
        # Generate real car image URL using centralized service
        from app.services.car_images import CarImageService
        image_url = CarImageService.get_car_image_url(
            make=make,
            model=model,
            year=year,
            width=800,
            height=600
        )
        
        # Generate listing URL (fake but realistic)
        url = f"https://{source.lower().replace(' ', '')}.com/listing/{random.randint(100000, 999999)}"
        
        # VIN (realistic format but fake)
        vin = f"{''.join(random.choices('123456789ABCDEFGHJKLMNPRSTUVWXYZ', k=17))}" if random.random() < 0.7 else None
        
        title = f"{year} {make} {model} {trim}"
        
        return LiveListing(
            title=title,
            year=year,
            make=make,
            model=model,
            trim=trim,
            price=price,
            mileage=mileage,
            location=location,
            dealer_name=dealer_name,
            url=url,
            image_url=image_url,
            source=source,
            vin=vin,
            exterior_color=exterior_color,
            interior_color=interior_color,
            transmission=random.choice(LiveListingService.TRANSMISSIONS),
            fuel_type=random.choice(LiveListingService.FUEL_TYPES),
            drivetrain=random.choice(LiveListingService.DRIVETRAINS),
            features=features,
            days_listed=days_listed,
            price_drop=price_drop,
            is_certified=is_certified
        )
