# SentinelOne MDM/RMM Signed URL Generator

A Cloud Run service built with FastAPI that generates signed URLs for Google Cloud Storage uploads. This service is designed to work with SentinelOne Remote Ops scripts, providing secure, time-limited upload URLs.

## Features

- Secure API Key authentication
- Generates time-limited signed URLs for GCS uploads
- Cloud Run ready
- Comprehensive logging with Google Cloud Logging
- Health check endpoint
- Configurable URL expiration time

## Prerequisites

- Google Cloud Platform account
- Google Cloud Storage bucket
- Python 3.7+
- Docker (for local development and deployment)

## Environment Variables

The following environment variables are required:

- `GCP_BUCKET_NAME`: The name of your Google Cloud Storage bucket
- `API_KEY`: Your chosen API key for securing the endpoints
- `PORT`: (Optional) Port number for the server (defaults to 8080)

## Deployment to Cloud Run

1. Build and push the container to Google Container Registry:
   ```bash
   gcloud builds submit --tag gcr.io/[PROJECT_ID]/signed-url-generator
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy signed-url-generator \
       --image gcr.io/[PROJECT_ID]/signed-url-generator \
       --platform managed \
       --set-env-vars GCP_BUCKET_NAME="your-bucket-name",API_KEY="your-api-key"
   ```

## API Usage

### Generate Signed URL

```bash
curl -X GET "https://[YOUR-SERVICE-URL]/get_signed_url?object_name=example.txt" \
    -H "X-API-KEY: your-api-key"
```

Parameters:
- `object_name`: Name of the file to be uploaded (required)
- `exp_min`: URL expiration time in minutes (optional, defaults to 5)

### Health Check

```bash
curl -X GET "https://[YOUR-SERVICE-URL]/health"
```

## Security Considerations

- Keep your API key secure and rotate it regularly
- Use HTTPS for all API calls
- Monitor your application logs for unauthorized access attempts
- Consider implementing rate limiting for production use

## Local Development

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: .\env\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   export GCP_BUCKET_NAME="your-bucket-name"
   export API_KEY="your-api-key"
   ```

5. Run the development server:
   ```bash
   python api-server.py
   ```

## Docker Development

Build and run the Docker container locally:
```bash
docker build -t signed-url-generator .
docker run -p 8080:8080 \
    -e GCP_BUCKET_NAME="your-bucket-name" \
    -e API_KEY="your-api-key" \
    signed-url-generator
```