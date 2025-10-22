"""Main FastAPI application for the Ocean Forecasting Agent."""

import logging
import logging.config
from contextlib import asynccontextmanager
from datetime import datetime
from json import JSONEncoder
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.models.schemas import MaritimeSafetyQuery, AgentResponse, LocationData
from src.agents.supervisor_agent import SupervisorAgent

# Configure logging
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr"
        }
    },
    "root": {
        "level": settings.log_level,
        "handlers": ["default"]
    }
}

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)


# Global supervisor agent instance
supervisor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global supervisor
    
    logger.info("Starting Autonomous Ocean Forecasting Agent")
    supervisor = SupervisorAgent()
    logger.info(f"Supervisor agent initialized: {supervisor.name}")
    
    yield
    
    logger.info("Shutting down Autonomous Ocean Forecasting Agent")


# Custom JSON encoder for datetime
class DateTimeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


# Create FastAPI application with custom JSON encoder
app = FastAPI(
    title="Autonomous Ocean Forecasting Agent",
    description="Multi-agent AI system for maritime safety powered by AWS Bedrock",
    version="0.1.0",
    lifespan=lifespan,
    json_encoder=DateTimeEncoder
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# API Routes
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Autonomous Ocean Forecasting Agent",
        "version": "0.1.0"
    }


@app.get("/info")
async def agent_info():
    """Get information about the agent system."""
    if supervisor is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return {
        "agent": supervisor.get_agent_info(),
        "config": {
            "bedrock_model": settings.bedrock_model_id,
            "bedrock_region": settings.bedrock_region,
            "s3_bucket": settings.s3_bucket_name
        }
    }


@app.post("/query", response_model=AgentResponse)
async def maritime_safety_query(query: MaritimeSafetyQuery):
    """
    Submit a maritime safety query to the agent.
    
    The agent will:
    1. Extract location information
    2. Fetch current ocean and weather data
    3. Analyze maritime risks using LLM reasoning
    4. Generate actionable safety alerts
    
    Args:
        query: MaritimeSafetyQuery containing the natural language query
        
    Returns:
        AgentResponse with alert and analysis
    """
    if supervisor is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    logger.info(f"Received query: {query.query}")
    
    try:
        response = await supervisor.process_query(query)
        logger.info(f"Query processed successfully in {response.execution_time_seconds:.2f}s")
        return response
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.post("/query/location", response_model=AgentResponse)
async def maritime_safety_query_with_location(
    query: str,
    latitude: float,
    longitude: float,
    location_name: str = None
):
    """
    Submit a maritime safety query with explicit location.
    
    Args:
        query: Natural language query
        latitude: Location latitude
        longitude: Location longitude
        location_name: Optional location name
        
    Returns:
        AgentResponse with alert and analysis
    """
    if supervisor is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    location = LocationData(
        latitude=latitude,
        longitude=longitude,
        name=location_name or f"({latitude}, {longitude})"
    )
    
    maritime_query = MaritimeSafetyQuery(
        query=query,
        location=location
    )
    
    try:
        response = await supervisor.process_query(maritime_query)
        return response
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/docs", include_in_schema=False)
async def get_docs():
    """Redirect to API documentation."""
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Autonomous Ocean Forecasting Agent API"
    )


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower()
    )
