"""
Google Places API Client (NEW v1) for Attractions and Points of Interest
https://developers.google.com/maps/documentation/places/web-service/op-overview
"""

import os
import json
from typing import Optional
import requests


class PlacesClient:
    """Client for Google Places API (New v1)."""
    
    BASE_URL = "https://places.googleapis.com/v1/places"
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "GOOGLE_PLACES_API_KEY environment variable required. "
                "Get a key at: https://console.cloud.google.com/"
            )
    
    def _text_search(self, query: str, max_results: int = 10) -> dict:
        """Perform a text search using the new Places API."""
        url = f"{self.BASE_URL}:searchText"
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.types,places.location,places.currentOpeningHours,places.priceLevel"
        }
        
        data = {"textQuery": query, "maxResultCount": max_results}
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            return {"error": f"Places API error: {response.text}"}
        
        return response.json()
    
    def get_attractions(self, city: str, max_results: int = 10) -> dict:
        """Get tourist attractions in a city."""
        result = self._text_search(f"tourist attractions landmarks in {city}", max_results)
        
        if "error" in result:
            return result
        
        places = result.get("places", [])
        attractions = []
        for place in places:
            attractions.append({
                "name": place.get("displayName", {}).get("text"),
                "address": place.get("formattedAddress"),
                "rating": place.get("rating"),
                "total_reviews": place.get("userRatingCount"),
                "types": [t.replace("_", " ").title() for t in place.get("types", [])[:3]],
                "open_now": place.get("currentOpeningHours", {}).get("openNow"),
            })
        
        return {"city": city, "attractions_found": len(attractions), "attractions": attractions}
    
    def get_restaurants(self, city: str, cuisine: Optional[str] = None, max_results: int = 10) -> dict:
        """Get restaurants in a city."""
        query = f"{cuisine} restaurants in {city}" if cuisine else f"best restaurants in {city}"
        result = self._text_search(query, max_results)
        
        if "error" in result:
            return result
        
        places = result.get("places", [])
        restaurants = []
        for place in places:
            price_map = {"PRICE_LEVEL_INEXPENSIVE": "$", "PRICE_LEVEL_MODERATE": "$$", "PRICE_LEVEL_EXPENSIVE": "$$$", "PRICE_LEVEL_VERY_EXPENSIVE": "$$$$"}
            price_range = price_map.get(place.get("priceLevel"), "N/A")
            
            restaurants.append({
                "name": place.get("displayName", {}).get("text"),
                "address": place.get("formattedAddress"),
                "rating": place.get("rating"),
                "total_reviews": place.get("userRatingCount"),
                "price_range": price_range,
                "open_now": place.get("currentOpeningHours", {}).get("openNow"),
            })
        
        return {"city": city, "cuisine": cuisine or "Various", "restaurants_found": len(restaurants), "restaurants": restaurants}
    
    def get_hotels(self, city: str, max_results: int = 10) -> dict:
        """Get hotels in a city (backup for Booking.com)."""
        result = self._text_search(f"hotels lodging in {city}", max_results)
        
        if "error" in result:
            return result
        
        places = result.get("places", [])
        hotels = []
        for place in places:
            price_map = {"PRICE_LEVEL_INEXPENSIVE": "Economy", "PRICE_LEVEL_MODERATE": "Mid-Range", "PRICE_LEVEL_EXPENSIVE": "Upscale", "PRICE_LEVEL_VERY_EXPENSIVE": "Luxury"}
            
            hotels.append({
                "name": place.get("displayName", {}).get("text"),
                "address": place.get("formattedAddress"),
                "rating": place.get("rating"),
                "total_reviews": place.get("userRatingCount"),
                "price_category": price_map.get(place.get("priceLevel"), "Unknown"),
            })
        
        return {"city": city, "hotels_found": len(hotels), "hotels": hotels}
