"""
AWS Lambda Function: Ocean Data Ingestion Agent
Fetches real-time ocean conditions from Copernicus Marine and Open-Meteo APIs
Stores processed data in Amazon S3 for agent analysis
"""

import json
import boto3
import requests
from datetime import datetime, timedelta
from typing import Dict, Any

# Initialize AWS clients
s3_client = boto3.client('s3')
BUCKET_NAME = 'ocean-forecast-data-911167913661'

def fetch_ocean_data(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetch ocean conditions from Copernicus Marine Service
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
    
    Returns:
        Dictionary containing ocean data (currents, sea surface height, temperature)
    """
    try:
        # Note: In production, use copernicusmarine library with authentication
        # For hackathon demo, we'll use simulated data structure
        # Real implementation:
        # import copernicusmarine
        # dataset = copernicusmarine.open_dataset(
        #     dataset_id="cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m",
        #     variables=["sea_surface_height_above_geoid", "sea_water_velocity"],
        #     minimum_longitude=lon-0.5, maximum_longitude=lon+0.5,
        #     minimum_latitude=lat-0.5, maximum_latitude=lat+0.5,
        #     start_datetime=datetime.now() - timedelta(days=1),
        #     end_datetime=datetime.now()
        # )
        
        # Simulated ocean data for demo (replace with real API call)
        ocean_data = {
            'sea_surface_height': 0.15,  # meters
            'sea_surface_temperature': 18.5,  # Celsius
            'ocean_current_velocity_u': 0.3,  # m/s (eastward)
            'ocean_current_velocity_v': -0.2,  # m/s (northward)
            'salinity': 35.2,  # PSU
            'data_source': 'Copernicus Marine Service',
            'timestamp': datetime.now().isoformat()
        }
        
        return ocean_data
        
    except Exception as e:
        print(f"Error fetching ocean data: {str(e)}")
        return {'error': str(e), 'data_source': 'Copernicus Marine Service'}


def fetch_marine_weather(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetch marine weather and wave data from Open-Meteo Marine API
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
    
    Returns:
        Dictionary containing marine weather forecast data
    """
    try:
        url = "https://marine-api.open-meteo.com/v1/marine"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": [
                "wave_height",
                "wave_direction",
                "wave_period",
                "wind_wave_height",
                "swell_wave_height",
                "ocean_current_velocity",
                "ocean_current_direction"
            ],
            "forecast_days": 5,
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract current conditions (first hourly data point)
        hourly = data.get('hourly', {})
        current_conditions = {
            'wave_height': hourly.get('wave_height', [0])[0],
            'wave_direction': hourly.get('wave_direction', [0])[0],
            'wave_period': hourly.get('wave_period', [0])[0],
            'wind_wave_height': hourly.get('wind_wave_height', [0])[0],
            'swell_wave_height': hourly.get('swell_wave_height', [0])[0],
            'ocean_current_velocity': hourly.get('ocean_current_velocity', [0])[0],
            'ocean_current_direction': hourly.get('ocean_current_direction', [0])[0],
            'data_source': 'Open-Meteo Marine API',
            'forecast_hours': len(hourly.get('wave_height', [])),
            'timestamp': datetime.now().isoformat()
        }
        
        # Include full forecast for analysis
        current_conditions['full_forecast'] = hourly
        
        return current_conditions
        
    except Exception as e:
        print(f"Error fetching marine weather: {str(e)}")
        return {'error': str(e), 'data_source': 'Open-Meteo Marine API'}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for data ingestion
    
    Args:
        event: Lambda event containing location coordinates
        context: Lambda context object
    
    Returns:
        Response with S3 key of stored data
    """
    try:
        # Extract location from event (default: Cape Town, South Africa)
        location = event.get('location', {'lat': -33.9249, 'lon': 18.4241})
        lat = location.get('lat', -33.9249)
        lon = location.get('lon', 18.4241)
        location_name = location.get('name', 'Cape Town Harbor')
        
        print(f"Fetching data for {location_name} (lat: {lat}, lon: {lon})")
        
        # Fetch data from both sources
        ocean_data = fetch_ocean_data(lat, lon)
        weather_data = fetch_marine_weather(lat, lon)
        
        # Combine data
        combined_data = {
            'timestamp': datetime.now().isoformat(),
            'location': {
                'name': location_name,
                'latitude': lat,
                'longitude': lon
            },
            'ocean_conditions': ocean_data,
            'marine_weather': weather_data,
            'data_quality': {
                'ocean_data_available': 'error' not in ocean_data,
                'weather_data_available': 'error' not in weather_data
            }
        }
        
        # Store in S3
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        key = f"ocean-data/{timestamp_str}_{location_name.replace(' ', '_')}.json"
        
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=json.dumps(combined_data, indent=2),
            ContentType='application/json'
        )
        
        print(f"Data stored successfully: s3://{BUCKET_NAME}/{key}")
        
        return {
            'statusCode': 200,
            'data_key': key,
            'bucket': BUCKET_NAME,
            'location': location_name,
            'timestamp': combined_data['timestamp']
        }
        
    except Exception as e:
        print(f"Lambda execution error: {str(e)}")
        return {
            'statusCode': 500,
            'error': str(e)
        }


# For local testing
if __name__ == "__main__":
    test_event = {
        'location': {
            'lat': -33.9249,
            'lon': 18.4241,
            'name': 'Cape Town Harbor'
        }
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
