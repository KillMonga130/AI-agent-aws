"""Data fetching from external APIs."""

import httpx
import logging
from typing import Optional, Tuple
from datetime import datetime
import math

from src.models.schemas import WeatherData, OceanData, LocationData

logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetch ocean and weather data from external APIs."""
    
    COPERNICUS_BASE_URL = "https://my.cmems-du.eu/thredds/wms"
    METEO_BASE_URL = "https://api.open-meteo.com/v1/marine"
    
    @staticmethod
    async def fetch_open_meteo_data(
        latitude: float,
        longitude: float,
        forecast_days: int = 5
    ) -> Optional[WeatherData]:
        """
        Fetch marine weather data from Open-Meteo API (free, no auth required).
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            forecast_days: Number of forecast days (max 7)
            
        Returns:
            WeatherData object or None if failed
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "wave_height,wave_direction,wave_period,wind_speed,wind_direction,visibility",
                    "forecast_days": min(forecast_days, 7),
                    "timezone": "UTC"
                }
                
                logger.info(f"Fetching Open-Meteo data for ({latitude}, {longitude})")
                response = await client.get(
                    DataFetcher.METEO_BASE_URL,
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                current = data.get("current", {})
                
                # Default values if data missing
                return WeatherData(
                    wave_height=current.get("wave_height", 0.5),
                    wave_direction=current.get("wave_direction", 180.0),
                    wave_period=current.get("wave_period", 5.0),
                    wind_speed=current.get("wind_speed", 10.0),
                    wind_direction=current.get("wind_direction", 270.0),
                    visibility=current.get("visibility", 10.0),
                    timestamp=datetime.utcnow()
                )
                
        except Exception as e:
            logger.error(f"Error fetching Open-Meteo data: {e}")
            return None
    
    @staticmethod
    async def fetch_copernicus_mock_data(
        latitude: float,
        longitude: float
    ) -> Optional[OceanData]:
        """
        Fetch ocean physics data from Copernicus Marine Service.
        Note: Returns mock data for demo (requires credentials for real API).
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            OceanData object or mock data
        """
        try:
            logger.info(f"Fetching Copernicus data for ({latitude}, {longitude})")
            
            # In production, would use real Copernicus API with credentials
            # For now, return realistic mock data based on location
            
            # Simulate regional variation
            import random
            random.seed(int(latitude * longitude * 100))  # Deterministic based on location
            
            return OceanData(
                sea_surface_height=random.uniform(-0.5, 0.5),
                current_velocity_u=random.uniform(-0.5, 0.5),
                current_velocity_v=random.uniform(-0.5, 0.5),
                sea_surface_temperature=random.uniform(15.0, 26.0),
                salinity=random.uniform(33.0, 35.0),
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error fetching Copernicus data: {e}")
            return None
    
    @staticmethod
    async def fetch_all_data(
        location: LocationData
    ) -> Tuple[Optional[WeatherData], Optional[OceanData]]:
        """
        Concurrently fetch all available data for a location.
        
        Args:
            location: Location information
            
        Returns:
            Tuple of (WeatherData, OceanData), either or both may be None
        """
        import asyncio
        
        weather_task = DataFetcher.fetch_open_meteo_data(
            location.latitude,
            location.longitude
        )
        ocean_task = DataFetcher.fetch_copernicus_mock_data(
            location.latitude,
            location.longitude
        )
        
        weather_data, ocean_data = await asyncio.gather(
            weather_task,
            ocean_task,
            return_exceptions=False
        )
        
        return weather_data, ocean_data
