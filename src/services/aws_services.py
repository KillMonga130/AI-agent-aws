"""AWS Bedrock and related services integration."""

import boto3
import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime
from botocore.exceptions import ClientError
from src.config import settings

logger = logging.getLogger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class BedrockClient:
    """Client for AWS Bedrock LLM operations."""
    
    def __init__(self):
        """Initialize Bedrock client."""
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.bedrock_region
        )
        self.model_id = settings.bedrock_model_id
    
    def invoke_model(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Invoke the LLM model with a prompt.
        
        Args:
            prompt: User prompt/query
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation (0.0-1.0)
            system_prompt: Optional system prompt for context
            
        Returns:
            Model response text
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "user",
                    "content": system_prompt + "\n\n" + prompt
                })
            else:
                messages.append({
                    "role": "user",
                    "content": prompt
                })
            
            body = {
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            logger.debug(f"Invoking Bedrock model {self.model_id}")
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response["body"].read())
            
            if "content" in response_body:
                content = response_body["content"]
                if isinstance(content, list) and len(content) > 0:
                    return content[0].get("text", "")
            
            logger.warning("Unexpected response structure from Bedrock")
            return str(response_body)
            
        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error invoking Bedrock: {e}")
            raise
    
    def analyze_with_reasoning(
        self,
        context: str,
        analysis_prompt: str,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Perform reasoning-based analysis using the LLM.
        
        Args:
            context: Background context/data for analysis
            analysis_prompt: Specific analysis question
            max_tokens: Maximum response tokens
            
        Returns:
            Analysis result as dictionary
        """
        full_prompt = f"""
{context}

Please analyze the above information and respond to this query:
{analysis_prompt}

Provide:
1. Your assessment
2. Key factors considered
3. Confidence level (0-100)
4. Specific recommendations
"""
        
        response_text = self.invoke_model(
            prompt=full_prompt,
            max_tokens=max_tokens,
            temperature=0.3
        )
        
        return {
            "analysis": response_text,
            "raw_response": response_text
        }


class S3Client:
    """Client for AWS S3 storage operations."""
    
    def __init__(self):
        """Initialize S3 client."""
        self.client = boto3.client("s3", region_name=settings.s3_region)
        self.bucket_name = settings.s3_bucket_name
    
    def put_object(self, key: str, data: Dict[str, Any]) -> bool:
        """
        Store data in S3.
        
        Args:
            key: S3 object key
            data: Data dictionary to store
            
        Returns:
            Success boolean
        """
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(data, cls=DateTimeEncoder),
                ContentType="application/json"
            )
            logger.info(f"Stored data to S3: {key}")
            return True
        except ClientError as e:
            logger.error(f"Error storing to S3: {e}")
            return False
    
    def get_object(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve data from S3.
        
        Args:
            key: S3 object key
            
        Returns:
            Data dictionary or None if not found
        """
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=key)
            data = json.loads(response["Body"].read().decode("utf-8"))
            return data
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logger.warning(f"Object not found in S3: {key}")
                return None
            logger.error(f"Error retrieving from S3: {e}")
            return None
    
    def list_objects(self, prefix: str) -> list:
        """
        List objects in S3 with given prefix.
        
        Args:
            prefix: S3 key prefix
            
        Returns:
            List of object keys
        """
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            return [obj["Key"] for obj in response.get("Contents", [])]
        except ClientError as e:
            logger.error(f"Error listing S3 objects: {e}")
            return []


# Global clients
bedrock_client = BedrockClient()
s3_client = S3Client()
