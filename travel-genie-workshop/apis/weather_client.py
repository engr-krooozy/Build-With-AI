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
