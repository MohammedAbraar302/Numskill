FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install build deps and clean up
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application
COPY . /app

# Let the host/platform set the PORT env var; default to 8080 for local runs
ENV PORT 8080
EXPOSE 8080

# Use a shell form so $PORT is expanded at runtime
CMD ["sh", "-c", "gunicorn wsgi:app -b 0.0.0.0:$PORT --workers 1 --threads 4"]
