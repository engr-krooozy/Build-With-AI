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
