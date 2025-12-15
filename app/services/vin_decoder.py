# app/services/vin_decoder.py
"""
VIN Decoder Service Module

This module provides integration with the NHTSA (National Highway Traffic Safety
Administration) VIN decoder API to retrieve vehicle information.

The NHTSA API is a free, public service that decodes Vehicle Identification Numbers
to return make, model, year, and other vehicle details.

API Documentation: https://vpic.nhtsa.dot.gov/api/
"""

import httpx
from typing import Optional, Dict, Any


class VINDecoderService:
    """
    Service class for decoding VINs using the NHTSA API.
    
    This service handles:
    - Making HTTP requests to the NHTSA VIN decoder API
    - Parsing and normalizing the response
    - Error handling (timeouts, network errors, invalid responses)
    - Extracting relevant vehicle information (year, make, model, trim)
    """
    
    # NHTSA VIN decoder API endpoint
    BASE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin"
    
    # Timeout for external API calls (in seconds)
    TIMEOUT = 10.0
    
    @classmethod
    async def decode_vin(cls, vin: str) -> Dict[str, Optional[str]]:
        """
        Decode a VIN using the NHTSA API.
        
        Makes an asynchronous HTTP request to the NHTSA VIN decoder API
        and extracts vehicle information.
        
        Args:
            vin: The VIN string to decode (should be 17 characters)
            
        Returns:
            Dictionary with keys: year, make, model, trim
            Values are strings if found, None if not available
            
        Raises:
            httpx.TimeoutException: If the request times out
            httpx.HTTPError: If there's a network error
            ValueError: If the API response is invalid or unexpected
        """
        # Validate VIN length
        if len(vin) != 17:
            raise ValueError("VIN must be exactly 17 characters")
        
        # Build the request URL with query parameters
        url = f"{cls.BASE_URL}/{vin}"
        params = {
            "format": "json"  # Request JSON format response
        }
        
        # Make the HTTP request with timeout
        async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()  # Raise exception for 4xx/5xx status codes
                
            except httpx.TimeoutException as e:
                raise httpx.TimeoutException(
                    f"NHTSA API request timed out after {cls.TIMEOUT} seconds"
                ) from e
            
            except httpx.HTTPError as e:
                raise httpx.HTTPError(
                    f"NHTSA API request failed: {str(e)}"
                ) from e
        
        # Parse the JSON response
        try:
            data = response.json()
        except Exception as e:
            raise ValueError(f"Invalid JSON response from NHTSA API: {str(e)}") from e
        
        # Extract vehicle information from the response
        return cls._parse_nhtsa_response(data)
    
    @classmethod
    def _parse_nhtsa_response(cls, data: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """
        Parse the NHTSA API response and extract vehicle information.
        
        The NHTSA API returns a complex nested structure. This method
        extracts the relevant fields (year, make, model, trim) and
        normalizes them into a simple dictionary.
        
        Args:
            data: The parsed JSON response from NHTSA API
            
        Returns:
            Dictionary with keys: year, make, model, trim
            
        Raises:
            ValueError: If the response structure is unexpected
        """
        # The NHTSA API returns a 'Results' array with variable/value pairs
        if "Results" not in data:
            raise ValueError("Invalid NHTSA API response: missing 'Results' field")
        
        results = data["Results"]
        if not isinstance(results, list):
            raise ValueError("Invalid NHTSA API response: 'Results' is not a list")
        
        # Build a lookup dictionary from the results
        lookup = {}
        for item in results:
            if isinstance(item, dict) and "Variable" in item and "Value" in item:
                variable = item["Variable"]
                value = item["Value"]
                # Only store non-empty values
                if value and value.strip():
                    lookup[variable] = value.strip()
        
        # Extract the fields we care about
        # NHTSA uses specific variable names for each field
        return {
            "year": lookup.get("Model Year"),
            "make": lookup.get("Make"),
            "model": lookup.get("Model"),
            "trim": lookup.get("Trim") or lookup.get("Series"),  # Try both fields
        }
    
    @classmethod
    def decode_vin_sync(cls, vin: str) -> Dict[str, Optional[str]]:
        """
        Synchronous version of decode_vin for non-async contexts.
        
        This is a convenience wrapper that uses httpx's synchronous client.
        
        Args:
            vin: The VIN string to decode
            
        Returns:
            Dictionary with keys: year, make, model, trim
            
        Raises:
            httpx.TimeoutException: If the request times out
            httpx.HTTPError: If there's a network error
            ValueError: If the API response is invalid or unexpected
        """
        # Validate VIN length
        if len(vin) != 17:
            raise ValueError("VIN must be exactly 17 characters")
        
        # Build the request URL
        url = f"{cls.BASE_URL}/{vin}"
        params = {"format": "json"}
        
        # Make synchronous HTTP request
        try:
            with httpx.Client(timeout=cls.TIMEOUT) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                
        except httpx.TimeoutException as e:
            raise httpx.TimeoutException(
                f"NHTSA API request timed out after {cls.TIMEOUT} seconds"
            ) from e
        
        except httpx.HTTPError as e:
            raise httpx.HTTPError(
                f"NHTSA API request failed: {str(e)}"
            ) from e
        
        # Parse and return
        try:
            data = response.json()
        except Exception as e:
            raise ValueError(f"Invalid JSON response from NHTSA API: {str(e)}") from e
        
        return cls._parse_nhtsa_response(data)
