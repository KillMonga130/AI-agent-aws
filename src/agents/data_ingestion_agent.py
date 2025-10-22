"""Data Ingestion Agent - fetches and normalizes ocean + weather data."""

import logging
from datetime import datetime
from src.models.schemas import LocationData, IngestionResult
from src.services.data_fetcher import DataFetcher
from src.services.aws_services import s3_client

logger = logging.getLogger(__name__)


class DataIngestionAgent:
    """Agent responsible for fetching and normalizing marine data."""
    
    def __init__(self):
        """Initialize the data ingestion agent."""
        self.name = "DataIngestionAgent"
    
    async def execute(self, location: LocationData) -> IngestionResult:
        """
        Execute data ingestion for a location.
        
        Args:
            location: Location to fetch data for
            
        Returns:
            IngestionResult with fetched data
        """
        logger.info(f"{self.name} executing for location: {location}")
        
        try:
            # Fetch weather and ocean data concurrently
            weather_data, ocean_data = await DataFetcher.fetch_all_data(location)
            
            result = IngestionResult(
                location=location,
                weather_data=weather_data,
                ocean_data=ocean_data,
                timestamp=datetime.utcnow()
            )
            
            # Store to S3 for audit trail
            s3_key = f"raw/{location.latitude}_{location.longitude}/{datetime.utcnow().isoformat()}.json"
            s3_client.put_object(
                key=s3_key,
                data=result.model_dump()
            )
            
            logger.info(f"{self.name} completed successfully for {location.name or location}")
            return result
            
        except Exception as e:
            logger.error(f"{self.name} failed: {e}")
            return IngestionResult(
                location=location,
                error=str(e),
                timestamp=datetime.utcnow()
            )
    
    def get_tool_definitions(self) -> list:
        """
        Return tool definitions for agent orchestration.
        Tools that this agent provides to the supervisor.
        """
        return [
            {
                "name": "fetch_marine_data",
                "description": "Fetch current ocean physics and weather data for a location",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "latitude": {
                            "type": "number",
                            "description": "Location latitude"
                        },
                        "longitude": {
                            "type": "number",
                            "description": "Location longitude"
                        },
                        "location_name": {
                            "type": "string",
                            "description": "Optional location name (e.g., Cape Town)"
                        }
                    },
                    "required": ["latitude", "longitude"]
                }
            }
        ]
