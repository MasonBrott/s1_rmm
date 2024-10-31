from fastapi import FastAPI, Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from google.cloud import storage
from google.auth import default
import google.cloud.logging
import datetime
import logging
import os

# Environment Variables
bucket_name = os.getenv('GCP_BUCKET_NAME')
if not bucket_name:
    raise ValueError("GCP_BUCKET_NAME environment variable is required")
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable is required")

# Initialize Cloud Logging
client = google.cloud.logging.Client()
client.setup_logging()
logger = logging.getLogger(__name__)

# Cloud Run instance information
INSTANCE_ID = os.getenv('K_SERVICE', 'local')
REVISION = os.getenv('K_REVISION', 'local')
REGION = os.getenv('CLOUD_RUN_REGION', 'unknown')

# Initialize FastAPI
app = FastAPI(
    title="SentinelOne MDM/RMM Signed URL Generator",
    description="Cloud Run service for generating GCS signed URLs",
    version="1.0.0"
)

# API Key Configuration
api_key_header = APIKeyHeader(name='X-API-KEY', auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    logger.warning("Invalid API key attempt")
    raise HTTPException(
        status_code=403,
        detail="Invalid API Key"
    )

async def generate_signed_url(bucket_name: str, blob_name: str, expiration_minutes: int = 5):
    try:
        credentials, project = default()
        client = storage.Client(credentials=credentials)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=expiration_minutes),
            method="PUT",
        )
        return url
    except Exception as e:
        logger.error(f"Error generating signed URL: {str(e)}", extra={
            "bucket": bucket_name,
            "blob": blob_name,
            "error": str(e)
        })
        raise

@app.get("/get_signed_url")
async def get_signed_url(object_name: str, api_key: str = Security(get_api_key), exp_min: int = 5):
    """Generate a signed URL for uploading to GCS"""
    if not object_name:
        raise HTTPException(status_code=400, detail="object_name required")
    
    logger.info("Generating signed URL", extra={
        "object_name": object_name,
        "bucket_name": bucket_name,
        "expiration_minutes": exp_min
    })

    try:
        signed_url = await generate_signed_url(bucket_name, object_name)
        return {"signed_url": signed_url}
    except Exception as e:
        logger.error(f"Error in get_signed_url endpoint: {str(e)}", extra={
            "object_name": object_name,
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {
        "status": "healthy",
        "instance": INSTANCE_ID,
        "revision": REVISION,
        "region": REGION
    }
    
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)