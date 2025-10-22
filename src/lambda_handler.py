"""AWS Lambda handler for serverless deployment."""

import json
import asyncio
import logging
from src.main import app
from src.models.schemas import MaritimeSafetyQuery

logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    """
    AWS Lambda handler for the FastAPI application.
    
    Converts Lambda events to HTTP requests and processes them through FastAPI.
    
    Args:
        event: Lambda event (API Gateway proxy format)
        context: Lambda context
        
    Returns:
        HTTP response in Lambda proxy format
    """
    try:
        # Parse the incoming request
        http_method = event.get("httpMethod", "GET")
        path = event.get("path", "/")
        body = event.get("body", "")
        headers = event.get("headers", {})
        query_params = event.get("queryStringParameters", {})
        
        logger.info(f"Lambda handler: {http_method} {path}")
        
        # Route to appropriate handler
        if path == "/health":
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "healthy"}),
                "headers": {"Content-Type": "application/json"}
            }
        
        elif path == "/query" and http_method == "POST":
            # Parse the query from body
            query_data = json.loads(body) if body else {}
            query = MaritimeSafetyQuery(**query_data)
            
            # Run async function in event loop
            response = asyncio.run(app.router.dependant.call(query))
            
            return {
                "statusCode": 200,
                "body": json.dumps(response.model_dump(), default=str),
                "headers": {"Content-Type": "application/json"}
            }
        
        elif path == "/query/location" and http_method == "POST":
            # Handle location-specific query
            query_data = json.loads(body) if body else {}
            response = asyncio.run(
                app.router.dependant.call(
                    query=query_data.get("query"),
                    latitude=query_data.get("latitude"),
                    longitude=query_data.get("longitude"),
                    location_name=query_data.get("location_name")
                )
            )
            
            return {
                "statusCode": 200,
                "body": json.dumps(response.model_dump(), default=str),
                "headers": {"Content-Type": "application/json"}
            }
        
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Not found"}),
                "headers": {"Content-Type": "application/json"}
            }
    
    except Exception as e:
        logger.error(f"Lambda handler error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {"Content-Type": "application/json"}
        }
