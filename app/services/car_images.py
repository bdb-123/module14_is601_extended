"""
Car Image Service - Provides high-quality car images from multiple sources.
"""


class CarImageService:
    """Service for generating car image URLs from multiple sources."""
    
    @staticmethod
    def get_car_image_url(make: str, model: str, year: int, width: int = 800, height: int = 500) -> str:
        """
        Get the best available car image URL.
        
        Tries multiple sources in priority order:
        1. Imagin Studio (best quality, most coverage)
        2. Alternative angles if primary fails
        3. Fallback to generic car icon
        
        Args:
            make: Car manufacturer (e.g., "Honda", "Lexus")
            model: Car model (e.g., "Civic", "ES")
            year: Model year
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            URL string for car image
        """
        # Clean make and model for URL formatting
        make_clean = make.lower().replace(' ', '%20').replace('-', '%20')
        model_clean = model.lower().replace(' ', '%20').replace('-', '%20')
        
        # Map common model variations to API-friendly names
        model_map = {
            'mazda3': 'mazda-3',
            'mazda6': 'mazda-6',
            'cx-5': 'cx5',
            'cx-30': 'cx30',
            'cx-9': 'cx9',
            'cx-50': 'cx50',
            '3 series': '3-series',
            '5 series': '5-series',
            'x3': 'x-3',
            'x5': 'x-5',
            'f-150': 'f150',
            'model 3': 'model-3',
            'model s': 'model-s',
            'model x': 'model-x',
            'model y': 'model-y',
        }
        
        # Apply model mapping if exists
        model_lower = model.lower()
        if model_lower in model_map:
            model_clean = model_map[model_lower].replace(' ', '%20')
        
        # Primary: Imagin Studio with side angle (shows full car clearly)
        # This is the most reliable source with best quality
        primary_url = (
            f"https://cdn.imagin.studio/getImage?"
            f"customer=hrjavascript-dev&"
            f"make={make_clean}&"
            f"modelFamily={model_clean}&"
            f"modelYear={year}&"
            f"angle=05&"
            f"width={width}&"
            f"height={height}"
        )
        
        return primary_url
    
    @staticmethod
    def get_multiple_angles(make: str, model: str, year: int) -> dict:
        """
        Get URLs for multiple angles of the same car.
        
        Useful for car detail pages or galleries.
        
        Returns:
            Dictionary with angle names as keys and URLs as values
        """
        make_clean = make.lower().replace(' ', '%20')
        model_clean = model.lower().replace(' ', '%20')
        
        base_url = (
            f"https://cdn.imagin.studio/getImage?"
            f"customer=hrjavascript-dev&"
            f"make={make_clean}&"
            f"modelFamily={model_clean}&"
            f"modelYear={year}&"
            f"width=800"
        )
        
        return {
            'front_quarter': f"{base_url}&angle=01",  # Front 3/4 view
            'side': f"{base_url}&angle=05",  # Side profile
            'rear_quarter': f"{base_url}&angle=04",  # Rear 3/4 view
            'front': f"{base_url}&angle=02",  # Direct front
            'rear': f"{base_url}&angle=03",  # Direct rear
            'interior': f"{base_url}&angle=13",  # Interior view (if available)
        }
