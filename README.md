# 🧞 TravelGenie Live: Building an AI Travel Concierge with Real APIs

## Welcome to the Workshop! ✈️

In this hands-on workshop, you'll build **TravelGenie Live**, an autonomous AI travel concierge powered by **REAL APIs** for:

- ✈️ **Real Flight Search** - Actual flights via hundreds of airlines (Duffel API)
- 🏨 **Real Hotel Search** - Actual hotel listings via Booking.com (RapidAPI)
- 🌤️ **Live Weather** - Real forecasts and conditions (OpenWeatherMap)
- 🎯 **Real Attractions** - Actual tourist spots with ratings (Google Places)
- 🎭 **Live Events** - Real concerts, sports, and festivals (SerpAPI + Ticketmaster)
- 📅 **Smart Itineraries** - AI-generated using all real data

**All data is LIVE and REAL!**

**Estimated Time:** ~90 minutes

---

## 🎯 What You'll Learn

| Concept | Description |
|---------|-------------|
| **LangGraph** | Build autonomous agents with state management and tool calling |
| **Gemini AI** | Use Google's Gemini model via Vertex AI |
| **Real APIs** | Integrate multiple external APIs (Duffel, Booking.com, OpenWeatherMap, Google Places, SerpAPI, Ticketmaster) |
| **API Design** | Build modular, reusable API client classes |
| **Streamlit** | Build modern, interactive web interfaces |
| **Cloud Run** | Deploy serverless, scalable applications |

---

## 🏗️ Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Input    │────▶│    Streamlit    │────▶│   LangGraph     │
│   (Chat UI)     │     │   (Frontend)    │     │   (Agent)       │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                        ┌────────────────────────────────┼────────────────────────────────┐
                        │                                ▼                                │
                        │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
                        │  │   Gemini     │◀───│    Tool      │───▶│  REAL APIs   │      │
                        │  │   (Brain)    │    │   Executor   │    │  (Live Data) │      │
                        │  └──────────────┘    └──────────────┘    └──────────────┘      │
                        │                                                                 │
                        │                         Agent Logic                             │
                        └─────────────────────────────────────────────────────────────────┘
                                                         │
                 ┌───────────────┬───────────────┬───────┴───────┬───────────────┐
                 ▼               ▼               ▼               ▼               ▼
          ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
          │  Duffel  │   │ OpenWea- │   │  Google  │   │ SerpAPI  │   │  Vertex  │
          │ (Flights)│   │ therMap  │   │  Places  │   │ (Events) │   │    AI    │
          └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
```

---

## 🔑 Required API Keys

Before starting, obtain free API keys from these providers:

| API | Free Tier | Sign Up Link |
|-----|-----------|--------------|
| **Duffel** | Pay-as-you-go / Test mode | [duffel.com](https://duffel.com/) |
| **RapidAPI (Booking)** | Free tier available | [rapidapi.com](https://rapidapi.com/apidojo/api/booking-com/) |
| **OpenWeatherMap** | 1,000 calls/day | [openweathermap.org/api](https://openweathermap.org/api) |
| **Google Places** | $200/month credit | [console.cloud.google.com](https://console.cloud.google.com/) |
| **SerpAPI** | 100 searches/month | [serpapi.com](https://serpapi.com/) |
| **Ticketmaster** | 5,000 calls/day | [developer.ticketmaster.com](https://developer.ticketmaster.com/) |

---

## Section 1: Preparing Your Environment

> **Prerequisites:**
> - Google Cloud account with billing enabled
> - Basic Python knowledge
> - API keys from providers listed above

### 1.1 Activate Cloud Shell

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click the **Activate Cloud Shell** button (`>_`) in the top toolbar
3. Click **Open Editor** to launch the VS Code-like environment

### 1.2 Configure Your Project

```bash
# Set your Project ID (replace with your actual project ID)
gcloud config set project YOUR_PROJECT_ID

# Store variables for easy use
export PROJECT_ID=$(gcloud config get-value project)
export REGION="us-central1"

# Verify configuration
echo "Project: $PROJECT_ID | Region: $REGION"
```

### 1.3 Enable Required APIs

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  logging.googleapis.com

echo "✅ APIs enabled successfully!"
```

---

## Section 2: Project Setup

### 2.1 Create Project Directory

```bash
mkdir -p travel-genie-live/apis && cd travel-genie-live
```

### 2.2 Create Environment Variables File

```bash
cat > .env.example << 'EOF'
# TravelGenie Live - Environment Variables
# Copy this file to .env and fill in your API keys

# ========================================
# FLIGHTS API (Duffel)
# Get a key at: https://duffel.com/
# ========================================
DUFFEL_API_KEY=your_duffel_api_key

# ========================================
# HOTELS API (Booking.com via RapidAPI)
# Get a key at: https://rapidapi.com/apidojo/api/booking-com/
# ========================================
RAPIDAPI_KEY=your_rapidapi_key

# ========================================
# OPENWEATHERMAP API (Weather)
# Get free key at: https://openweathermap.org/api
# Free tier: 1,000 calls/day
# ========================================
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key

# ========================================
# GOOGLE PLACES API (Attractions)
# Get key at: https://console.cloud.google.com/
# Free tier: $200 monthly credit
# ========================================
GOOGLE_PLACES_API_KEY=your_google_places_api_key

# ========================================
# SERPAPI (Events)
# Get free key at: https://serpapi.com/
# Free tier: 100 searches/month
# ========================================
SERPAPI_API_KEY=your_serpapi_api_key
EOF

# Create your actual .env file
cp .env.example .env
echo "✅ Now edit .env with your actual API keys"
```

---

## Section 3: Building the API Clients

We will create modular API client classes for each external service.

### 3.1 Create the APIs Package Init

```bash
cat > apis/__init__.py << 'EOF'
"""
API Clients Package for TravelGenie Live
"""

from .duffel_client import DuffelClient, normalize_airport_code
from .booking_client import BookingClient
from .weather_client import WeatherClient
from .places_client import PlacesClient
from .events_client import EventsClient
from .ticketmaster_client import TicketmasterClient

__all__ = ['DuffelClient', 'BookingClient', 'WeatherClient', 'PlacesClient', 'EventsClient', 'TicketmasterClient', 'normalize_airport_code']
EOF
```

### 3.2 Create the Flights & Hotels Clients (Duffel & Booking.com)

We will use **Duffel** for real-time flight search and **Booking.com (via RapidAPI)** for hotels.

#### A. Duffel Client (Flights)

```bash
cat > apis/duffel_client.py << 'EOF'
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
EOF
```

#### B. Booking.com Client (Hotels)

```bash
cat > apis/booking_client.py << 'EOF'
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
EOF
```

### 3.3 Create the Weather Client (OpenWeatherMap)

```bash
cat > apis/weather_client.py << 'EOF'
"""
OpenWeatherMap API Client for Weather Forecasts
https://openweathermap.org/api
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional
import requests


class WeatherClient:
    """Client for OpenWeatherMap API."""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "OPENWEATHERMAP_API_KEY environment variable required. "
                "Get a free key at: https://openweathermap.org/api"
            )
    
    def get_current_weather(self, city: str) -> dict:
        """Get current weather for a city."""
        url = f"{self.BASE_URL}/weather"
        params = {"q": city, "appid": self.api_key, "units": "metric"}
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return {"error": f"Failed to get weather: {response.text}"}
        
        data = response.json()
        
        return {
            "city": data.get("name"),
            "country": data.get("sys", {}).get("country"),
            "current": {
                "temperature_c": round(data.get("main", {}).get("temp", 0)),
                "temperature_f": round(data.get("main", {}).get("temp", 0) * 9/5 + 32),
                "feels_like_c": round(data.get("main", {}).get("feels_like", 0)),
                "humidity": data.get("main", {}).get("humidity"),
                "description": data.get("weather", [{}])[0].get("description", "").title(),
                "wind_speed_kmh": round(data.get("wind", {}).get("speed", 0) * 3.6),
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_forecast(self, city: str, days: int = 5) -> dict:
        """Get weather forecast for a city (5-day / 3-hour intervals)."""
        url = f"{self.BASE_URL}/forecast"
        params = {"q": city, "appid": self.api_key, "units": "metric", "cnt": min(days * 8, 40)}
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return {"error": f"Failed to get forecast: {response.text}"}
        
        data = response.json()
        
        # Group forecasts by day
        daily_forecasts = {}
        
        for item in data.get("list", []):
            dt = datetime.fromtimestamp(item["dt"])
            date_key = dt.strftime("%Y-%m-%d")
            
            if date_key not in daily_forecasts:
                daily_forecasts[date_key] = {
                    "date": date_key, "day_name": dt.strftime("%A"),
                    "temps": [], "descriptions": []
                }
            
            daily_forecasts[date_key]["temps"].append(item["main"]["temp"])
            daily_forecasts[date_key]["descriptions"].append(item["weather"][0]["description"])
        
        forecast_list = []
        for date_key, day_data in sorted(daily_forecasts.items())[:days]:
            temps = day_data["temps"]
            forecast_list.append({
                "date": day_data["date"],
                "day": day_data["day_name"],
                "temp_high_c": round(max(temps)),
                "temp_low_c": round(min(temps)),
                "temp_high_f": round(max(temps) * 9/5 + 32),
                "temp_low_f": round(min(temps) * 9/5 + 32),
                "description": max(set(day_data["descriptions"]), key=day_data["descriptions"].count).title(),
            })
        
        return {
            "city": data.get("city", {}).get("name", city),
            "country": data.get("city", {}).get("country"),
            "forecast_days": len(forecast_list),
            "forecast": forecast_list
        }
    
    def get_weather_for_trip(self, city: str, start_date: str, end_date: str) -> dict:
        """Get weather information for a trip with packing suggestions."""
        current = self.get_current_weather(city)
        forecast = self.get_forecast(city, days=5)
        
        if "error" in current or "error" in forecast:
            return {"error": current.get("error") or forecast.get("error")}
        
        # Determine packing suggestions
        avg_temp = sum(f["temp_high_c"] for f in forecast.get("forecast", [])) / max(len(forecast.get("forecast", [])), 1)
        descriptions = " ".join(f.get("description", "").lower() for f in forecast.get("forecast", []))
        
        packing_tips = []
        if avg_temp < 10:
            packing_tips.extend(["Warm jacket", "Layers", "Gloves"])
        elif avg_temp < 20:
            packing_tips.extend(["Light jacket", "Sweater", "Long pants"])
        else:
            packing_tips.extend(["Light clothing", "T-shirts", "Shorts"])
        
        if "rain" in descriptions:
            packing_tips.append("Umbrella/Rain jacket")
        if "sun" in descriptions or "clear" in descriptions:
            packing_tips.append("Sunglasses/Sunscreen")
        
        return {
            "city": current.get("city"),
            "country": current.get("country"),
            "trip_dates": f"{start_date} to {end_date}",
            "current_weather": current.get("current"),
            "forecast": forecast.get("forecast", []),
            "packing_suggestions": list(set(packing_tips))
        }
EOF
```

### 3.4 Create the Google Places Client (Attractions)

> **Note:** This uses the **new Places API (v1)** - make sure to enable "Places API (New)" in Google Cloud Console.

```bash
cat > apis/places_client.py << 'EOF'
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
EOF
```

### 3.5 Create the Events Client (SerpAPI)

```bash
cat > apis/events_client.py << 'EOF'
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
EOF
```

### 3.6 Create the Ticketmaster Client (Events Backup)

```bash
cat > apis/ticketmaster_client.py << 'EOF'
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
EOF
```

---

## Section 4: Building the Agent

This is the core of TravelGenie—a LangGraph agent powered by Gemini with real API tools.

### 4.1 Create the Agent Module

```bash
cat > agent.py << 'EOF'
"""
TravelGenie Live Agent - Autonomous AI Travel Concierge with Real APIs
Built with LangGraph and Vertex AI (Gemini)
"""

import operator
import json
import os
from typing import Annotated, Sequence, TypedDict, Optional
from datetime import datetime, timedelta

from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph, END

from apis.duffel_client import DuffelClient, normalize_airport_code
from apis.booking_client import BookingClient
from apis.weather_client import WeatherClient
from apis.places_client import PlacesClient
from apis.events_client import EventsClient
from apis.ticketmaster_client import TicketmasterClient

# --- System Prompt ---
SYSTEM_PROMPT = """You are TravelGenie, an expert AI travel concierge powered by real-time data.

Your capabilities include:
1. 🔍 **Real Flight Search**: Search actual flights from hundreds of airlines via Duffel
2. 🏨 **Real Hotel Search**: Find real hotels via Booking.com
3. 🌤️ **Live Weather**: Get real weather forecasts from OpenWeatherMap
4. 🎯 **Real Attractions**: Find genuine tourist attractions via Google Places
5. 🎭 **Live Events**: Discover real concerts, sports, and festivals
6. 📅 **Itinerary Creation**: Build personalized itineraries using all real data

Guidelines:
- Always ask for dates in YYYY-MM-DD format when not provided
- For flights, use 3-letter IATA airport codes (JFK, LAX, CDG, etc.)
- Mention that bookings need to be completed on actual websites
- Use weather data to make packing and activity recommendations

Remember: You're providing REAL, LIVE data. All suggestions are actual places and events!"""

# --- Initialize API Clients (Lazy Loading) ---
_clients = {}

def get_duffel_client() -> Optional[DuffelClient]:
    if "duffel" not in _clients:
        try:
            _clients["duffel"] = DuffelClient()
        except ValueError:
            _clients["duffel"] = None
    return _clients["duffel"]

def get_booking_client() -> Optional[BookingClient]:
    if "booking" not in _clients:
        try:
            _clients["booking"] = BookingClient()
        except ValueError:
            _clients["booking"] = None
    return _clients["booking"]

def get_weather_client() -> Optional[WeatherClient]:
    if "weather" not in _clients:
        try:
            _clients["weather"] = WeatherClient()
        except ValueError:
            _clients["weather"] = None
    return _clients["weather"]

def get_places_client() -> Optional[PlacesClient]:
    if "places" not in _clients:
        try:
            _clients["places"] = PlacesClient()
        except ValueError:
            _clients["places"] = None
    return _clients["places"]

def get_events_client() -> Optional[EventsClient]:
    """Get or create Events client."""
    if "events" not in _clients:
        try:
            _clients["events"] = EventsClient()
        except ValueError:
            _clients["events"] = None
    return _clients["events"]

def get_ticketmaster_client() -> Optional[TicketmasterClient]:
    """Get or create Ticketmaster client."""
    if "ticketmaster" not in _clients:
        try:
            _clients["ticketmaster"] = TicketmasterClient()
        except ValueError:
            _clients["ticketmaster"] = None
    return _clients["ticketmaster"]


# --- Define Tools with Real APIs ---

@tool
def search_flights(origin: str, destination: str, departure_date: str, passengers: int = 1, return_date: str = None) -> str:
    """Search for REAL available flights using Duffel API."""
    print(f"✈️ Searching REAL flights: {origin} → {destination}")
    
    client = get_duffel_client()
    if not client:
        return json.dumps({"error": "Duffel API not configured. Set DUFFEL_API_KEY."})
    
    origin_code = normalize_airport_code(origin)
    dest_code = normalize_airport_code(destination)
    
    result = client.search_flights(origin=origin_code, destination=dest_code, departure_date=departure_date, return_date=return_date, adults=passengers)
    return json.dumps(result, indent=2)


@tool
def search_hotels(location: str, checkin_date: str, checkout_date: str, guests: int = 2) -> str:
    """Search for REAL hotels using Booking.com API with Google Places fallback."""
    print(f"🏨 Searching REAL hotels in {location}")
    
    client = get_booking_client()
    if client:
        result = client.search_hotels(location_name=location, check_in_date=checkin_date, check_out_date=checkout_date, adults=guests)
        if "error" not in result:
            return json.dumps(result, indent=2)
    
    places_client = get_places_client()
    if places_client:
        return json.dumps(places_client.get_hotels(location), indent=2)
    
    return json.dumps({"error": "No hotel API configured."})


@tool
def get_weather(location: str, start_date: str = None, end_date: str = None) -> str:
    """Get REAL weather data from OpenWeatherMap API."""
    print(f"🌤️ Getting REAL weather for {location}")
    
    client = get_weather_client()
    if not client:
        return json.dumps({"error": "OpenWeatherMap API not configured."})
    
    if start_date and end_date:
        result = client.get_weather_for_trip(location, start_date, end_date)
    else:
        current = client.get_current_weather(location)
        forecast = client.get_forecast(location)
        if "error" in current:
            return json.dumps(current)
        result = {**current, "forecast": forecast.get("forecast", [])}
    
    return json.dumps(result, indent=2)


@tool
def get_attractions(location: str) -> str:
    """Get REAL tourist attractions from Google Places API."""
    print(f"🎯 Getting REAL attractions in {location}")
    
    client = get_places_client()
    if not client:
        return json.dumps({"error": "Google Places API not configured."})
    
    return json.dumps(client.get_attractions(location), indent=2)


@tool
def get_restaurants(location: str, cuisine: str = None) -> str:
    """Get REAL restaurant recommendations from Google Places API."""
    print(f"🍽️ Getting REAL restaurants in {location}")
    
    client = get_places_client()
    if not client:
        return json.dumps({"error": "Google Places API not configured."})
    
    return json.dumps(client.get_restaurants(location, cuisine), indent=2)


@tool
def get_events(location: str, event_type: str = None, date_range: str = "week") -> str:
    """Get REAL events happening in a location via SerpAPI."""
    print(f"🎭 Getting REAL events in {location}")
    
    client = get_events_client()
    if client:
        result = client.get_events(location, query=event_type, date_filter=date_range)
        if "error" not in result or result.get("events"):
            return json.dumps(result, indent=2)

    # Fallback to Ticketmaster
    tm_client = get_ticketmaster_client()
    if tm_client:
        city = location.split(",")[0].strip()
        result = tm_client.search_events(city=city, keyword=event_type)
        if "error" not in result:
            return json.dumps(result, indent=2)
            
    return json.dumps({"error": "No events API configured."})


@tool
def create_itinerary(destination: str, start_date: str, end_date: str, interests: str = "general") -> str:
    """Create a personalized itinerary using REAL data from all APIs."""
    print(f"📅 Creating REAL itinerary for {destination}")
    
    itinerary_data = {"destination": destination, "dates": f"{start_date} to {end_date}", "interests": interests}
    
    weather_client = get_weather_client()
    if weather_client:
        weather = weather_client.get_weather_for_trip(destination, start_date, end_date)
        if "error" not in weather:
            itinerary_data["weather"] = {"summary": weather.get("current_weather", {}).get("description", ""), "packing_tips": weather.get("packing_suggestions", [])}
    
    places_client = get_places_client()
    if places_client:
        attractions = places_client.get_attractions(destination)
        if "error" not in attractions:
            itinerary_data["top_attractions"] = attractions.get("attractions", [])[:8]
        restaurants = places_client.get_restaurants(destination)
        if "error" not in restaurants:
            itinerary_data["recommended_restaurants"] = restaurants.get("restaurants", [])[:5]
    
    events_client = get_events_client()
    if events_client:
        events = events_client.get_events(destination, date_filter="month")
        if "error" not in events:
            itinerary_data["upcoming_events"] = events.get("events", [])[:5]
    
    itinerary_data["note"] = "This itinerary uses REAL data. All attractions and events listed are actual!"
    return json.dumps(itinerary_data, indent=2)


# --- Setup ---
tools = [search_flights, search_hotels, get_weather, get_attractions, get_restaurants, get_events, create_itinerary]
tools_map = {t.name: t for t in tools}

model = ChatVertexAI(model_name="gemini-2.0-flash", temperature=0.3, max_output_tokens=4096)
model_with_tools = model.bind_tools(tools)


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return "end"
    return "continue"


def call_model(state: AgentState) -> dict:
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    return {"messages": [model_with_tools.invoke(messages)]}


def call_tools(state: AgentState) -> dict:
    last_message = state["messages"][-1]
    results = []
    for tc in last_message.tool_calls:
        try:
            result = tools_map[tc["name"]].invoke(tc["args"]) if tc["name"] in tools_map else '{"error": "Tool not found"}'
        except Exception as e:
            result = json.dumps({"error": str(e)})
        results.append(ToolMessage(tool_call_id=tc["id"], content=str(result)))
    return {"messages": results}


# --- Build Graph ---
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", call_tools)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
workflow.add_edge("tools", "agent")
app = workflow.compile()

if __name__ == "__main__":
    print("🧞 TravelGenie LIVE Agent ready!")
    print(f"Tools: {list(tools_map.keys())}")
EOF
```

---

## Section 5: Building the User Interface

### 5.1 Create the Streamlit App

```bash
cat > app.py << 'EOF'
"""TravelGenie Live - AI Travel Concierge with Real APIs"""

import streamlit as st
import os
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from agent import app as agent_app, SYSTEM_PROMPT

st.set_page_config(page_title="TravelGenie Live ✈️", page_icon="✈️", layout="wide")

# Custom CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    h1 {
        background: linear-gradient(135deg, #10b981, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    
    .subtitle { text-align: center; color: #94a3b8; margin-bottom: 0.5rem; }
    
    .live-badge {
        display: block;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-align: center;
        width: fit-content;
        margin: 0 auto 1.5rem;
    }
    
    .api-status { padding: 0.5rem; border-radius: 8px; margin-bottom: 0.5rem; font-size: 0.85rem; }
    .api-ok { background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: #10b981; }
    .api-error { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); color: #ef4444; }
    
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        color: white;
        border: none;
        border-radius: 12px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("# ✈️ TravelGenie Live")
st.markdown('<p class="subtitle">AI Travel Concierge with Real-Time Data</p>', unsafe_allow_html=True)
st.markdown('<div class="live-badge">🟢 LIVE DATA</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🔌 API Status")
    
    api_status = {
        "Duffel (Flights)": bool(os.getenv("DUFFEL_API_KEY")),
        "Booking.com (Hotels)": bool(os.getenv("RAPIDAPI_KEY")),
        "OpenWeatherMap": bool(os.getenv("OPENWEATHERMAP_API_KEY")),
        "Google Places": bool(os.getenv("GOOGLE_PLACES_API_KEY")),
        "SerpAPI (Events)": bool(os.getenv("SERPAPI_API_KEY")),
        "Ticketmaster": bool(os.getenv("TICKETMASTER_API_KEY"))
    }
    
    for api, is_configured in api_status.items():
        status_class = "api-ok" if is_configured else "api-error"
        icon = "✅" if is_configured else "❌"
        st.markdown(f'<div class="api-status {status_class}">{icon} {api}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## 💡 Try These")
    
    examples = [
        "Find flights from NYC to Paris for 2026-01-20",
        "What's the real weather in Tokyo?",
        "Show me attractions in Barcelona",
        "What events are happening in London?",
    ]
    
    for ex in examples:
        if st.button(f"📌 {ex[:32]}...", key=ex):
            st.session_state.suggested_prompt = ex
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Initialize state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage) and msg.content:
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# Handle suggested prompts
if "suggested_prompt" in st.session_state:
    prompt = st.session_state.suggested_prompt
    del st.session_state.suggested_prompt
    st.session_state.pending = prompt
    st.rerun()

# Chat input
user_input = st.chat_input("Ask about real flights, hotels, weather, or events! 🌍")

if "pending" in st.session_state:
    user_input = st.session_state.pending
    del st.session_state.pending

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    
    st.session_state.messages.append(HumanMessage(content=user_input))
    
    with st.chat_message("assistant"):
        with st.spinner("🔍 Fetching REAL data..."):
            try:
                conversation = [SystemMessage(content=SYSTEM_PROMPT)] + list(st.session_state.messages)
                result = agent_app.invoke({"messages": conversation})
                
                new_messages = [m for m in result["messages"] if not isinstance(m, SystemMessage)]
                st.session_state.messages = new_messages
                
                final = result["messages"][-1]
                if isinstance(final, AIMessage) and final.content:
                    st.markdown(final.content)
                else:
                    st.markdown("Request processed. What else?")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.markdown('<p style="text-align:center;color:#64748b;">Powered by Gemini AI, Duffel, Booking.com, OpenWeatherMap, Google Places & SerpAPI</p>', unsafe_allow_html=True)
EOF
```

### 5.2 Create Requirements File

```bash
cat > requirements.txt << 'EOF'
streamlit>=1.32.0
langchain>=0.2.0
langchain-core>=0.2.0
langchain-google-vertexai>=1.0.0
langgraph>=0.1.0
google-cloud-aiplatform>=1.50.0
requests>=2.31.0
python-dotenv>=1.0.0
EOF
```

---

## Section 6: Containerization

### 6.1 Create Dockerfile

```bash
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ca-certificates && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.headless=true"]
EOF
```

### 6.2 Create Docker Ignore File

```bash
cat > .dockerignore << 'EOF'
.env
__pycache__/
*.py[cod]
.git
README.md
EOF
```

---

## Section 7: Local Testing

### 7.1 Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 7.2 Configure API Keys

```bash
# Edit .env with your actual API keys
nano .env
```

### 7.3 Run the Application

```bash
# Load environment variables
export $(cat .env | xargs)

# Run Streamlit
streamlit run app.py
```

Open http://localhost:8501 in your browser!

---

## Section 8: Deploy to Cloud Run

### 8.1 Store API Keys in Secret Manager

> **⚠️ Important:** Replace the placeholder values below with your **actual API keys** before running these commands!

```bash
# Create secrets for each API key (replace <YOUR_KEY> with actual values!)
echo -n "<YOUR_DUFFEL_API_KEY>" | gcloud secrets create duffel-api-key --data-file=-
echo -n "<YOUR_RAPIDAPI_KEY>" | gcloud secrets create rapidapi-key --data-file=-
echo -n "<YOUR_OPENWEATHER_KEY>" | gcloud secrets create openweather-api-key --data-file=-
echo -n "<YOUR_GOOGLE_PLACES_KEY>" | gcloud secrets create google-places-api-key --data-file=-
echo -n "<YOUR_SERPAPI_KEY>" | gcloud secrets create serpapi-api-key --data-file=-
echo -n "<TICKETMASTER_API_KEY>" | gcloud secrets create ticketmaster-api-key --data-file=-
echo -n "<TICKETMASTER_API_SECRET>" | gcloud secrets create ticketmaster-api-secret --data-file=-

```

**If you already created secrets with wrong values, update them:**
```bash
echo -n "<YOUR_ACTUAL_KEY>" | gcloud secrets versions add <secret-name> --data-file=-
```

### 8.2 Grant Secret Access to Cloud Run

**Important:** Cloud Run needs permission to access your secrets. Run this command:

```bash
# Get your project number
export PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')

# Grant Secret Manager access to the Cloud Run service account
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

echo "✅ Secret access granted!"
```

> **Note:** Without this step, deployment will fail with "Permission denied on secret" error.

### 8.3 Build the Container

```bash
export PROJECT_ID=$(gcloud config get-value project)
export REGION="us-central1"
export IMAGE_NAME="gcr.io/${PROJECT_ID}/travel-genie-live:v1"

gcloud builds submit --tag $IMAGE_NAME

echo "✅ Container built successfully!"
```

### 8.4 Deploy to Cloud Run

```bash
gcloud run deploy travel-genie-live \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 1Gi \
  --timeout 300 \
  --set-secrets "DUFFEL_API_KEY=duffel-api-key:latest,RAPIDAPI_KEY=rapidapi-key:latest,OPENWEATHERMAP_API_KEY=openweather-api-key:latest,GOOGLE_PLACES_API_KEY=google-places-api-key:latest,SERPAPI_API_KEY=serpapi-api-key:latest,TICKETMASTER_API_KEY=ticketmaster-api-key:latest,  TICKETMASTER_API_SECRET=ticketmaster-api-secret:latest"

echo "🚀 Deployment complete!"
```

---
## Section 9: Test Your Live App!

Once deployed, try these conversations:

### Flight Search
> "Find me flights from New York to Paris for January 20th, 2026"

### Real Weather
> "What's the weather like in Tokyo right now?"

### Live Attractions
> "Show me the top attractions in Barcelona"

### Real Events
> "What concerts are happening in London this week?"

### Full Itinerary
> "Create an itinerary for Rome from January 15-20 with focus on history and food"

---

## Section 10: Cleanup

```bash
# Delete Cloud Run service
gcloud run services delete travel-genie-live --region=$REGION --quiet

# Delete container image
gcloud container images delete $IMAGE_NAME --quiet

# Delete secrets
gcloud secrets delete duffel-api-key --quiet
gcloud secrets delete rapidapi-key --quiet
gcloud secrets delete openweather-api-key --quiet
gcloud secrets delete google-places-api-key --quiet
gcloud secrets delete serpapi-api-key --quiet

echo "✅ Cleanup complete!"
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **API key errors** | Check .env file has correct keys without quotes |
| **No flights found** | Use 3-letter airport codes (JFK, CDG, LHR) |
| **Rate limit errors** | Free tiers have limits; wait or upgrade |
| **Timeout errors** | Increase Cloud Run timeout to 300s |
| **Import errors** | Ensure `apis/` folder exists with `__init__.py` |

---

## 📚 API Documentation

- [Duffel Docs](https://duffel.com/docs/api)
- [Booking.com API (RapidAPI)](https://rapidapi.com/apidojo/api/booking-com/)
- [OpenWeatherMap Docs](https://openweathermap.org/api)
- [Google Places Docs](https://developers.google.com/maps/documentation/places)
- [SerpAPI Docs](https://serpapi.com/google-events-api)
- [Ticketmaster API](https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/)

---

**Happy Travels with REAL Data! 🧞✈️**
