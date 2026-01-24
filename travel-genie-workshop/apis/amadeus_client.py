"""
Amadeus API Client for Flight and Hotel Search
https://developers.amadeus.com/
"""

import os
import json
from datetime import datetime
from typing import Optional
import requests


class AmadeusClient:
    """Client for Amadeus Self-Service APIs."""
    
    BASE_URL = "https://test.api.amadeus.com/v1"
    BASE_URL_V2 = "https://test.api.amadeus.com/v2"
    
    def __init__(self):
        self.api_key = os.getenv("AMADEUS_API_KEY")
        self.api_secret = os.getenv("AMADEUS_API_SECRET")
        self.access_token = None
        self.token_expires = None
        
        if not self.api_key or not self.api_secret:
            raise ValueError(
                "AMADEUS_API_KEY and AMADEUS_API_SECRET environment variables required. "
                "Get free keys at: https://developers.amadeus.com/"
            )
    
    def _get_access_token(self) -> str:
        """Get OAuth2 access token from Amadeus."""
        if self.access_token and self.token_expires:
            if datetime.now().timestamp() < self.token_expires:
                return self.access_token
        
        url = f"{self.BASE_URL}/security/oauth2/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get Amadeus token: {response.text}")
        
        token_data = response.json()
        self.access_token = token_data["access_token"]
        self.token_expires = datetime.now().timestamp() + token_data["expires_in"] - 60
        
        return self.access_token
    
    def _make_request(self, endpoint: str, params: dict, version: str = "v1") -> dict:
        """Make authenticated request to Amadeus API."""
        token = self._get_access_token()
        base = self.BASE_URL if version == "v1" else self.BASE_URL_V2
        url = f"{base}/{endpoint}"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text, "status_code": response.status_code}
    
    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        max_results: int = 5
    ) -> dict:
        """
        Search for flight offers.
        
        Args:
            origin: Origin airport IATA code (e.g., "JFK", "LAX")
            destination: Destination airport IATA code
            departure_date: Date in YYYY-MM-DD format
            return_date: Optional return date for round-trip
            adults: Number of adult passengers
            max_results: Maximum number of results to return
        """
        params = {
            "originLocationCode": origin.upper()[:3],
            "destinationLocationCode": destination.upper()[:3],
            "departureDate": departure_date,
            "adults": adults,
            "max": max_results,
            "currencyCode": "USD"
        }
        
        if return_date:
            params["returnDate"] = return_date
        
        result = self._make_request("shopping/flight-offers", params, version="v2")
        
        if "error" in result:
            return result
        
        flights = []
        for offer in result.get("data", []):
            try:
                itineraries = offer.get("itineraries", [])
                price_info = offer.get("price", {})
                outbound = itineraries[0] if itineraries else {}
                segments = outbound.get("segments", [])
                
                if segments:
                    first_segment = segments[0]
                    last_segment = segments[-1]
                    
                    flight = {
                        "offer_id": offer.get("id"),
                        "airline": first_segment.get("carrierCode"),
                        "flight_number": f"{first_segment.get('carrierCode')}{first_segment.get('number')}",
                        "origin": first_segment.get("departure", {}).get("iataCode"),
                        "destination": last_segment.get("arrival", {}).get("iataCode"),
                        "departure_time": first_segment.get("departure", {}).get("at"),
                        "arrival_time": last_segment.get("arrival", {}).get("at"),
                        "duration": outbound.get("duration"),
                        "stops": len(segments) - 1,
                        "price": price_info.get("grandTotal"),
                        "currency": price_info.get("currency", "USD"),
                        "seats_available": offer.get("numberOfBookableSeats"),
                        "cabin_class": segments[0].get("cabin", "ECONOMY")
                    }
                    flights.append(flight)
            except Exception:
                continue
        
        return {
            "origin": origin.upper(),
            "destination": destination.upper(),
            "departure_date": departure_date,
            "return_date": return_date,
            "passengers": adults,
            "flights_found": len(flights),
            "flights": flights
        }
    
    def search_hotels(
        self,
        city_code: str,
        check_in_date: str,
        check_out_date: str,
        adults: int = 2,
        max_results: int = 10
    ) -> dict:
        """Search for hotels by city."""
        params = {
            "cityCode": city_code.upper()[:3],
            "radius": 20,
            "radiusUnit": "KM",
            "hotelSource": "ALL"
        }
        
        hotels_result = self._make_request("reference-data/locations/hotels/by-city", params, version="v1")
        
        if "error" in hotels_result:
            return hotels_result
        
        hotel_list = hotels_result.get("data", [])[:max_results]
        
        hotels = []
        for hotel in hotel_list:
            try:
                hotels.append({
                    "hotel_id": hotel.get("hotelId"),
                    "name": hotel.get("name"),
                    "city": city_code.upper(),
                    "address": hotel.get("address", {}).get("lines", [""])[0] if hotel.get("address") else "",
                    "latitude": hotel.get("geoCode", {}).get("latitude"),
                    "longitude": hotel.get("geoCode", {}).get("longitude"),
                    "distance_km": hotel.get("distance", {}).get("value"),
                    "check_in": check_in_date,
                    "check_out": check_out_date
                })
            except Exception:
                continue
        
        return {
            "city": city_code.upper(),
            "check_in": check_in_date,
            "check_out": check_out_date,
            "hotels_found": len(hotels),
            "hotels": hotels
        }


# City code mappings for convenience
CITY_TO_AIRPORT = {
    "new york": "JFK", "nyc": "JFK", "los angeles": "LAX", "la": "LAX",
    "san francisco": "SFO", "chicago": "ORD", "miami": "MIA",
    "london": "LHR", "paris": "CDG", "tokyo": "NRT", "sydney": "SYD",
    "dubai": "DXB", "rome": "FCO", "barcelona": "BCN", "amsterdam": "AMS",
    "bangkok": "BKK", "singapore": "SIN",
}


def normalize_airport_code(city_or_code: str) -> str:
    """Convert city name to airport code."""
    city_lower = city_or_code.lower().strip()
    if len(city_or_code) == 3 and city_or_code.isalpha():
        return city_or_code.upper()
    return CITY_TO_AIRPORT.get(city_lower, city_or_code.upper()[:3])
