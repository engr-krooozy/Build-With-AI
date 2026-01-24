"""
SerpAPI Client for Real Events Search (Google Events)
https://serpapi.com/google-events-api
"""

import os
import json
from typing import Optional
import requests


class EventsClient:
    """Client for SerpAPI Google Events search."""
    
    BASE_URL = "https://serpapi.com/search"
    
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "SERPAPI_API_KEY environment variable required. "
                "Get a free key at: https://serpapi.com/"
            )
    
    def get_events(
        self,
        location: str,
        query: Optional[str] = None,
        date_filter: str = "week"
    ) -> dict:
        """
        Search for events in a location.
        
        Args:
            location: City or location name (e.g., "Paris, France")
            query: Optional search query (e.g., "concerts", "sports")
            date_filter: Time filter - "today", "tomorrow", "week", "month"
        """
        search_query = f"events in {location}"
        if query:
            search_query = f"{query} events in {location}"
        
        params = {
            "engine": "google_events",
            "q": search_query,
            "hl": "en",
            "api_key": self.api_key
        }
        
        response = requests.get(self.BASE_URL, params=params)
        
        if response.status_code != 200:
            return {"error": f"SerpAPI error: {response.text}"}
        
        data = response.json()
        
        if "error" in data:
            return {"error": data["error"]}
        
        events_results = data.get("events_results", [])
        
        events = []
        for event in events_results[:15]:
            date_info = event.get("date", {})
            events.append({
                "title": event.get("title"),
                "date": date_info.get("start_date"),
                "time": date_info.get("when"),
                "venue": event.get("venue", {}).get("name"),
                "address": event.get("address", []),
                "description": event.get("description"),
                "link": event.get("link"),
                "thumbnail": event.get("thumbnail"),
            })
        
        return {
            "location": location,
            "query": query,
            "events_found": len(events),
            "events": events
        }
    
    def get_concerts(self, location: str) -> dict:
        """Get concerts and music events."""
        return self.get_events(location, query="concerts live music", date_filter="month")
    
    def get_sports_events(self, location: str) -> dict:
        """Get sports events."""
        return self.get_events(location, query="sports games matches", date_filter="month")
    
    def get_festivals(self, location: str) -> dict:
        """Get festivals and cultural events."""
        return self.get_events(location, query="festivals cultural events", date_filter="month")
