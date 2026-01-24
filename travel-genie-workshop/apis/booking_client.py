"""
Booking.com API Client via RapidAPI
"""

import os
import requests
from typing import Optional


class BookingClient:
    """Client for Booking.com APIs via RapidAPI."""
    
    BASE_URL = "https://booking-com.p.rapidapi.com"
    
    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        if not self.api_key:
            raise ValueError("RAPIDAPI_KEY environment variable required.")
        self.headers = {"X-RapidAPI-Key": self.api_key, "X-RapidAPI-Host": "booking-com.p.rapidapi.com"}

    def _get_location_id(self, name: str) -> Optional[str]:
        url = f"{self.BASE_URL}/v1/hotels/locations"
        response = requests.get(url, headers=self.headers, params={"name": name, "locale": "en-gb"})
        if response.status_code == 200:
            locations = response.json()
            return locations[0].get("dest_id") if locations else None
        return None

    def search_hotels(self, location_name: str, check_in_date: str, check_out_date: str, adults: int = 2) -> dict:
        dest_id = self._get_location_id(location_name)
        if not dest_id: return {"error": "Location not found"}
        
        params = {"dest_id": dest_id, "checkin_date": check_in_date, "checkout_date": check_out_date, "adults_number": str(adults), "units": "metric", "dest_type": "city"}
        response = requests.get(f"{self.BASE_URL}/v1/hotels/search", headers=self.headers, params=params)
        
        if response.status_code != 200: return {"error": response.text}
        
        results = response.json().get("result", [])[:10]
        hotels = [{"name": h.get("hotel_name"), "price": h.get("min_total_price"), "currency": h.get("currency_code"), "rating": h.get("review_score")} for h in results]
        return {"hotels": hotels, "hotels_found": len(hotels)}
