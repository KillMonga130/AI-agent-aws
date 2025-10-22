import json
import os
import time
import logging
from datetime import datetime, timezone
from urllib.parse import urlencode

import boto3
import requests
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(message)s"))
if not logger.handlers:
    logger.addHandler(handler)

s3 = boto3.client("s3")
secrets = boto3.client("secretsmanager")

OPEN_METEO_MARINE = "https://marine-api.open-meteo.com/v1/marine"


def _get_copernicus_creds(secret_name: str):
    if not secret_name:
        return None
    try:
        r = secrets.get_secret_value(SecretId=secret_name)
        return json.loads(r.get("SecretString", "{}"))
    except secrets.exceptions.ResourceNotFoundException:
        logger.info({"msg": "copernicus secret not found", "secret": secret_name})
        return None
    except Exception as e:
        logger.warning({"msg": "copernicus secret error", "error": str(e)})
        return None


def _fetch_open_meteo(lat: float, lon: float):
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join([
            "wave_height",
            "wave_direction",
            "wave_period",
            "wind_speed",
            "wind_direction",
            "visibility",
            "surface_temperature",
        ]),
        "timezone": "UTC",
    }
    url = f"{OPEN_METEO_MARINE}?{urlencode(params)}"
    t0 = time.time()
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    logger.info({"msg": "open-meteo fetched", "ms": int((time.time()-t0)*1000)})
    return data


def _store_to_s3(bucket: str, lat: float, lon: float, payload: dict) -> str:
    now = datetime.now(timezone.utc).isoformat()
    key = f"raw/{lat:.4f}_{lon:.4f}/{now}.json"
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(payload).encode("utf-8"),
        ContentType="application/json",
        ServerSideEncryption="AES256",
    )
    return key


def lambda_handler(event, context):
    """Ingest ocean + weather data and store in S3.

    Event JSON (either body string or dict):
    {
      "latitude": -33.9249,
      "longitude": 18.4241,
      "forecast_hours": 48
    }
    """
    try:
        body = event.get("body", event) if isinstance(event, dict) else event
        if isinstance(body, str):
            body = json.loads(body or "{}")
        lat = float(body.get("latitude"))
        lon = float(body.get("longitude"))
        forecast_hours = int(body.get("forecast_hours", 48))
    except Exception as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"invalid input: {str(e)}"}),
        }

    bucket = os.environ["DATA_BUCKET"]
    secret_name = os.getenv("COPERNICUS_SECRET_NAME", "")

    open_meteo = None
    copernicus_status = "not_configured"

    try:
        open_meteo = _fetch_open_meteo(lat, lon)
    except Exception as e:
        logger.error({"msg": "open-meteo error", "error": str(e)})

    # Optional Copernicus: placeholder wiring, fetch via external client if configured
    creds = _get_copernicus_creds(secret_name)
    if creds and creds.get("username") and creds.get("password"):
        copernicus_status = "configured"
        # Place to add real copernicus integration
        # For now, record config presence; you can extend to fetch gridded datasets

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "location": {"latitude": lat, "longitude": lon},
        "forecast_hours": forecast_hours,
        "sources": {
            "open_meteo": open_meteo,
            "copernicus": {"status": copernicus_status},
        },
    }

    key = _store_to_s3(bucket, lat, lon, payload)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "bucket": bucket,
            "key": key,
            "copernicus": copernicus_status,
        }),
    }
