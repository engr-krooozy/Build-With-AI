"""
Duffel API Client for Flight Search
https://duffel.com/docs/api
"""

import os
import json
import requests
from typing import Optional, List


class DuffelClient:
    """Client for Duffel Flight APIs."""
    
    BASE_URL = "https://api.duffel.com/air"
    
    def __init__(self):
        self.api_key = os.getenv("DUFFEL_API_KEY")
        if not self.api_key:
            raise ValueError("DUFFEL_API_KEY environment variable required.")

    def _make_request(self, method: str, endpoint: str, data: Optional[dict] = None) -> dict:
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Duffel-Version": "v2",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Encoding": "gzip"
        }
        response = requests.request(method, url, headers=headers, json=data)
        return response.json() if response.status_code in [200, 201] else {"error": response.text}

    def search_flights(self, origin: str, destination: str, departure_date: str, return_date: Optional[str] = None, adults: int = 1) -> dict:
        slices = [{"origin": origin.upper(), "destination": destination.upper(), "departure_date": departure_date}]
        if return_date:
            slices.append({"origin": destination.upper(), "destination": origin.upper(), "departure_date": return_date})
            
        data = {"data": {"slices": slices, "passengers": [{"type": "adult"} for _ in range(adults)], "cabin_class": "economy"}}
        result = self._make_request("POST", "offer_requests", data=data)
        
        if "error" in result: return result
        
        offers = result.get("data", {}).get("offers", [])[:5]
        flights = []
        for offer in offers:
            try:
                outbound = offer.get("slices", [])[0]
                segments = outbound.get("segments", [])
                flights.append({
                    "airline": segments[0].get("operating_carrier", {}).get("iata_code"),
                    "flight_number": f"{segments[0].get('operating_carrier_flight_number')}",
                    "departure_time": segments[0].get("departing_at"),
                    "arrival_time": segments[-1].get("arriving_at"),
                    "price": offer.get("total_amount"),
                    "currency": offer.get("total_currency")
                })
            except Exception: continue
                
        return {"flights": flights, "flights_found": len(flights)}

CITY_TO_AIRPORT = {
    "new york": "JFK", "nyc": "JFK", "los angeles": "LAX", "la": "LAX",
    "san francisco": "SFO", "chicago": "ORD", "miami": "MIA",
    "london": "LHR", "paris": "CDG", "tokyo": "NRT", "sydney": "SYD",
}

def normalize_airport_code(city_or_code: str) -> str:
    city_lower = city_or_code.lower().strip()
    if len(city_or_code) == 3 and city_or_code.isalpha():
        return city_or_code.upper()
    return CITY_TO_AIRPORT.get(city_lower, city_or_code.upper()[:3])
