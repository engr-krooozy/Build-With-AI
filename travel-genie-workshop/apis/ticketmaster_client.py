"""
Ticketmaster Discovery API Client for Events Search
https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
"""

import os
import requests
from typing import Optional

class TicketmasterClient:
    """Client for Ticketmaster Discovery API."""
    
    BASE_URL = "https://app.ticketmaster.com/discovery/v2"
    
    def __init__(self):
        self.api_key = os.getenv("TICKETMASTER_API_KEY")
        if not self.api_key:
            raise ValueError("TICKETMASTER_API_KEY environment variable required.")
    
    def search_events(self, city: str, keyword: Optional[str] = None, max_results: int = 10) -> dict:
        """Search for events in a city."""
        url = f"{self.BASE_URL}/events.json"
        params = {
            "apikey": self.api_key,
            "city": city,
            "size": max_results,
            "sort": "date,asc"
        }
        if keyword: params["keyword"] = keyword
        
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return {"error": f"Ticketmaster API error: {response.text}"}
        
        data = response.json()
        events = []
        for event in data.get("_embedded", {}).get("events", []):
            try:
                events.append({
                    "name": event.get("name"),
                    "date": event.get("dates", {}).get("start", {}).get("localDate"),
                    "venue": event.get("_embedded", {}).get("venues", [{}])[0].get("name"),
                    "url": event.get("url")
                })
            except: continue
            
        return {"city": city, "events_found": len(events), "events": events}
