"""AWS Lambda handler for serverless deployment."""

import logging
from mangum import Mangum
from src.main import app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Mangum handler - this adapts FastAPI to AWS Lambda
handler = Mangum(app, lifespan="off")


def lambda_handler(event, context):
    """
    AWS Lambda handler for the FastAPI application.
    
    Uses Mangum to convert Lambda events to ASGI requests.
    
    Args:
        event: Lambda event (API Gateway proxy format)
        context: Lambda context
        
    Returns:
        HTTP response in Lambda proxy format
    """
    logger.info(f"Received event: {event.get('httpMethod')} {event.get('path')}")
    return handler(event, context)
