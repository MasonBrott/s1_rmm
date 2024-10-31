FROM gcr.io/google-appengine/python

# Create and activate virtual environment
ENV VIRTUAL_ENV /env
RUN python -m venv $VIRTUAL_ENV
ENV PATH "$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Cloud Run will set PORT environment variable
ENV PORT 8080

# Use gunicorn as the production server
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 api-server:app -k uvicorn.workers.UvicornWorker 