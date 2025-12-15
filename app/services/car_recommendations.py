"""
AI-powered car recommendation service.

This service provides intelligent car recommendations based on user preferences.
"""
from typing import List, Optional
import random
from app.schemas.recommendation import (
    CarRecommendationRequest, 
    CarRecommendation, 
    CarRecommendationResponse
)


class CarRecommendationService:
    """Service for generating AI-powered car recommendations."""
    
    # Popular car database for recommendations
    CAR_DATABASE = [
        # Budget-Friendly Sedans (under $20k)
        {"year": 2018, "make": "Honda", "model": "Civic", "trim": "LX", "body": "sedan", "price": 15000, "features": ["backup camera", "bluetooth", "cruise control"]},
        {"year": 2017, "make": "Honda", "model": "Accord", "trim": "Sport", "body": "sedan", "price": 17000, "features": ["sunroof", "alloy wheels", "bluetooth"]},
        {"year": 2019, "make": "Honda", "model": "Civic", "trim": "EX", "body": "sedan", "price": 18000, "features": ["sunroof", "heated seats", "Apple CarPlay"]},
        {"year": 2016, "make": "Honda", "model": "Accord", "trim": "EX", "body": "sedan", "price": 14000, "features": ["backup camera", "sunroof", "bluetooth"]},
        {"year": 2018, "make": "Toyota", "model": "Corolla", "trim": "LE", "body": "sedan", "price": 14500, "features": ["backup camera", "bluetooth", "lane assist"]},
        {"year": 2017, "make": "Toyota", "model": "Camry", "trim": "LE", "body": "sedan", "price": 16000, "features": ["backup camera", "bluetooth", "power seats"]},
        {"year": 2019, "make": "Toyota", "model": "Corolla", "trim": "SE", "body": "sedan", "price": 17500, "features": ["sunroof", "sport seats", "Apple CarPlay"]},
        {"year": 2015, "make": "Honda", "model": "Civic", "trim": "EX", "body": "sedan", "price": 12000, "features": ["sunroof", "backup camera", "bluetooth"]},
        {"year": 2016, "make": "Mazda", "model": "Mazda3", "trim": "Touring", "body": "sedan", "price": 13000, "features": ["sunroof", "leather seats", "navigation"]},
        {"year": 2018, "make": "Hyundai", "model": "Elantra", "trim": "SEL", "body": "sedan", "price": 13500, "features": ["sunroof", "backup camera", "bluetooth"]},
        {"year": 2017, "make": "Nissan", "model": "Sentra", "trim": "SR", "body": "sedan", "price": 12500, "features": ["sport package", "backup camera", "bluetooth"]},
        {"year": 2019, "make": "Kia", "model": "Forte", "trim": "LXS", "body": "sedan", "price": 14000, "features": ["bluetooth", "backup camera", "warranty"]},
        
        # Budget-Friendly Coupes (under $20k)
        {"year": 2016, "make": "Honda", "model": "Civic", "trim": "EX-T", "body": "coupe", "price": 15500, "features": ["turbo", "sunroof", "sport wheels"]},
        {"year": 2017, "make": "Honda", "model": "Accord", "trim": "EX-L", "body": "coupe", "price": 18500, "features": ["leather", "sunroof", "V6 engine"]},
        {"year": 2015, "make": "Honda", "model": "Civic", "trim": "Si", "body": "coupe", "price": 17000, "features": ["manual transmission", "sport suspension", "limited slip"]},
        {"year": 2018, "make": "Hyundai", "model": "Elantra", "trim": "Sport", "body": "coupe", "price": 16000, "features": ["turbo", "sport seats", "sunroof"]},
        
        # Mid-Range Sedans ($20k-$30k)
        {"year": 2020, "make": "Honda", "model": "Accord", "trim": "Sport", "body": "sedan", "price": 24000, "features": ["sunroof", "leather", "Honda Sensing"]},
        {"year": 2021, "make": "Honda", "model": "Civic", "trim": "Touring", "body": "sedan", "price": 26000, "features": ["leather", "sunroof", "navigation", "heated seats"]},
        {"year": 2020, "make": "Toyota", "model": "Camry", "trim": "SE", "body": "sedan", "price": 23000, "features": ["sport seats", "sunroof", "Apple CarPlay"]},
        {"year": 2022, "make": "Honda", "model": "Civic", "trim": "Sport", "body": "sedan", "price": 24000, "features": ["sunroof", "sport wheels", "Apple CarPlay"]},
        {"year": 2022, "make": "Toyota", "model": "Corolla", "trim": "SE", "body": "sedan", "price": 23000, "features": ["backup camera", "lane assist", "Apple CarPlay"]},
        {"year": 2023, "make": "Honda", "model": "Accord", "trim": "Sport", "body": "sedan", "price": 28000, "features": ["sunroof", "leather", "backup camera"]},
        {"year": 2023, "make": "Toyota", "model": "Camry", "trim": "XSE", "body": "sedan", "price": 29000, "features": ["leather", "sunroof", "adaptive cruise"]},
        {"year": 2022, "make": "Mazda", "model": "Mazda3", "trim": "Premium", "body": "sedan", "price": 26000, "features": ["leather", "sunroof", "Bose audio"]},
        {"year": 2023, "make": "Hyundai", "model": "Sonata", "trim": "SEL Plus", "body": "sedan", "price": 27000, "features": ["sunroof", "wireless charging"]},
        
        # Budget SUVs (under $20k)
        {"year": 2016, "make": "Honda", "model": "CR-V", "trim": "EX", "body": "suv", "price": 18000, "features": ["AWD", "sunroof", "backup camera"]},
        {"year": 2017, "make": "Toyota", "model": "RAV4", "trim": "LE", "body": "suv", "price": 17500, "features": ["AWD", "backup camera", "bluetooth"]},
        {"year": 2015, "make": "Mazda", "model": "CX-5", "trim": "Touring", "body": "suv", "price": 16000, "features": ["AWD", "sunroof", "backup camera"]},
        {"year": 2018, "make": "Subaru", "model": "Forester", "trim": "Premium", "body": "suv", "price": 19000, "features": ["AWD", "sunroof", "EyeSight"]},
        
        # Mid-Range SUVs ($20k-$40k)
        {"year": 2020, "make": "Honda", "model": "CR-V", "trim": "EX", "body": "suv", "price": 28000, "features": ["AWD", "sunroof", "Honda Sensing"]},
        {"year": 2023, "make": "Honda", "model": "CR-V", "trim": "EX-L", "body": "suv", "price": 35000, "features": ["AWD", "leather", "sunroof", "Honda Sensing"]},
        {"year": 2023, "make": "Toyota", "model": "RAV4", "trim": "XLE Premium", "body": "suv", "price": 34000, "features": ["AWD", "sunroof", "power liftgate"]},
        {"year": 2023, "make": "Mazda", "model": "CX-5", "trim": "Touring", "body": "suv", "price": 32000, "features": ["AWD", "leather", "Bose audio"]},
        {"year": 2022, "make": "Subaru", "model": "Outback", "trim": "Premium", "body": "suv", "price": 33000, "features": ["AWD", "roof rails", "EyeSight"]},
        {"year": 2022, "make": "Mazda", "model": "CX-30", "trim": "Select", "body": "suv", "price": 26000, "features": ["AWD", "safety features", "touchscreen"]},
        
        # Trucks
        {"year": 2018, "make": "Ford", "model": "F-150", "trim": "XLT", "body": "truck", "price": 28000, "features": ["4WD", "towing package", "backup camera"]},
        {"year": 2023, "make": "Ford", "model": "F-150", "trim": "XLT", "body": "truck", "price": 42000, "features": ["4WD", "towing package", "backup camera"]},
        {"year": 2023, "make": "Chevrolet", "model": "Silverado", "trim": "LT", "body": "truck", "price": 41000, "features": ["4WD", "towing", "power seats"]},
        {"year": 2022, "make": "Toyota", "model": "Tacoma", "trim": "SR5", "body": "truck", "price": 38000, "features": ["4WD", "towing", "off-road package"]},
        
        # Luxury - Lexus (various price ranges)
        # Budget-friendly used Lexus (under $20k)
        {"year": 2010, "make": "Lexus", "model": "ES", "trim": "350", "body": "sedan", "price": 12000, "features": ["leather", "sunroof", "premium audio", "heated seats"]},
        {"year": 2011, "make": "Lexus", "model": "IS", "trim": "250", "body": "sedan", "price": 13500, "features": ["leather", "sunroof", "premium audio", "backup camera"]},
        {"year": 2012, "make": "Lexus", "model": "ES", "trim": "350", "body": "sedan", "price": 14500, "features": ["leather", "sunroof", "navigation", "heated seats"]},
        {"year": 2013, "make": "Lexus", "model": "IS", "trim": "250", "body": "sedan", "price": 16000, "features": ["leather", "sunroof", "premium audio", "sport package"]},
        {"year": 2014, "make": "Lexus", "model": "ES", "trim": "300h", "body": "sedan", "price": 17500, "features": ["hybrid", "leather", "sunroof", "navigation", "backup camera"]},
        {"year": 2014, "make": "Lexus", "model": "IS", "trim": "250", "body": "sedan", "price": 18000, "features": ["leather", "sunroof", "premium audio", "backup camera"]},
        {"year": 2015, "make": "Lexus", "model": "ES", "trim": "350", "body": "sedan", "price": 19500, "features": ["leather", "sunroof", "navigation", "heated seats", "premium audio"]},
        
        # Mid-range Lexus ($20k-$35k)
        {"year": 2015, "make": "Lexus", "model": "IS", "trim": "250", "body": "sedan", "price": 22000, "features": ["leather", "sunroof", "premium audio"]},
        {"year": 2016, "make": "Lexus", "model": "ES", "trim": "300h", "body": "sedan", "price": 24000, "features": ["hybrid", "leather", "sunroof", "navigation"]},
        {"year": 2017, "make": "Lexus", "model": "ES", "trim": "350", "body": "sedan", "price": 25000, "features": ["leather", "sunroof", "heated seats", "navigation"]},
        {"year": 2018, "make": "Lexus", "model": "IS", "trim": "300", "body": "sedan", "price": 28000, "features": ["leather", "sunroof", "premium audio", "backup camera"]},
        {"year": 2016, "make": "Lexus", "model": "RX", "trim": "350", "body": "suv", "price": 30000, "features": ["AWD", "leather", "sunroof", "navigation"]},
        {"year": 2019, "make": "Lexus", "model": "IS", "trim": "350", "body": "sedan", "price": 32000, "features": ["leather", "sunroof", "premium audio", "V6 engine"]},
        {"year": 2018, "make": "Lexus", "model": "NX", "trim": "300", "body": "suv", "price": 32000, "features": ["AWD", "leather", "sunroof", "backup camera"]},
        
        # Premium Lexus ($35k+)
        {"year": 2020, "make": "Lexus", "model": "ES", "trim": "350", "body": "sedan", "price": 38000, "features": ["leather", "sunroof", "premium audio", "heated seats", "safety system"]},
        {"year": 2021, "make": "Lexus", "model": "IS", "trim": "300", "body": "sedan", "price": 40000, "features": ["leather", "sunroof", "sport package", "premium audio"]},
        {"year": 2023, "make": "Lexus", "model": "ES", "trim": "350", "body": "sedan", "price": 45000, "features": ["leather", "sunroof", "premium audio", "heated seats"]},
        {"year": 2023, "make": "Lexus", "model": "NX", "trim": "350", "body": "suv", "price": 46000, "features": ["AWD", "leather", "panoramic roof", "premium audio"]},
        {"year": 2022, "make": "Lexus", "model": "RX", "trim": "350", "body": "suv", "price": 48000, "features": ["AWD", "leather", "panoramic roof", "premium audio", "navigation"]},
        
        # Other Luxury
        {"year": 2022, "make": "BMW", "model": "3 Series", "trim": "330i", "body": "sedan", "price": 48000, "features": ["leather", "sunroof", "sport package"]},
        {"year": 2023, "make": "Audi", "model": "Q5", "trim": "Premium", "body": "suv", "price": 47000, "features": ["AWD", "leather", "panoramic roof", "virtual cockpit"]},
        
        # Electric/Hybrid
        {"year": 2023, "make": "Tesla", "model": "Model 3", "trim": "Long Range", "body": "sedan", "price": 50000, "features": ["autopilot", "premium audio", "glass roof"]},
        {"year": 2023, "make": "Toyota", "model": "Prius", "trim": "XLE", "body": "sedan", "price": 32000, "features": ["hybrid", "sunroof", "heated seats"]},
        {"year": 2023, "make": "Hyundai", "model": "Ioniq 5", "trim": "SEL", "body": "suv", "price": 45000, "features": ["electric", "AWD", "fast charging"]},
        {"year": 2023, "make": "Kia", "model": "Forte", "trim": "GT-Line", "body": "sedan", "price": 25000, "features": ["sunroof", "sport seats", "wireless charging"]},
    ]
    
    @staticmethod
    def generate_recommendations(request: CarRecommendationRequest) -> CarRecommendationResponse:
        """
        Generate car recommendations based on user preferences.
        
        Args:
            request: CarRecommendationRequest with user preferences
            
        Returns:
            CarRecommendationResponse with recommended cars
        """
        # Filter cars based on criteria
        filtered_cars = CarRecommendationService.CAR_DATABASE.copy()
        
        # Apply budget filter
        if request.budget_min is not None:
            filtered_cars = [car for car in filtered_cars if car["price"] >= request.budget_min]
        if request.budget_max is not None:
            filtered_cars = [car for car in filtered_cars if car["price"] <= request.budget_max]
        
        # Apply year filter
        if request.year_min is not None:
            filtered_cars = [car for car in filtered_cars if car["year"] >= request.year_min]
        if request.year_max is not None:
            filtered_cars = [car for car in filtered_cars if car["year"] <= request.year_max]
        
        # Apply body style filter
        if request.body_styles:
            body_styles_lower = [style.lower() for style in request.body_styles]
            filtered_cars = [car for car in filtered_cars if car["body"].lower() in body_styles_lower]
        
        # Apply brand filter
        if request.brands:
            brands_lower = [brand.lower() for brand in request.brands]
            filtered_cars = [car for car in filtered_cars if car["make"].lower() in brands_lower]
        
        # Score and rank cars
        scored_cars = []
        for car in filtered_cars:
            score = CarRecommendationService._calculate_match_score(car, request)
            scored_cars.append((car, score))
        
        # Sort by score (descending)
        scored_cars.sort(key=lambda x: x[1], reverse=True)
        
        # Take top 5 recommendations
        top_cars = scored_cars[:5]
        
        # Generate recommendations
        recommendations = []
        for car, score in top_cars:
            recommendation = CarRecommendation(
                year=car["year"],
                make=car["make"],
                model=car["model"],
                trim=car.get("trim"),
                estimated_price=car["price"],
                image_url=CarRecommendationService._generate_image_url(car),
                reason=CarRecommendationService._generate_reason(car, request),
                pros=CarRecommendationService._generate_pros(car),
                cons=CarRecommendationService._generate_cons(car),
                confidence_score=round(score, 2)
            )
            recommendations.append(recommendation)
        
        # Generate search summary
        summary = CarRecommendationService._generate_summary(request)
        
        return CarRecommendationResponse(
            recommendations=recommendations,
            total_count=len(recommendations),
            search_summary=summary
        )
    
    @staticmethod
    def _calculate_match_score(car: dict, request: CarRecommendationRequest) -> float:
        """Calculate how well a car matches the user's preferences."""
        score = 0.5  # Base score
        
        # Budget fit (closer to middle of range = higher score)
        if request.budget_min is not None and request.budget_max is not None:
            budget_middle = (request.budget_min + request.budget_max) / 2
            budget_range = request.budget_max - request.budget_min
            if budget_range > 0:
                distance_from_middle = abs(car["price"] - budget_middle)
                budget_score = 1 - (distance_from_middle / (budget_range / 2))
                score += max(0, budget_score) * 0.3
        
        # Feature matching
        if request.features:
            features_lower = [f.lower() for f in request.features]
            car_features_lower = [f.lower() for f in car.get("features", [])]
            matches = sum(1 for feat in features_lower if any(feat in cf for cf in car_features_lower))
            if len(features_lower) > 0:
                feature_score = matches / len(features_lower)
                score += feature_score * 0.2
        
        # Newer year bonus
        if car["year"] >= 2023:
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    @staticmethod
    def _generate_image_url(car: dict) -> str:
        """
        Generate a car image URL using real car photo APIs.
        
        Uses the centralized CarImageService for best quality images.
        """
        from app.services.car_images import CarImageService
        
        return CarImageService.get_car_image_url(
            make=car['make'],
            model=car['model'],
            year=car['year'],
            width=800,
            height=500
        )
    
    @staticmethod
    def _generate_reason(car: dict, request: CarRecommendationRequest) -> str:
        """Generate a reason why this car is recommended."""
        reasons = []
        
        if request.budget_max and car["price"] <= request.budget_max:
            reasons.append("fits your budget")
        
        if request.body_styles and car["body"] in [s.lower() for s in request.body_styles]:
            reasons.append(f"matches your preference for {car['body']}s")
        
        if car["year"] >= 2023:
            reasons.append("recent model year")
        
        if not reasons:
            reasons.append("excellent reliability and value")
        
        return f"Great choice! This car {', '.join(reasons)}."
    
    @staticmethod
    def _generate_pros(car: dict) -> List[str]:
        """Generate pros for a car."""
        pros = []
        
        if car["make"].lower() in ["toyota", "honda", "mazda", "subaru"]:
            pros.append("Excellent reliability")
        
        if car["year"] >= 2023:
            pros.append("Latest safety features")
        
        if car["body"] == "suv":
            pros.append("Spacious interior and cargo area")
        elif car["body"] == "sedan":
            pros.append("Fuel efficient")
        elif car["body"] == "truck":
            pros.append("Strong towing capacity")
        
        if "AWD" in car.get("features", []) or "4WD" in car.get("features", []):
            pros.append("All-weather capability")
        
        if len(pros) < 3:
            pros.append("Good resale value")
        
        return pros[:3]
    
    @staticmethod
    def _generate_cons(car: dict) -> List[str]:
        """Generate cons for a car."""
        cons = []
        
        if car["price"] > 45000:
            cons.append("Higher price point")
        
        if car["body"] == "truck":
            cons.append("Lower fuel economy")
        
        if car["make"].lower() in ["bmw", "audi"]:
            cons.append("Higher maintenance costs")
        
        if car["year"] < 2022:
            cons.append("Older technology")
        
        if len(cons) == 0:
            cons.append("Limited inventory in some markets")
        
        return cons[:2]
    
    @staticmethod
    def _generate_summary(request: CarRecommendationRequest) -> str:
        """Generate a summary of search criteria."""
        parts = []
        
        if request.budget_min or request.budget_max:
            if request.budget_min and request.budget_max:
                parts.append(f"${request.budget_min:,.0f}-${request.budget_max:,.0f}")
            elif request.budget_max:
                parts.append(f"up to ${request.budget_max:,.0f}")
            else:
                parts.append(f"over ${request.budget_min:,.0f}")
        
        if request.body_styles:
            parts.append(f"{', '.join(request.body_styles)}")
        
        if request.year_min or request.year_max:
            if request.year_min and request.year_max:
                parts.append(f"{request.year_min}-{request.year_max}")
            elif request.year_min:
                parts.append(f"{request.year_min}+")
        
        if request.brands:
            parts.append(f"{', '.join(request.brands)}")
        
        if parts:
            return f"Showing recommendations for: {' | '.join(parts)}"
        else:
            return "Showing all available recommendations"
